import os
import re
import sys
import textwrap
import unicodedata
import requests
from dotenv import load_dotenv

HOST = "fragrancefinder-api.p.rapidapi.com"

def get_key() -> str:
    load_dotenv()
    key = os.getenv("RAPIDAPI_KEY_SEONGKYU")
    if not key:
        print("[ERR] .env에 RAPIDAPI_KEY가 없습니다.")
        sys.exit(1)
    return key

def call_get(path: str, params: dict | None = None):
    url = f"https://{HOST}{path}"
    headers = {
        "x-rapidapi-key": get_key(),
        "x-rapidapi-host": HOST,
    }
    r = requests.get(url, headers=headers, params=params, timeout=20)
    print(f"[HTTP] {r.status_code} GET {url} params={params or {}}")
    try:
        data = r.json()
    except Exception:
        print(r.text)
        r.raise_for_status()
        raise
    if r.status_code >= 400:
        print("[API ERROR]", data)
        r.raise_for_status()
    return data

def wrap(s: str | None, width: int = 90) -> str:
    if not s:
        return ""
    return "\n".join(textwrap.wrap(s, width=width))

def search_perfume(query: str) -> list[dict]:
    """
    /perfumes/search 는 list 를 반환 (플레이그라운드와 동일 구조).
    """
    data = call_get("/perfumes/search", params={"q": query})
    return data if isinstance(data, list) else (data.get("results") or [])

def get_dupes(perfume_id: str) -> dict:
    return call_get(f"/dupes/{perfume_id}")

STOP_TOKENS = {
    "eau", "de", "parfum", "parfume", "perfume", "toilette", "edt", "edp",
    "cologne", "edc", "extrait", "intense", "extreme", "elixir", "absolu",
    "absolue", "nacre", "spray",
    "for", "women", "woman", "men", "man", "unisex", "femme", "homme",
    "edition", "collection", "reserve", "minérale", "mineral",
}

def _nfkd_lower(s: str) -> str:
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))

def _space_norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def _normalize_ascii(s: str) -> str:
    return _space_norm(_nfkd_lower(s))

def _strip_trailing_for_segment(title: str) -> str:
    return re.sub(r"\s+for\s+.*$", "", title, flags=re.IGNORECASE).strip()

def _tokenize(s: str) -> list[str]:
    s = _normalize_ascii(s)
    return [t for t in re.split(r"[^\w]+", s) if t]

def _remove_brand_words(tokens: list[str], brand: str) -> list[str]:
    b_tokens = set(_tokenize(brand))
    return [t for t in tokens if t not in b_tokens]

def _remove_stop_tokens(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in STOP_TOKENS]

def _title_core_tokens(title: str, brand: str) -> list[str]:
    base = _strip_trailing_for_segment(title)
    toks = _tokenize(base)
    toks = _remove_brand_words(toks, brand)
    toks = _remove_stop_tokens(toks)
    return toks

def _query_core_tokens(name: str, brand: str) -> list[str]:
    toks = _tokenize(name)
    toks = _remove_brand_words(toks, brand)
    toks = _remove_stop_tokens(toks)
    return toks

def url_brand_score(u: str, brand: str) -> int:
    u = (u or "").lower()
    words = [
        brand.lower(),
        brand.lower().replace(" ", "-"),
        brand.lower().replace(" ", ""),
    ]
    return sum(1 for w in words if w and w in u)

def overlap_score(core_tokens: list[str], candidate_tokens: list[str]) -> tuple[int, float]:
    """
    반환: (겹치는 토큰 개수, recall 비율 = 겹치는 수 / 쿼리 토큰 수)
    """
    cs = set(candidate_tokens)
    qs = [t for t in core_tokens if t]
    hits = [t for t in qs if t in cs]
    return (len(hits), (len(hits) / max(1, len(qs))))

