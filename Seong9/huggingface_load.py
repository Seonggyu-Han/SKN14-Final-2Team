import pandas as pd
import re

# # 1) 원본 CSV: 파이프 구분자로 읽기
# df_raw = pd.read_csv("perfumes_hf.csv", sep="|", engine="python")

# # 2) 필요한 컬럼만 사용
# df = df_raw[["brand","name_perfume","gender","description","fragrances","family","subfamily"]].copy()

# # 4) fragrances(메인 어코드 후보) → 토큰화 함수 정의
# def parse_fragrances(s: str):
#     if not isinstance(s, str):
#         return []
#     toks = re.split(r"[;,/|]+|\s+", s.strip().lower())
#     toks = [t for t in toks if t]
#     out = []
#     i = 0
#     while i < len(toks):
#         if i + 1 < len(toks):
#             two = toks[i] + " " + toks[i+1]
#             if two in {"white floral","warm spicy","soft spicy"}:
#                 out.append(two)
#                 i += 2
#                 continue
#         out.append(toks[i])
#         i += 1
#     return out

# df["main_accord_en_tokens"] = df["fragrances"].apply(parse_fragrances)

# # 5) EN → KO 매핑 딕셔너리 (59개 라벨 기준)
# en2ko = {
#     "floral": "플로랄",
#     "white floral": "화이트플로랄",
#     "woody": "우디",
#     "oud": "오드", "agarwood": "오드", "oudh": "오드",
#     "citrus": "시트러스",
#     "fruity": "프루티",
#     "green": "그린",
#     "aromatic": "아로마틱", "herbal": "아로마틱",
#     "musk": "머스크", "musky": "머스크",
#     "amber": "앰버",
#     "vanilla": "바닐라",
#     "powdery": "파우더리",
#     "leather": "레더",
#     "spicy": "스파이시",
#     "warm spicy": "웜스파이시",
#     "soft spicy": "소프트스파이시", "anise": "소프트스파이시",
#     "aquatic": "아쿠아틱",
#     "marine": "마린",
#     "ozonic": "오조닉",
#     "smoky": "스모키", "smoke": "스모키",
#     "tobacco": "타바코",
#     "patchouli": "패출리",
#     "aldehydic": "알데하이드",
#     "tuberose": "튜베로즈",
#     "lavender": "라벤더",
#     "moss": "모스", "oakmoss": "모스",
#     "coconut": "코코넛",
#     "coffee": "커피",
#     "caramel": "카라멜",
#     "cherry": "체리",
#     "lactonic": "락토닉",
#     "honey": "허니",
#     "rose": "로즈",
#     "iris": "아이리스",
#     "animalic": "애니멀릭",
#     "fresh": "프레쉬",
#     "nutty": "너티",
#     "violet": "바이올렛",
#     "balsamic": "발사믹",
#     "beeswax": "비즈왁스",
#     "salty": "솔티",
#     "soap": "솝",
#     "sweet": "스위트",
#     "almond": "아몬드",
#     "earthy": "얼시", "earth": "얼시", "soil": "얼시",
#     "whiskey": "위스키",
#     "tropical": "트로피칼",
# }

# # 6) 토큰 리스트 → 한글 라벨 리스트 변환
# def map_en_to_ko(tokens):
#     ko_list = []
#     for t in tokens:
#         if t in en2ko:
#             ko_list.append(en2ko[t])
#         else:
#             # 예: musky → musk
#             t2 = t.rstrip("y")
#             if t2 in en2ko:
#                 ko_list.append(en2ko[t2])
#     # 중복 제거 + 순서 유지
#     seen, out = set(), []
#     for k in ko_list:
#         if k not in seen:
#             seen.add(k)
#             out.append(k)
#     return out

# df["main_accord_ko_list"] = df["main_accord_en_tokens"].apply(map_en_to_ko)
# df["main_accord_ko"] = df["main_accord_ko_list"].apply(lambda xs: " ".join(xs) if xs else "")

# # 7) 최종 컬럼만 정리
# final = df[["brand","name_perfume","gender","description","main_accord_ko"]].copy()

