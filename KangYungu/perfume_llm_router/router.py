import os, re, json
from typing import Set, List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ALLOWED  = ["SCENT_INFO", "BRAND_INFO", "PRICE_INFO", "OTHER"]
PRIORITY = {"SCENT_INFO": 0, "BRAND_INFO": 1, "PRICE_INFO": 2, "OTHER": 3}

SCENT_KEYWORDS: Set[str] = {
    "시트러스","우디","파우더리","플로랄","머스크","바닐라","앰버","스파이시","레더","가죽","그린","프루티",
    "허브","코코넛","코튼","비누향","잔향","오드","우드","베르가못","패출리","시더","자스민",
    "상쾌","산뜻","상큼","시원","따뜻","달콤","쌉싸래","은은","진득","청결","깨끗","부드럽","무거운","가벼운",
    "봄","여름","가을","겨울","노트","분위기","무드",
    "향긋","향긋한","향기","향기로운","청량한","따스한","포근한","달달한","상큼한","프레시","프레시한","시원한",
    "따뜻한","부드러운","진한","가벼운","은은한","스모키","그루망","구르망","고소한","크리미","파우더","파우더리한"
}

BRANDS = [
    "톰포드","tom ford","조 말론","조말론","jo malone","딥티크","diptyque","샤넬","chanel","디올","dior","크리드","creed",
    "르 라보","르라보","le labo","바이레도","byredo","메종 마르지엘라","maison margiela","margiela",
    "입생로랑","yves saint laurent","ysl","구찌","gucci","프라다","prada","발렌티노","valentino",
    "버버리","burberry","에르메스","hermes","겔랑","guerlain","루이비통","louis vuitton","아르마니","armani",
    "조르지오 아르마니","giorgio armani","에스티 로더","estee lauder","estée lauder","캘빈클라인","calvin klein",
    "베르사체","versace","지방시","givenchy","몽블랑","montblanc","불가리","bvlgari","랑방","lanvin","자라","zara",
    "프레데릭 말","frédéric malle","frederic malle","랑콤","lancome","lancôme"
]
BRAND_FORMS = set()
for b in BRANDS:
    s = b.lower()
    BRAND_FORMS.update({s, s.replace(" ", ""), s.replace(" ", "-")})

PRICE_PATTERNS = [
    r"\d+\s*만원대", r"\d+\s*~\s*\d+\s*만원", r"\d+\s*만원",
    r"\d{2,}\s*원", r"\$\s*\d+", r"\d+\s*dollars?",
    r"가격|예산|비용|얼마|이하|이상|까지"
]

SYSTEM_PROMPT = """
너는 향수 도메인 라우터다. 사용자의 문장을 아래 INTENTS 중 복수로 분류한다.
가능한 값: SCENT_INFO, BRAND_INFO, PRICE_INFO, OTHER. 최소 1개는 포함한다.

규칙:
- SCENT_INFO: 향/노트/분위기/느낌 등 향 묘사 또는 “~한 향” 표현이 있으면 포함.
- BRAND_INFO: 브랜드명이 있으면 포함(한/영/띄어쓰기 변형 포함).
- PRICE_INFO: 금액/가격/예산/만원/달러/$/짜리/대/이하/이상/까지 등의 표현이 있으면 포함.
- 해당 없음이면 OTHER만.
- 오직 JSON: {"intents":["SCENT_INFO","BRAND_INFO"]}

주의:
- "향수" 단어만 있다고 SCENT_INFO로 분류하지 말 것.
- 향 묘사 또는 ~한 향 표현 향/노트/분위기/느낌 등이 있어야만 SCENT_INFO로 분류해야 됨.
""".strip()

def detect_price(text: str) -> bool:
    t = text
    if any(re.search(p, t) for p in PRICE_PATTERNS):
        return True
    t2 = t.lower().replace(" ", "")
    if ("짜리" in t2 or "대" in t2) and any(ch.isdigit() for ch in t2):
        return True
    return False

def detect_brand(text: str) -> bool:
    t = text.lower()
    t_nospace = t.replace(" ", "")
    t_hyphen  = t.replace(" ", "-")
    for form in BRAND_FORMS:
        if form in t or form in t_nospace or form in t_hyphen:
            return True
    return False

def detect_scent(text: str) -> bool:
    t = text or ""
    # 1) 명시적 향 키워드(우디/파우더리/포근한 등)
    if any(kw in t for kw in SCENT_KEYWORDS):
        return True

    # 2) "~한 향 / ~한 노트" (띄어쓰기 없어도 허용: "달달한향", "스모키한 향")
    if re.search(r"[가-힣A-Za-z]+\s*한\s*(향|노트)", t):
        return True

    # 3) "나무향/비누향/코튼향" 등 (단, '향수'는 제외)
    if re.search(r"(?!향수)[가-힣A-Za-z]+\s*향\b", t):
        return True

    # 4) "무슨/어떤 향"처럼 향 자체를 물어보는 질문
    if re.search(r"(무슨|어떤)\s*향", t):
        return True

    # --- 여기부터는 'SCENT 아님'을 강하게 판정하는 네거티브 룰 ---

    # 일반 "향수 추천/알려줘/찾아줘" 패턴은 SCENT 아님
    if re.search(r"향수\s*(추천|알려줘|찾아줘|추천해줘)", t):
        return False

    # 브랜드가 있고 향 묘사가 없으면 SCENT 아님
    if detect_brand(text):
        return False

    return False


def _llm_intents(question: str) -> List[str]:
    try:
        resp = client.chat.completions.create(
            model=os.getenv("ROUTER_MODEL", "gpt-4o-mini"),
            messages=[{"role":"system","content":SYSTEM_PROMPT},
                      {"role":"user","content":question}],
            temperature=0,
            response_format={"type":"json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        intents = data.get("intents", [])
        if not isinstance(intents, list):
            intents = [data.get("intent")] if data.get("intent") else []
        return [i for i in intents if i in ALLOWED]
    except Exception:
        return []

def classify_question(question: str) -> Dict[str, Any]:
    llm = _llm_intents(question)

    scent = detect_scent(question)
    brand = detect_brand(question)
    price = detect_price(question)

    heur: List[str] = []
    if scent: heur.append("SCENT_INFO")
    if brand: heur.append("BRAND_INFO")
    if price: heur.append("PRICE_INFO")
    if not heur and not llm:
        heur.append("OTHER")

    merged = list({*llm, *heur})
    merged = [i for i in merged if i in ALLOWED]

    # LLM이 SCENT라고 해도 휴리스틱이 아니라고 보면 제거
    if "SCENT_INFO" in merged and not scent:
        merged = [i for i in merged if i != "SCENT_INFO"]

    # 다른 라벨이 있으면 OTHER 제거
    if any(x for x in merged if x != "OTHER"):
        merged = [x for x in merged if x != "OTHER"]

    if not merged:
        merged = ["OTHER"]

    merged.sort(key=lambda x: PRIORITY.get(x, 99))
    return {
        "intents": merged,
        "signals": {"scent": bool(scent), "brand": bool(brand), "price": bool(price)}
    }


if __name__ == "__main__":
    try:
        while True:
            q = input("질문: ").strip()
            if not q: continue
            print(classify_question(q))
    except KeyboardInterrupt:
        pass
