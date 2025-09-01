# csv_assemble.py
# - cleaned-eng(eng_name) 과 accords_all(perfume_name) 병합
# - 규칙: exact -> case_only -> whitespace_only -> suffix_removed
#         -> paren_removed -> punct_removed -> fuzzy>=0.90 -> no_suggestion
# - 결과: cleaned 행 순서 보존(원래 순서에 맞춰 확장), merge_rule 라벨링

from pathlib import Path
import pandas as pd
import re
import string
from difflib import SequenceMatcher

# =========================
# 0) 경로/설정
# =========================
BASE = Path(__file__).resolve().parent

CLEANED_PATH = BASE / "separated_perfume_cleaned_eng.csv"  # cleaned-eng
ACCORDS_PATH = BASE / "main_accords_all.csv"               # accords_all
OUT_PATH     = BASE / "merged_cleaned_eng__rules_applied.csv"

# 필드명
ENG_COL = "eng_name"          # cleaned 기준 키
ACC_COL = "perfume_name"      # accords 기준 키

# fuzzy 임계값
FUZZY_THRESHOLD = 0.90

# =========================
# 1) 유틸 함수
# =========================
def norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())

def strip_suffixes(s: str) -> str:
    # 끝에 붙는 세트/테스터/리필 등 제거 (케이스 무시)
    suffixes = [
        r"travel set", r"gift set", r"discovery set", r"sample set",
        r"tester", r"refill", r"duo", r"trio", r"mini", r"set"
    ]
    x = s
    for suf in suffixes:
        # 단어 경계 + 문자열 끝에서만 제거
        x = re.sub(rf"\b{suf}\b\s*$", "", x, flags=re.IGNORECASE).strip()
        x = norm_space(x)
    return x

def strip_parens(s: str) -> str:
    # 괄호 내용 제거: (), [], {}
    x = re.sub(r"\([^)]*\)", " ", s)
    x = re.sub(r"\[[^\]]*\]", " ", x)
    x = re.sub(r"\{[^}]*\}", " ", x)
    return norm_space(x)

def remove_punct(s: str) -> str:
    # 모든 구두점 제거(하이픈 포함), 공백 정리
    table = str.maketrans("", "", string.punctuation)
    return norm_space(s.translate(table))

def casefold(s: str) -> str:
    return s.casefold()

def similar(a: str, b: str) -> float:
    # 0~1 사이 유사도
    return SequenceMatcher(None, a, b).ratio()

