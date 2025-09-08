# search.py — 자동 필터(노트/브랜드/가격) + 스티키 백오프 + 한 줄 RAG 응답
import os, re
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from pinecone.exceptions import NotFoundException

load_dotenv()

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
CHAT_MODEL  = os.getenv("CHAT_MODEL",  "gpt-4o-mini")
INDEX_NAME  = os.getenv("PINECONE_INDEX_CORPUS", "perfume-rag")
NAMESPACE   = os.getenv("PINECONE_NAMESPACE_CORPUS", "catalog")
MIN_SCORE   = float(os.getenv("RAG_MIN_SCORE", "0.35"))
TOPK_DEF    = int(os.getenv("RAG_TOPK", "8"))

STICKY_BRAND = True
STICKY_NOTES = True

oa_key = os.getenv("OPENAI_API_KEY")
pc_key = os.getenv("PINECONE_API_KEY")
if not oa_key or not pc_key:
    raise RuntimeError("OPENAI_API_KEY / PINECONE_API_KEY가 .env에 없습니다.")

_client = OpenAI(api_key=oa_key)
_pc = Pinecone(api_key=pc_key)
try:
    _index = _pc.Index(INDEX_NAME)
    _pc.describe_index(INDEX_NAME)
except NotFoundException:
    raise RuntimeError(f"Pinecone 인덱스 '{INDEX_NAME}'가 없습니다. 먼저 업로드를 완료하세요.")

def _embed(text: str) -> List[float]:
    return _client.embeddings.create(model=EMBED_MODEL, input=text).data[0].embedding

def _norm_list_lower(xs: Optional[List[str]]) -> List[str]:
    if not xs: return []
    seen, out = set(), []
    for x in xs:
        s = (x or "").strip().lower()
        if s and s not in seen:
            seen.add(s); out.append(s)
    return out

def _normalize(s: str) -> str:
    return s.lower().replace(" ", "")

BRAND_ALIASES = {
    "jo malone": "조말론", "jomlaone": "조말론", "조 말론": "조말론",
    "tom ford": "톰포드", "톰 포드": "톰포드",
    "frederic malle": "프레데릭 말", "frédéric malle": "프레데릭 말", "프레데릭말": "프레데릭 말",
    "estee lauder": "에스티 로더", "estée lauder": "에스티 로더", "에스티로더": "에스티 로더",
    "le labo": "르 라보", "르라보": "르 라보",
    "byredo": "바이레도",
    "maison margiela": "메종 마르지엘라", "margiela": "메종 마르지엘라",
    "chanel": "샤넬", "dior": "디올", "guerlain": "겔랑",
    "lancome": "랑콤", "lancôme": "랑콤",
    "ysl": "입생로랑", "yves saint laurent": "입생로랑",
    "gucci": "구찌", "prada": "프라다", "valentino": "발렌티노",
    "givenchy": "지방시", "montblanc": "몽블랑", "bvlgari": "불가리",
    "zara": "자라", "armani": "아르마니", "giorgio armani": "조르지오 아르마니",
    "calvin klein": "캘빈클라인", "creed": "크리드", "hermes": "에르메스",
}
KNOWN_BRANDS = set(list(BRAND_ALIASES.values()) + list(BRAND_ALIASES.keys()))

NOTE_ALIASES = {
    "우디": ["나무향", "우드", "wood", "woody"],
    "시트러스": ["레몬", "라임", "오렌지", "베르가못", "citrus"],
    "파우더리": ["파우더", "포근한", "파우더리한", "powdery", "코튼", "솝", "비누향", "soap", "cotton"],
    "머스크": ["머스키", "musky", "musk"],
    "플로랄": ["꽃향", "플로럴", "floral"],
    "화이트 플로랄": ["화이트플로랄", "white floral", "화이트플로럴"],
    "프루티": ["과일향", "과즙", "fruit", "fruity"],
    "스파이시": ["스파이스", "spicy", "peppery", "페퍼리"],
    "그린": ["허브", "허벌", "herbal", "green"],
    "얼씨": ["earthy", "어시", "토양"],
    "스모키": ["smoky", "훈연", "훈제"],
    "앰버": ["ambery", "엠버"],
    "바닐라": ["vanilla"],
    "구르망": ["그루망", "gourmand"],
    "아쿠아": ["마린", "바다향", "수분감", "aqcua", "marine", "aquatic"],
    "프레시": ["상쾌", "상큼", "시원한", "fresh", "프레시"],
    "레더": ["가죽", "leather"],
    "코코넛": ["coconut"],
}

def _extract_brands(query: str) -> List[str]:
    qn = _normalize(query)
    out = []
    for token in KNOWN_BRANDS:
        t = _normalize(token)
        if t and t in qn:
            canon = BRAND_ALIASES.get(token, token)
            out.append(canon.lower())
    return list(dict.fromkeys(out))

def _extract_notes(query: str) -> List[str]:
    q = query.lower()
    found = []
    for canon, syns in NOTE_ALIASES.items():
        if any(s in q for s in syns) or canon in q:
            found.append(canon)
    return list(dict.fromkeys(found))