# # 8) CSV 저장 (utf-8-sig로 저장해야 Excel에서 한글 안 깨짐)
# final.to_csv("hf_perfumes_mapped_ko.csv", index=False, encoding="utf-8-sig")

# # 9) 결과 확인
# print(final.head(10))


import pandas as pd, re, csv, os

# 0) 경로 설정
RAW = "perfumes_hf.csv"                     # HF에서 받은 원본 (파이프 구분자)
    CLEAN = "hf_perfumes_min_clean.csv"      # 정리본
    MAPPED = "hf_perfumes_mapped_ko.csv"     # 최종 매핑본

# 1) 원본 읽기: 파이프(|) 구분자 시도 → 실패 시 구분자 자동추정
def read_pipe_csv(path):
    try:
        return pd.read_csv(path, sep="|", engine="python", encoding="utf-8-sig")
    except Exception:
        # 구분자 탐지
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            sample = f.read(8192)
        try:
            dialect = csv.Sniffer().sniff(sample)
            return pd.read_csv(path, sep=dialect.delimiter, engine="python", encoding="utf-8", on_bad_lines="skip")
        except Exception:
            # 콤마/세미콜론 폴백
            for sep in [",",";","\t"]:
                try:
                    return pd.read_csv(path, sep=sep, engine="python", encoding="utf-8", on_bad_lines="skip")
                except Exception:
                    pass
            raise

df_raw = read_pipe_csv(RAW)

# 2) 컬럼명 정규화 (소문자, 앞뒤 공백 제거, 연속 공백 1칸)
def norm_cols(cols):
    out = []
    for c in cols:
        c0 = str(c).strip().lower()
        c0 = re.sub(r"\s+", " ", c0)
        out.append(c0)
    return out

df_raw.columns = norm_cols(df_raw.columns)

# 3) 우리가 필요로 하는 컬럼 별칭 정의 + 자동 매핑
aliases = {
    "brand": ["brand", "brands"],
    "name_perfume": ["name_perfume", "name", "perfume_name", "perfume"],
    "gender": ["gender", "sex"],
    "description": ["description", "desc", "text"],
    # 핵심! fragrances의 다양한 변형을 모두 허용
    "fragrances": ["fragrances", "fragrance", "accords", "main accord", "main accords", "main_accord", "main_accords"],
    "family": ["family", "families"],
    "subfamily": ["subfamily", "sub family", "sub-family", "subfamilies"],
}

colmap = {}
for target, cands in aliases.items():
    found = None
    for cand in cands:
        if cand in df_raw.columns:
            found = cand
            break
    if found is not None:
        colmap[target] = found

# 4) fragrances 존재 확인 (여기서 없으면 헤더가 더 많이 깨진 상태)
if "fragrances" not in colmap:
    print("현재 컬럼 목록:", list(df_raw.columns))
    raise KeyError("`fragrances` 계열 컬럼을 찾지 못했습니다. 위 목록을 확인해 가깝게 보이는 이름을 aliases에 추가해 주세요.")

# 5) 정리본 만들기 (없는 것은 생성만 하고 비워둠)
need = ["brand","name_perfume","gender","description","fragrances","family","subfamily"]
df_clean = pd.DataFrame()
for k in need:
    src = colmap.get(k)
    if src is not None:
        df_clean[k] = df_raw[src]
    else:
        df_clean[k] = None

# 저장 (엑셀 호환 위해 utf-8-sig)
df_clean.to_csv(CLEAN, index=False, encoding="utf-8-sig")
print("정리본 저장:", CLEAN, df_clean.shape)

# 6) fragrances → 토큰화
def parse_fr(s: str):
    if not isinstance(s, str): 
        return []
    toks = re.split(r"[;,/|]+|\s+", s.strip().lower())
    toks = [t for t in toks if t]
    out, i = [], 0
    while i < len(toks):
        if i+1 < len(toks):
            two = toks[i] + " " + toks[i+1]
            if two in {"white floral","warm spicy","soft spicy","fresh spicy","woody spicy","fruity floral"}:
                out.append(two); i += 2; continue
        out.append(toks[i]); i += 1
    return out

