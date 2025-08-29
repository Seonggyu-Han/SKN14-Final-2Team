# ============================================
# 설치 (Runpod A40 / 로컬)
# ============================================
# CPU 전용
# python -m pip install -U sentence-transformers "torch>=2.2,<3.0" scikit-learn pandas numpy joblib

# GPU (CUDA 12.1, Runpod A40)
# python -m pip install -U "torch>=2.2,<3.0" torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
# python -m pip install -U sentence-transformers scikit-learn pandas numpy joblib
# ============================================

import os, time
import numpy as np
import pandas as pd
from collections import Counter

import torch
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import f1_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
import warnings
warnings.filterwarnings("ignore")

# -------------------------------
# 설정
# -------------------------------
DATA_CSV = "./dataset/perfumes_huggingface.csv"  # 경로 맞게 수정
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # 또는 "distiluse-base-multilingual-cased-v2"
THRESHOLD = 0.35
TOP_K = 3
RARE_MIN_COUNT = 10  # <= 이하면 제거 (5~30 튜닝 권장)

# -------------------------------
# 유틸
# -------------------------------
def split_labels(s: str):
    s = str(s)
    for sep in [",", "|", "/", ";"]:
        s = s.replace(sep, " ")
    return [t.strip() for t in s.split() if t.strip()]

def encode_with_auto_batch(embedder: SentenceTransformer, texts, init_bs=1024, min_bs=64):
    """
    CUDA OOM 시 배치 크기를 절반으로 줄여가며 재시도.
    GPU면 큰 배치로 빠르게, CPU면 init_bs를 작게 설정 권장.
    """
    bs = init_bs
    Xs = []
    i = 0
    n = len(texts)
    while i < n:
        j = min(i + bs, n)
        chunk = texts[i:j]
        try:
            emb = embedder.encode(chunk, batch_size=bs, convert_to_numpy=True, show_progress_bar=False)
            Xs.append(emb)
            i = j
        except RuntimeError as e:
            if "CUDA out of memory" in str(e) and bs > min_bs:
                torch.cuda.empty_cache()
                bs = max(min_bs, bs // 2)
                print(f"[WARN] CUDA OOM → batch_size 축소: {bs}")
                continue
            raise
    return np.vstack(Xs)

# -------------------------------
# 1) 데이터 로드 & 전처리
# -------------------------------
df = pd.read_csv(DATA_CSV, sep="|", engine="python", on_bad_lines="skip")
df = df[~df["description"].isna()].copy()
df["labels"] = df["fragrances"].apply(split_labels)

# 희소 라벨 제거
cnt = Counter([l for L in df["labels"] for l in L])
rare = {k for k, v in cnt.items() if v <= RARE_MIN_COUNT}
df["labels"] = df["labels"].apply(lambda L: [l for l in L if l not in rare])
df = df[df["labels"].map(len) > 0].copy()

# 타깃 인코딩
mlb = MultiLabelBinarizer()
Y = mlb.fit_transform(df["labels"])

# -------------------------------
# 2) 데이터 분할 (다중라벨 → stratify 사용 X)
# -------------------------------
X_train_text, X_val_text, y_train, y_val = train_test_split(
    df["description"].tolist(), Y, test_size=0.2, random_state=42
)

# -------------------------------
# 3) 디바이스 & 임베더
# -------------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[Device] {device} | Torch CUDA available: {torch.cuda.is_available()}")

embedder = SentenceTransformer(MODEL_NAME, device=device)

# GPU면 큰 배치, CPU면 작은 배치
init_bs = 1024 if device == "cuda" else 128

# -------------------------------
# 4) 임베딩 (자동 배치 조절 + 벤치마킹)
# -------------------------------
t0 = time.perf_counter()
X_train = encode_with_auto_batch(embedder, X_train_text, init_bs=init_bs, min_bs=64)
t1 = time.perf_counter()
print(f"[Embed] train: {X_train.shape} | time: {t1 - t0:.2f}s | thru: {len(X_train_text)/(t1-t0+1e-9):.1f}/s")

t0 = time.perf_counter()
X_val = encode_with_auto_batch(embedder, X_val_text, init_bs=init_bs, min_bs=64)
t1 = time.perf_counter()
print(f"[Embed] valid: {X_val.shape} | time: {t1 - t0:.2f}s | thru: {len(X_val_text)/(t1-t0+1e-9):.1f}/s")

# -------------------------------
# 5) 분류기 학습 (CPU 기반)
# -------------------------------
clf = OneVsRestClassifier(
    LogisticRegression(max_iter=2000, C=2.0, class_weight="balanced")
)
t0 = time.perf_counter()
clf.fit(X_train, y_train)
t1 = time.perf_counter()
print(f"[Train] OvR-LogReg: {t1 - t0:.2f}s")

# -------------------------------
# 6) 검증 평가 (임계값 & Top-K)
# -------------------------------
try:
    y_val_proba = clf.predict_proba(X_val)
except Exception:
    scores = clf.decision_function(X_val)
    y_val_proba = 1 / (1 + np.exp(-scores))

# 임계값
y_val_thr = (y_val_proba >= THRESHOLD).astype(int)
print("\n=== Threshold-based ===")
print(f"Micro-F1: {f1_score(y_val, y_val_thr, average='micro'):.4f}")
print(f"Macro-F1: {f1_score(y_val, y_val_thr, average='macro'):.4f}")
print(f"Sample-F1: {f1_score(y_val, y_val_thr, average='samples'):.4f}")
print("\n[classification_report @thr]")
print(classification_report(y_val, y_val_thr, target_names=mlb.classes_, zero_division=0))

# Top-K
top_idx = np.argsort(-y_val_proba, axis=1)[:, :TOP_K]
y_val_topk = np.zeros_like(y_val_proba, dtype=int)
for i, idxs in enumerate(top_idx):
    y_val_topk[i, idxs] = 1

print("\n=== Top-K-based ===")
print(f"Micro-F1: {f1_score(y_val, y_val_topk, average='micro'):.4f}")
print(f"Macro-F1: {f1_score(y_val, y_val_topk, average='macro'):.4f}")
print(f"Sample-F1: {f1_score(y_val, y_val_topk, average='samples'):.4f}")
print("\n[classification_report @topK]")
print(classification_report(y_val, y_val_topk, target_names=mlb.classes_, zero_division=0))

# -------------------------------
# 7) 예측 함수 (한국어/영어 입력 그대로)
# -------------------------------
def predict_multilingual(text: str, topk=3, threshold=None):
    v = encode_with_auto_batch(embedder, [text], init_bs=64 if device=="cpu" else 256, min_bs=32)
    try:
        proba = clf.predict_proba(v)[0]
    except Exception:
        score = clf.decision_function(v)[0]
        proba = 1 / (1 + np.exp(-score))
    if threshold is not None:
        pick = np.where(proba >= threshold)[0]
    else:
        pick = np.argsort(-proba)[:topk]
    return [mlb.classes_[i] for i in pick]

# 예시
print("\n[Example Prediction]")
print(predict_multilingual("바닷가에서 느껴지는 시원하고 약간 달콤한 향이 좋아요", topk=3))