def pick_best_by_name_brand(results: list[dict], target_name: str, target_brand: str) -> dict | None:
    tb = _normalize_ascii(target_brand)
    q_tokens = _query_core_tokens(target_name, target_brand)
    if not q_tokens:
        q_tokens = _tokenize(target_name)

    brand_hits = []
    for r in results:
        rb = _normalize_ascii(r.get("brand", ""))
        if tb in rb:
            brand_hits.append(r)
    if not brand_hits:
        return None

    ranked: list[tuple[tuple, dict]] = []
    for r in brand_hits:
        cand_tokens = _title_core_tokens(r.get("perfume", ""), target_brand)
        ovl_cnt, recall = overlap_score(q_tokens, cand_tokens)
        score_tuple = (
            ovl_cnt,
            recall,
            url_brand_score(r.get("url", ""), target_brand),
            -len(cand_tokens),
        )
        ranked.append((score_tuple, r))

    ranked = [x for x in ranked if x[0][0] > 0]
    if not ranked:
        return None

    ranked.sort(key=lambda x: x[0], reverse=True)
    return ranked[0][1]

def print_one_perfume(p: dict):
    print("\n===== 매칭된 향수 =====")
    print("이름 :", p.get("perfume"))
    print("브랜드:", p.get("brand"))
    print("노트 :", ", ".join(p.get("notes", [])))
    print("이미지:", p.get("image") or "이미지 없음")
    print("URL  :", p.get("url"))
    desc = p.get("description") or ""
    if desc:
        print("설명 :\n", wrap(desc), sep="")

def print_base_perfume(base: dict):
    print("\n===== 기준 향수 =====")
    print("이름 :", base.get("perfume"))
    print("브랜드:", base.get("brand"))
    print("노트 :", ", ".join(base.get("notes", [])))
    print("URL  :", base.get("url"))
    print("설명 :\n", wrap(base.get("description")), sep="")

def print_recommendations(recs: list[dict]):
    print("\n===== 추천 향수 (유사도 기준) =====")
    if not recs:
        print("(추천 결과 없음)")
        return
    for i, r in enumerate(recs, 1):
        print("-" * 60)
        print(f"[{i}] {r.get('perfume')}  ({r.get('brand')})")
        print("   노트 :", ", ".join(r.get("notes", [])))
        if "combinedSimilarity" in r:
            print(f"   유사도: {r.get('combinedSimilarity'):.2f}%")
        img = r.get("image") or "이미지 없음"
        print("   이미지:", img)
        print("   URL  :", r.get("url"))
        if r.get("description"):
            print("   설명  :")
            print(textwrap.indent(wrap(r["description"]), prefix="           "))

def cmd_search(args: list[str]):
    q = " ".join(args).strip()
    data = search_perfume(q)
    from pprint import pprint
    pprint(data)

def show_by_name(name: str, brand: str):
    query = f"{name} {brand}".strip()
    results = search_perfume(query)
    picked = pick_best_by_name_brand(results, name, brand)
    if not picked:
        print("[매칭 실패] 이름/브랜드로 유의미한 후보를 찾지 못했습니다.")
        if isinstance(results, list) and results:
            print("\n[참고] 검색 상위 5개:")
            for i, r in enumerate(results[:5], 1):
                print(f"  {i}. {r.get('perfume')}  // brand: {r.get('brand')}")
        return
    print_one_perfume(picked)

def cmd_dupes_by_id(pid: str):
    data = get_dupes(pid)
    base = data.get("perfume", {})
    recs = data.get("recommendations", [])
    print_base_perfume(base)
    print_recommendations(recs)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("사용법:")
        print('  python perfume_api_test.py search "<임의 쿼리>"')
        print('  python perfume_api_test.py show-by-name "<향수명>" "<브랜드>"')
        print('  python perfume_api_test.py dupes "<perfume_id>"')
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "search" and len(sys.argv) >= 3:
        cmd_search(sys.argv[2:])
    elif cmd == "show-by-name" and len(sys.argv) >= 4:
        show_by_name(sys.argv[2], sys.argv[3])
    elif cmd == "dupes" and len(sys.argv) >= 3:
        cmd_dupes_by_id(sys.argv[2])
    else:
        print("잘못된 명령입니다.")
