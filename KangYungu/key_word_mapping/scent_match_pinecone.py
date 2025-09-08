import os, re
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

EMBED_MODEL = os.getenv("EMBED_MODEL","text-embedding-3-small")
INDEX_NAME  = os.getenv("PINECONE_INDEX","perfume-keywords")
NAMESPACE   = os.getenv("PINECONE_NAMESPACE","keywords")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(INDEX_NAME)

def _embed(t:str)->List[float]:
    return client.embeddings.create(model=EMBED_MODEL, input=t).data[0].embedding

def _norm_cats(c):
    if not c: return []
    if isinstance(c,list): return [str(x).strip() for x in c if str(x).strip()]
    if isinstance(c,str): return [s.strip() for s in re.split(r"[,\|/;]+", c) if s.strip()]
    return [str(c).strip()]

def _norm_note(n:str)->str:
    n = (n or "").strip()
    return n[:-1] if n.endswith("향") else n

def match_note(q:str, top_k:int=3, pre_k:int=300)->List[Dict[str,Any]]:
    vec = _embed(q)
    res = index.query(
        vector=vec,
        top_k=pre_k,
        include_metadata=True,
        namespace=NAMESPACE,
        filter={"type": {"$eq": "keyword_token"}},
    )
    agg: Dict[str,float] = {}
    for m in res.matches:
        md = dict(getattr(m,"metadata",{}) or {})
        note = md.get("canonical_note")
        if not note: continue
        cats = _norm_cats(md.get("categories"))
        w = 1.15 if "노트" in cats else 1.0
        s = float(m.score) * w
        n = _norm_note(note)
        if s > agg.get(n, 0.0):
            agg[n] = s
    return [{"note":k, "score":v} for k,v in sorted(agg.items(), key=lambda x:x[1], reverse=True)[:top_k]]

if __name__ == "__main__":
    try:
        while True:
            q = input("질문: ").strip()
            if not q: continue
            res = match_note(q, top_k=3)
            if not res:
                print("(노트 결과 없음)")
            else:
                for r in res:
                    print(f"{r['note']} (유사도: {r['score']:.2f})")
    except KeyboardInterrupt:
        pass
