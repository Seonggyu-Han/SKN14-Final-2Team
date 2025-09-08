# 1) 환경/경로 설정

import os, json, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer

DATA_PATH = "hf_perfumes_mapped_ko.csv"   # <- 필요시 경로 수정
TEXT_COL  = "description"                  # 영어 문장
LABEL_COL = "main_accord_ko"               # 한글 라벨(공백 구분)
OUTPUT_DIR = "./hf_xlmr_ckpt"              # 모델 저장 폴더
MODEL_NAME = "xlm-roberta-base"            # 다국어 베이스


# 2) 데이터 로드 + 결측/빈 라벨 처리

# 로드
df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
df[LABEL_COL] = df[LABEL_COL].fillna("").astype(str)

# 공백 구분 다중라벨 -> 리스트
def split_labels(s: str):
    return [t for t in s.split() if t.strip()]

df["labels_list"] = df[LABEL_COL].apply(split_labels)

# 학습셋: 라벨이 있는 행만 사용
n_total = len(df)
df_trainable = df[df["labels_list"].map(len) > 0].copy()
n_dropped = n_total - len(df_trainable)
print(f"총 {n_total}행 중, 빈 라벨 {n_dropped}행 제외 → 학습 행 {len(df_trainable)}")

# 라벨 인코딩
all_labels = sorted({lab for labs in df_trainable["labels_list"] for lab in labs})
mlb = MultiLabelBinarizer(classes=all_labels)
Y = mlb.fit_transform(df_trainable["labels_list"])

# train/valid split
idx_tr, idx_va = train_test_split(
    np.arange(len(df_trainable)),
    test_size=0.1,
    random_state=42,
    stratify=(Y.sum(axis=1) > 0)
)

df_tr = df_trainable.iloc[idx_tr].reset_index(drop=True)
df_va = df_trainable.iloc[idx_va].reset_index(drop=True)
Y_tr, Y_va = Y[idx_tr], Y[idx_va]
print("라벨 개수:", len(all_labels))
print("train:", df_tr.shape, "valid:", df_va.shape)



# 3) HF datasets 변환 & 토크나이즈

from datasets import Dataset
from transformers import AutoTokenizer

USE_TEXT_COL = TEXT_COL

train_ds = Dataset.from_dict({
    USE_TEXT_COL: df_tr[USE_TEXT_COL].astype(str).tolist(),
    "labels": Y_tr.astype("float32").tolist()
})
valid_ds = Dataset.from_dict({
    USE_TEXT_COL: df_va[USE_TEXT_COL].astype(str).tolist(),
    "labels": Y_va.astype("float32").tolist()
})

tok = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize(batch):
    return tok(batch[USE_TEXT_COL], truncation=True, padding="max_length", max_length=256)

train_ds = train_ds.map(tokenize, batched=True)
valid_ds = valid_ds.map(tokenize, batched=True)

for ds in (train_ds, valid_ds):
    ds.set_format(type="torch", columns=["input_ids","attention_mask","labels"])

"tokenized"



# 4) 모델 정의 & 학습

import torch
from transformers import AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.metrics import f1_score, jaccard_score

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(all_labels),
    problem_type="multi_label_classification"
)

def compute_metrics(pred):
    logits, labels = pred
    probs = 1 / (1 + np.exp(-logits))
    preds = (probs >= 0.5).astype(int)
    micro = f1_score(labels, preds, average="micro", zero_division=0)
    macro = f1_score(labels, preds, average="macro", zero_division=0)
    jacc = jaccard_score(labels, preds, average="samples")
    return {"micro_f1": micro, "macro_f1": macro, "jaccard": jacc}

args = TrainingArguments(
    OUTPUT_DIR,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    num_train_epochs=3,           # 필요시 4~5로 증가
    weight_decay=0.01,
    logging_steps=50,
    load_best_model_at_end=True,
    metric_for_best_model="micro_f1",
    greater_is_better=True,
    fp16=True if torch.cuda.is_available() else False
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=valid_ds,
    tokenizer=tok,
    compute_metrics=compute_metrics
)

trainer.train()

# 5) 체크포인트에 라벨/메타 저장