def _extract_price(query: str) -> (Optional[int], Optional[int]):
    q = query.replace(" ", "")
    m = re.search(r"(\d+)\s*~\s*(\d+)\s*만", q)
    if m:
        return int(m.group(1)) * 10000, int(m.group(2)) * 10000
    m = re.search(r"(\d+)\s*만\s*원?\s*대", q)
    if m:
        p = int(m.group(1)) * 10000
        return int(p * 0.9), int(p * 1.1)
    m = re.search(r"(\d+)\s*만\s*원?\s*이하|(\d+)\s*만\s*원?\s*까지", q)
    if m:
        v = m.group(1) or m.group(2)
        return None, int(v) * 10000
    m = re.search(r"(\d+)\s*만\s*원?\s*이상", q)
    if m:
        return int(m.group(1)) * 10000, None
    m = re.search(r"(\d{2,})\s*원", q)
    if m:
        val = int(m.group(1))
        return int(val * 0.9), int(val * 1.1)
    return None, None

def build_filters(
    notes: Optional[List[str]] = None,
    brands: Optional[List[str]] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    f: Dict[str, Any] = {}
    n = _norm_list_lower(notes)
    if n: f["main_accords"] = {"$in": n}
    b = _norm_list_lower(brands)
    if b: f["brand"] = {"$in": b}
    if price_min is not None or price_max is not None:
        rng: Dict[str, Any] = {}
        if price_min is not None: rng["$gte"] = int(price_min)
        if price_max is not None: rng["$lte"] = int(price_max)
        f["price_krw"] = rng
    if extra: f.update(extra)
    return f

def _meta_to_text(md: Dict[str, Any]) -> str:
    brand = (md.get("brand") or "").strip()
    name  = (md.get("name") or "").strip()
    parts: List[str] = []
    if brand or name: parts.append(f"{brand} {name}".strip())
    for k, label in (("main_accords","메인 어코드"),("top_notes","탑 노트"),("middle_notes","미들 노트"),("base_notes","베이스 노트")):
        v = md.get(k)
        if isinstance(v, list) and v:
            parts.append(f"{label}: {', '.join(map(str, v))}")
    return " | ".join(parts) or (brand or name)

def search_corpus(query: str, filters: Optional[Dict[str, Any]] = None, top_k: int = TOPK_DEF) -> List[Dict[str, Any]]:
    vec = _embed(query)
    res = _index.query(vector=vec, top_k=top_k, include_metadata=True, namespace=NAMESPACE, filter=filters or {})
    out: List[Dict[str, Any]] = []
    for m in res.matches:
        md = dict(getattr(m, "metadata", {}) or {})
        out.append({"id": m.id, "score": float(m.score), "text": _meta_to_text(md), "metadata": md})
    return out

def extract_filters_from_query(query: str) -> Dict[str, Any]:
    notes = _extract_notes(query)
    brands = _extract_brands(query)
    pmin, pmax = _extract_price(query)
    return build_filters(notes=notes or None, brands=brands or None, price_min=pmin, price_max=pmax)

def _progressive_search(query: str, base_filters: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
    f = base_filters.copy()
    docs = search_corpus(query, filters=f, top_k=top_k)
    if docs:
        if ("brand" in f and STICKY_BRAND) or ("main_accords" in f and STICKY_NOTES) or (docs[0]["score"] >= MIN_SCORE):
            return docs
    f2 = base_filters.copy(); f2.pop("price_krw", None)
    docs = search_corpus(query, filters=f2, top_k=top_k)
    if docs:
        if ("brand" in f2 and STICKY_BRAND) or ("main_accords" in f2 and STICKY_NOTES) or (docs[0]["score"] >= MIN_SCORE):
            return docs
    f3 = f2.copy(); f3.pop("brand", None)
    docs = search_corpus(query, filters=f3, top_k=top_k)
    if docs and docs[0]["score"] >= MIN_SCORE:
        return docs
    f4 = f3.copy(); f4.pop("main_accords", None)
    docs = search_corpus(query, filters=f4, top_k=top_k)
    if docs and docs[0]["score"] >= MIN_SCORE:
        return docs
    return search_corpus(query, filters=None, top_k=top_k)

def rag_one_line(query: str, top_k: int = TOPK_DEF) -> str:
    f = extract_filters_from_query(query)
    docs = _progressive_search(query, f, top_k)
    if not docs:
        return "내 데이터에서 관련 결과를 찾지 못했어요. 질문을 조금 더 구체적으로 적어줄래?"
    ctx = "\n".join(d["text"] for d in docs[:5])
    sys = ("너는 향수 추천 보조자다. 제공된 문맥만 근거로 한국어 한 줄로만 답하라. "
           "최대 3개 제품을 '브랜드 제품명' 형태로 콤마로 구분하라. "
           "가격이나 불필요한 설명은 금지. 문맥에 없는 정보는 절대 추측하지 말라.")
    user = f"질문: {query}\n\n문맥:\n{ctx}\n\n한 줄로만."
    r = _client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role":"system","content":sys},{"role":"user","content":user}],
        temperature=0.2,
    )
    return r.choices[0].message.content.strip().replace("\n"," ")

if __name__ == "__main__":
    try:
        while True:
            q = input("질문> ").strip()
            if not q: continue
            print(rag_one_line(q))
    except KeyboardInterrupt:
        pass
