from pathlib import Path
import sys, os, json

# 0) sys.path: 프로젝트 루트 + KangYungu
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
KG = ROOT / "KangYungu"
if KG.exists() and str(KG) not in sys.path:
    sys.path.insert(0, str(KG))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

def _fmt(obj) -> str:
    try:    return json.dumps(obj, ensure_ascii=False, indent=2)
    except: return str(obj)

# 1) router
try:
    from KangYungu.perfume_llm_router.router import classify_question
except Exception:
    from perfume_llm_router.router import classify_question

# 2) note 매핑 (pinecone 우선 → 키워드 대체)
match_note = None
try:
    from KangYungu.key_word_mapping.scent_match_pinecone import match_note as _mn
    match_note = _mn
except Exception:
    try:
        from key_word_mapping.scent_match_pinecone import match_note as _mn
        match_note = _mn
    except Exception:
        try:
            from KangYungu.key_word_mapping.scent_match import match_note as _mn
            match_note = _mn
        except Exception:
            try:
                from key_word_mapping.scent_match import match_note as _mn
                match_note = _mn
            except Exception:
                match_note = None

# 3) 검색 유틸
try:
    from KangYungu.perfume_vdb.vdb_llm.search import (
        search_corpus, build_filters, extract_filters_from_query,
        MIN_SCORE as _MIN_SCORE, TOPK_DEF as _TOPK_DEF,
    )
except Exception:
    try:
        from KangYungu.search import (
            search_corpus, build_filters, extract_filters_from_query,
            MIN_SCORE as _MIN_SCORE, TOPK_DEF as _TOPK_DEF,
        )
    except Exception:
        try:
            from perfume_vdb.vdb_llm.search import (
                search_corpus, build_filters, extract_filters_from_query,
                MIN_SCORE as _MIN_SCORE, TOPK_DEF as _TOPK_DEF,
            )
        except Exception:
            from search import (
                search_corpus, build_filters, extract_filters_from_query,
                MIN_SCORE as _MIN_SCORE, TOPK_DEF as _TOPK_DEF,
            )

MIN_SCORE   = float(os.getenv("RAG_MIN_SCORE", str(_MIN_SCORE)))
TOPK_DEF    = int(os.getenv("RAG_TOPK", str(_TOPK_DEF)))
STICKY_MIN  = float(os.getenv("RAG_STICKY_MIN", "0.25"))  # 노트/브랜드 있으면 임계 완화

# ---------- 유틸 ----------
def _to_text(d):
    if isinstance(d, dict):
        for k in ("text", "content", "chunk", "page_text", "body"):
            if k in d and isinstance(d[k], str):
                return d[k]
    return str(d)

def _merge_filters(base: dict | None, extra: dict | None) -> dict:
    b = dict(base or {})
    e = dict(extra or {})
    if not e: return b
    for k, v in e.items():
        if k not in b:
            b[k] = v; continue
        if k in ("brand", "main_accords"):
            if isinstance(b[k], dict) and "$in" in b[k] and isinstance(v, dict) and "$in" in v:
                b[k]["$in"] = list(dict.fromkeys(list(b[k]["$in"]) + list(v["$in"])))
            else:
                b[k] = v
        elif k == "price_krw":
            rng1 = b.get("price_krw", {}); rng2 = v or {}
            gte = max(rng1.get("$gte", -10**15), rng2.get("$gte", -10**15))
            lte = min(rng1.get("$lte",  10**15), rng2.get("$lte",  10**15))
            out = {}
            if gte != -10**15: out["$gte"] = int(gte)
            if lte !=  10**15: out["$lte"] = int(lte)
            b["price_krw"] = out if out else {}
        else:
            b[k] = v
    return b