def add_rule(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    df = df.copy()
    df.insert(0, "merge_rule", rule)
    return df

# =========================
# 2) 데이터 로드
# =========================
print("CLEANED_PATH =", CLEANED_PATH)
print("ACCORDS_PATH =", ACCORDS_PATH)

cleaned = pd.read_csv(CLEANED_PATH, encoding="utf-8-sig")
accords = pd.read_csv(ACCORDS_PATH, encoding="utf-8-sig")

if ENG_COL not in cleaned.columns:
    raise KeyError("cleaned에 '{}' 컬럼이 없습니다. 실제 컬럼: {}".format(ENG_COL, list(cleaned.columns)))
if ACC_COL not in accords.columns:
    raise KeyError("accords에 '{}' 컬럼이 없습니다. 실제 컬럼: {}".format(ACC_COL, list(accords.columns)))

# 최소한의 안정: 양끝 공백 제거
cleaned[ENG_COL] = cleaned[ENG_COL].astype(str).str.strip()
accords[ACC_COL] = accords[ACC_COL].astype(str).str.strip()

# 원래 순서 보존용 인덱스
cleaned = cleaned.reset_index(drop=True).copy()
cleaned["_rid"] = range(len(cleaned))

# accords 사본(규칙용 파생 컬럼)
acc_df = accords.copy()
acc_df["_acc_space"]   = acc_df[ACC_COL].map(norm_space)
acc_df["_acc_case"]    = acc_df["_acc_space"].map(casefold)
acc_df["_acc_parens"]  = acc_df["_acc_space"].map(strip_parens)
acc_df["_acc_nopunct"] = acc_df["_acc_parens"].map(remove_punct)

# cleaned 파생
cln_df = cleaned.copy()
cln_df["_eng_space"]   = cln_df[ENG_COL].map(norm_space)
cln_df["_eng_case"]    = cln_df["_eng_space"].map(casefold)
cln_df["_eng_suffix"]  = cln_df["_eng_space"].map(strip_suffixes)
cln_df["_eng_parens"]  = cln_df["_eng_space"].map(strip_parens)
cln_df["_eng_nopunct"] = cln_df["_eng_parens"].map(remove_punct)

# =========================
# 3) 단계별 매칭
#    - 각 단계에서 매칭된 cleaned._rid 를 수집하고,
#      다음 단계에서는 남은(미매칭)들만 대상으로 수행
# =========================
matched_ids = set()
results = []  # 단계별 결과 DataFrame 보관

def stage_left_merge(left_df: pd.DataFrame, right_df: pd.DataFrame,
                     left_key: str, right_key: str, rule_name: str) -> pd.DataFrame:
    """
    남은(cln_df 중 미매칭) 행을 left로 하여, 규칙 키로 inner merge
    - left_df: cln_df[~_rid.isin(matched_ids)]
    - right_df: acc_df
    """
    # left에 원본 cleaned 컬럼과 조인키를 포함시키고,
    # right에는 원본 accords 전체 컬럼을 포함시켜 확장되게 함
    merged = left_df.merge(
        right_df, left_on=left_key, right_on=right_key, how="inner", suffixes=("", "_acc")
    )
    if not merged.empty:
        merged = add_rule(merged, rule_name)
    return merged

# 3-1) exact
left = cln_df[~cln_df["_rid"].isin(matched_ids)]
exact = stage_left_merge(left, acc_df, ENG_COL, ACC_COL, "exact")
results.append(exact)
matched_ids.update(exact["_rid"].unique().tolist())

# 3-2) case_only (대소문자 무시)
left = cln_df[~cln_df["_rid"].isin(matched_ids)]
case_only = stage_left_merge(left, acc_df, "_eng_case", "_acc_case", "case_only")
results.append(case_only)
matched_ids.update(case_only["_rid"].unique().tolist())

# 3-3) whitespace_only (공백 정리)
left = cln_df[~cln_df["_rid"].isin(matched_ids)]
ws_only = stage_left_merge(left, acc_df, "_eng_space", "_acc_space", "whitespace_only")
results.append(ws_only)
matched_ids.update(ws_only["_rid"].unique().tolist())

# 3-4) suffix_removed (세트/테스터/리필 등 접미사 제거 후 비교)
left = cln_df[~cln_df["_rid"].isin(matched_ids)]
suf_removed = stage_left_merge(left, acc_df, "_eng_suffix", "_acc_space", "suffix_removed")
results.append(suf_removed)
matched_ids.update(suf_removed["_rid"].unique().tolist())

# 3-5) paren_removed (괄호 제거)
left = cln_df[~cln_df["_rid"].isin(matched_ids)]
par_removed = stage_left_merge(left, acc_df, "_eng_parens", "_acc_parens", "paren_removed")
results.append(par_removed)
matched_ids.update(par_removed["_rid"].unique().tolist())

# 3-6) punct_removed (구두점 제거)
left = cln_df[~cln_df["_rid"].isin(matched_ids)]
pun_removed = stage_left_merge(left, acc_df, "_eng_nopunct", "_acc_nopunct", "punct_removed")
results.append(pun_removed)
matched_ids.update(pun_removed["_rid"].unique().tolist())

# 3-7) fuzzy_suggestion (0.90 이상만)
left = cln_df[~cln_df["_rid"].isin(matched_ids)].copy()
fuzzy_matched = pd.DataFrame()
if not left.empty:
    # accords 후보 사전 (nopunct/casefold 기준으로 비교)
    acc_candidates = acc_df[["_acc_nopunct", ACC_COL]].drop_duplicates().values.tolist()
    # 각 left 행에 대해 best match 하나만 선택
    chosen = []
    for _, r in left.iterrows():
        ln = r["_eng_nopunct"]
        best_sc, best_nm = 0.0, None
        for an_norm, a_name in acc_candidates:
            sc = similar(ln, an_norm)
            if sc > best_sc:
                best_sc, best_nm = sc, a_name
        if best_nm is not None and best_sc >= FUZZY_THRESHOLD:
            chosen.append((r["_rid"], best_nm, best_sc))

    if chosen:
        map_df = pd.DataFrame(chosen, columns=["_rid", "_fuzzy_target_name", "_fuzzy_score"])
        # left(미매칭)와 매핑을 합치고, accords에 target_name으로 조인
        tmp = left.merge(map_df, on="_rid", how="inner")
        fuzzy_matched = tmp.merge(acc_df, left_on="_fuzzy_target_name", right_on=ACC_COL, how="inner")
        if not fuzzy_matched.empty:
            fuzzy_matched = add_rule(fuzzy_matched, "fuzzy_suggestion>=0.90")
            results.append(fuzzy_matched)
            matched_ids.update(fuzzy_matched["_rid"].unique().tolist())

# 3-8) no_suggestion: 끝까지 못 맞춘 애들 그냥 남김(붙이지 않음)
left = cln_df[~cln_df["_rid"].isin(matched_ids)].copy()
if not left.empty:
    # accords 컬럼을 NaN으로 채워서 모양 맞추기
    for col in accords.columns:
        if col not in left.columns:
            left[col] = pd.NA
    left = add_rule(left, "no_suggestion")
    results.append(left)

# =========================
# 4) 결과 결합 및 정렬
# =========================
final = pd.concat(results, ignore_index=True, sort=False)

# 원래 cleaned 컬럼 + accords 컬럼 순서로 정리
cleaned_cols = list(cleaned.columns)  # _rid 포함
accords_cols = [c for c in accords.columns if c not in cleaned_cols]
ordered_cols = ["merge_rule"] + cleaned_cols + accords_cols
final = final[ordered_cols]

# 원래 행 순서 기준으로 정렬(확장된 행은 같은 _rid끼리 묶임)
final = final.sort_values(by=["_rid", "merge_rule"]).reset_index(drop=True)

# helper 컬럼 정리(원한다면 남겨도 됨)
drop_helpers = [c for c in final.columns if c.startswith("_eng_") or c.startswith("_acc_") or c in ["_fuzzy_target_name", "_fuzzy_score"]]
final = final.drop(columns=[c for c in drop_helpers if c in final.columns], errors="ignore")

# =========================
# 5) 저장 및 로그
# =========================
final.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
print("done. output file:", OUT_PATH.name)

# 간단 요약
summary = final.groupby("merge_rule")["_rid"].nunique().reset_index(name="rows")
print("merge summary by rule:")
print(summary.to_string(index=False))