df = pd.read_csv(CLEAN, encoding="utf-8-sig")
df["en_tokens"] = df[colmap["fragrances"] if "fragrances" not in df.columns else "fragrances"].apply(parse_fr)

# 7) EN→KO 매핑 (우리 59라벨 기준 + 확장 별칭)
en2ko = {
    "floral":"플로랄", "white floral":"화이트플로랄",
    "woody":"우디",
    "oud":"오드","agarwood":"오드","oudh":"오드",
    "citrus":"시트러스","fruity":"프루티","green":"그린",
    "aromatic":"아로마틱","herbal":"아로마틱",
    "musk":"머스크","musky":"머스크","musks":"머스크",
    "amber":"앰버","ambery":"앰버",
    "vanilla":"바닐라","vanillic":"바닐라",
    "powdery":"파우더리","powder":"파우더리",
    "leather":"레더","leathery":"레더",
    "spicy":"스파이시","fresh spicy":("프레쉬","스파이시"), "woody spicy":("우디","스파이시"),
    "warm spicy":"웜스파이시","soft spicy":"소프트스파이시","anise":"소프트스파이시",
    "aquatic":"아쿠아틱","marine":"마린","ozonic":"오조닉",
    "smoky":"스모키","smoke":"스모키","incense":"스모키","incensy":"스모키",
    "tobacco":"타바코",
    "patchouli":"패출리",
    "aldehydic":"알데하이드",
    "tuberose":"튜베로즈",
    "lavender":"라벤더",
    "moss":"모스","oakmoss":"모스",
    "coconut":"코코넛",
    "coffee":"커피",
    "caramel":"카라멜",
    "cherry":"체리",
    "lactonic":"락토닉",
    "honey":"허니",
    "rose":"로즈",
    "iris":"아이리스",
    "animalic":"애니멀릭",
    "fresh":"프레쉬",
    "nutty":"너티",
    "violet":"바이올렛",
    "balsamic":"발사믹","resinous":"발사믹",
    "beeswax":"비즈왁스",
    "salty":"솔티",
    "soap":"솝","soapy":"솝",
    "sweet":"스위트",
    "almond":"아몬드",
    "earthy":"얼시","earth":"얼시","soil":"얼시",
    "whiskey":"위스키",
    "tropical":"트로피칼",
    "fruity floral":("프루티","플로랄"),
    "oriental":"앰버",
    # 복수형
    "florals":"플로랄","woods":"우디","fruits":"프루티",
}

def map_en_to_ko(tokens):
    out, seen = [], set()
    for t in tokens:
        cand = en2ko.get(t)
        if not cand:
            # 어간 단순화(s, y 제거)
            t2 = t.rstrip("s")
            cand = en2ko.get(t2) or en2ko.get(t2.rstrip("y"))
        if cand:
            if isinstance(cand, tuple):
                for k in cand:
                    if k not in seen:
                        seen.add(k); out.append(k)
            else:
                if cand not in seen:
                    seen.add(cand); out.append(cand)
    return out

df["main_accord_ko_list"] = df["en_tokens"].apply(map_en_to_ko)
df["main_accord_ko"] = df["main_accord_ko_list"].apply(lambda xs: " ".join(xs) if xs else "")

# 8) 최종 CSV
final = pd.DataFrame({
    "brand": df[colmap["brand"]] if "brand" not in df.columns and "brand" in colmap else df.get("brand"),
    "name_perfume": df[colmap["name_perfume"]] if "name_perfume" not in df.columns and "name_perfume" in colmap else df.get("name_perfume"),
    "gender": df[colmap["gender"]] if "gender" not in df.columns and "gender" in colmap else df.get("gender"),
    "description": df[colmap["description"]] if "description" not in df.columns and "description" in colmap else df.get("description"),
    "main_accord_ko": df["main_accord_ko"],
})
final.to_csv(MAPPED, index=False, encoding="utf-8-sig")
print("매핑본 저장:", MAPPED, final.shape)

# 9) sanity check
print("컬럼:", list(final.columns))
print(final.head(5))