def _progressive_search(query: str, base_filters: dict | None, top_k: int):
    """여러 단계 필터 완화. (docs, applied_filters, stage_name) 반환
       ※ 로그는 모두 제거(의도/노트만 찍기 위해)"""
    def _try(stage: str, f: dict | None):
        docs = search_corpus(query, filters=f, top_k=top_k)
        return docs, f, stage

    f = dict(base_filters or {})
    d, af, st = _try("full", f)
    if d and (d[0]["score"] >= MIN_SCORE or "brand" in f or "main_accords" in f):
        return d, af, st

    f2 = dict(f); f2.pop("price_krw", None)
    d, af, st = _try("no-price", f2)
    if d and (d[0]["score"] >= MIN_SCORE or "brand" in f2 or "main_accords" in f2):
        return d, af, st

    f3 = dict(f2); f3.pop("brand", None)
    d, af, st = _try("no-brand", f3)
    if d and d[0]["score"] >= MIN_SCORE:
        return d, af, st

    f4 = dict(f3); f4.pop("main_accords", None)
    d, af, st = _try("no-notes", f4)
    if d and d[0]["score"] >= MIN_SCORE:
        return d, af, st

    d, af, st = _try("no-filter", {})
    return d, af, st

def _dedup_keep_order(xs):
    seen = set(); out = []
    for x in xs:
        if not x: continue
        if x not in seen:
            seen.add(x); out.append(x)
    return out

def _names_from_docs(docs, limit=3) -> str:
    names = []
    for d in (docs or []):
        md = (d.get("metadata") or {})
        n = md.get("name")
        if n: names.append(str(n).strip())
    names = _dedup_keep_order(names)
    if not names:
        # fallback: text의 첫 구간 사용(브랜드 포함될 수 있음)
        for d in (docs or []):
            t = (d.get("text") or "").split(" | ", 1)[0].strip()
            if t: names.append(t)
        names = _dedup_keep_order(names)
    return ", ".join(names[:limit]) if names else ""

def _pick_better(a, b):
    """(docs, filters, stage, used_query_label) 2개 중 더 좋은 쪽 선택"""
    if a is None: return b
    if b is None: return a
    ad, _, _, _ = a; bd, _, _, _ = b
    if not ad: return b
    if not bd: return a
    if ad[0]["score"] != bd[0]["score"]:
        return a if ad[0]["score"] > bd[0]["score"] else b
    return a if len(ad) >= len(bd) else b

# ---------- 메인 ----------
def answer_query(query: str) -> str:
    info = classify_question(query)
    intents = info.get("intents", [])

    # (요구사항) 의도만 출력
    print(f"intents = {intents}")

    base_f = extract_filters_from_query(query)

    used = None

    # SCENT면 노트 매핑(요구사항) → 매칭된 메인어코드만 출력
    if "SCENT_INFO" in intents and match_note is not None:
        try:
            raw_notes = match_note(query, top_k=5) or []
            notes = [n["note"] for n in raw_notes[:3] if n.get("note")]
        except Exception:
            notes = []

        print(f"matched_main_accords = {notes}")

        note_f = build_filters(notes=notes) if notes else {}
        merged_f = _merge_filters(base_f, note_f)

        if notes:
            aug_q = f"{query} 메인 어코드: {', '.join(notes)}"
            d1, af1, st1 = _progressive_search(aug_q, merged_f, TOPK_DEF)
            used = (d1, af1, st1, "augmented")

        d2, af2, st2 = _progressive_search(query, merged_f, TOPK_DEF)
        cand2 = (d2, af2, st2, "original")
        used = _pick_better(used, cand2)
    else:
        d, af, st = _progressive_search(query, base_f, TOPK_DEF)
        used = (d, af, st, "original")

    docs, applied_filters, stage, label = used

    if not docs:
        return "내 데이터에서 관련 결과를 충분히 찾지 못했어. 질문을 조금 더 구체적으로 적어줄래?"

    top = docs[0]["score"]
    has_sticky = isinstance(applied_filters, dict) and (
        ("brand" in applied_filters) or ("main_accords" in applied_filters)
    )
    threshold = STICKY_MIN if has_sticky else MIN_SCORE
    if top < threshold:
        return "내 데이터에서 관련 결과를 충분히 찾지 못했어. 질문을 조금 더 구체적으로 적어줄래?"

    # (요구사항) 최종 출력: "향수 이름"만, 콤마 구분
    return _names_from_docs(docs, limit=3)

if __name__ == "__main__":
    try:
        while True:
            q = input("질문> ").strip()
            if not q: continue
            print(answer_query(q))
    except KeyboardInterrupt:
        pass