import os, json
os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(os.path.join(OUTPUT_DIR, "labels_ko.json"), "w", encoding="utf-8") as f:
    json.dump(all_labels, f, ensure_ascii=False, indent=2)
with open(os.path.join(OUTPUT_DIR, "meta.json"), "w", encoding="utf-8") as f:
    json.dump({"text_col": USE_TEXT_COL}, f, ensure_ascii=False, indent=2)
"saved labels/meta"



# 6) 라벨별 임계값 최적화
from sklearn.metrics import f1_score
import numpy as np, os

pred = trainer.predict(valid_ds)
probs = 1 / (1 + np.exp(-pred.predictions))   # (N,L)
labels = pred.label_ids                        # (N,L)

ths = np.arange(0.30, 0.71, 0.05)
best_th_per_label = np.zeros(probs.shape[1], dtype=float) + 0.5

for j in range(probs.shape[1]):
    best_f1, best_th = -1, 0.5
    for th in ths:
        y_pred = (probs[:, j] >= th).astype(int)
        f1 = f1_score(labels[:, j], y_pred, zero_division=0)
        if f1 > best_f1:
            best_f1, best_th = f1, th
    best_th_per_label[j] = best_th

np.save(os.path.join(OUTPUT_DIR, "label_thresholds.npy"), best_th_per_label)
best_th_per_label[:10], float(best_th_per_label.mean())



#  7) 추론(한국어 문장도 바로)

import torch, numpy as np, json, os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def load_model_for_infer(ckpt_dir=OUTPUT_DIR):
    tok_i = AutoTokenizer.from_pretrained(ckpt_dir)
    mdl_i = AutoModelForSequenceClassification.from_pretrained(ckpt_dir)
    labels_ko = json.load(open(os.path.join(ckpt_dir, "labels_ko.json"), "r", encoding="utf-8"))
    th_path = os.path.join(ckpt_dir, "label_thresholds.npy")
    per_label_th = np.load(th_path) if os.path.exists(th_path) else None
    meta = json.load(open(os.path.join(ckpt_dir, "meta.json"), "r", encoding="utf-8"))
    return tok_i, mdl_i, labels_ko, per_label_th, meta

tok_i, mdl_i, labels_ko, per_label_th, meta = load_model_for_infer(OUTPUT_DIR)

def predict_accords(texts, use_per_label_threshold=True, base_threshold=0.5, topk=10):
    if isinstance(texts, str):
        texts = [texts]
    inputs = tok_i(texts, return_tensors="pt", truncation=True, padding=True, max_length=256)
    with torch.no_grad():
        logits = mdl_i(**inputs).logits
    probs = torch.sigmoid(logits).cpu().numpy()

    outs = []
    for i, p in enumerate(probs):
        if use_per_label_threshold and per_label_th is not None:
            mask = (p >= per_label_th)
        else:
            mask = (p >= base_threshold)
        picked = [(labels_ko[j], float(p[j])) for j in np.where(mask)[0]]
        top = sorted([(labels_ko[j], float(p[j])) for j in range(len(labels_ko))], key=lambda x: -x[1])[:topk]
        outs.append({"text": texts[i], "picked": picked, "topk": top})
    return outs

# 예시: 한국어 문장
ex = "달콤한 바닐라에 따뜻한 스파이스가 포근하게 감싸는 겨울 향"
res = predict_accords(ex, use_per_label_threshold=True)
res[0]


# 8) (선택) 검증셋 지표 + 라벨별 리포트

from sklearn.metrics import classification_report

# 0.5 기준 간단 리포트
pred = trainer.predict(valid_ds)
probs = 1 / (1 + np.exp(-pred.predictions))
preds = (probs >= 0.5).astype(int)
print("== threshold 0.5 ==")
print(classification_report(pred.label_ids, preds, target_names=all_labels, zero_division=0))

# per-label threshold 리포트 (있을 때)
if per_label_th is not None:
    preds2 = (probs >= per_label_th).astype(int)
    print("== per-label thresholds ==")
    print(classification_report(pred.label_ids, preds2, target_names=all_labels, zero_division=0))
