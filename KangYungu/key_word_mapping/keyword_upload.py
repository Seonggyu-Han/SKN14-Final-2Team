import os
import re
import csv
import argparse
import hashlib
from typing import Dict, List, Set, Tuple

from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, PineconeApiException

EMBED_MODEL = "text-embedding-3-small"
EMBED_DIM = 1536
HERE = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(HERE)
DEFAULT_CSV = os.path.join(BASE_DIR, "dataset", "key_word.csv")
DEFAULT_INDEX = "perfume-keywords"
DEFAULT_NAMESPACE = "keywords"

COLUMNS = [
    "노트", "향/재료", "색상/이미지", "계절", "온도/습도",
    "날씨", "시간대", "장소/상황", "감정/분위기"
]

_SPLIT_RE = re.compile(r"[\/,;·•\|\n]+|\s-\s|\s–\s|\s—\s|,")

def split_tokens(cell: str) -> List[str]:
    if not cell:
        return []
    parts = _SPLIT_RE.split(str(cell))
    out, seen = [], set()
    for p in (p.strip() for p in parts):
        if not p:
            continue
        t = p
        if t not in seen:
            seen.add(t); out.append(t)
    return out

def load_token_note_pairs(path: str) -> List[Tuple[str, str, Set[str]]]:
    pairs_map: Dict[Tuple[str, str], Set[str]] = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            notes = split_tokens(row.get("노트", ""))
            if not notes:
                continue
            for col in COLUMNS:
                toks = split_tokens(row.get(col, ""))
                if not toks:
                    continue
                for tok in toks:
                    for note in notes:
                        key = (tok.strip(), note.strip())
                        if not key[0] or not key[1]:
                            continue
                        pairs_map.setdefault(key, set()).add(col)
    return [(k[0], k[1], v) for k, v in pairs_map.items()]

def embed_texts_unique(client: OpenAI, texts: List[str], batch: int = 256) -> Dict[str, List[float]]:
    uniq = list(dict.fromkeys(texts))
    vecs: Dict[str, List[float]] = {}
    for i in range(0, len(uniq), batch):
        chunk = uniq[i:i+batch]
        resp = client.embeddings.create(model=EMBED_MODEL, input=chunk)
        for t, d in zip(chunk, resp.data):
            vecs[t] = d.embedding
    return vecs

def stable_id(token: str, note: str) -> str:
    h = hashlib.md5(f"{token}|{note}".encode("utf-8")).hexdigest()[:16]
    return f"kw3-{h}"

def build_vectors(oa: OpenAI, pairs: List[Tuple[str, str, Set[str]]]) -> List[dict]:
    tokens = [t for t, _, _ in pairs]
    t2v = embed_texts_unique(oa, tokens)
    vecs = []
    for token, note, cats in pairs:
        vecs.append({
            "id": stable_id(token, note),
            "values": t2v[token],
            "metadata": {
                "type": "keyword_token",
                "label": token,
                "canonical_note": note,
                "categories": sorted(list(cats)),
                "source": "key_word.csv"
            }
        })
    return vecs

def upsert(index, vectors: List[dict], namespace: str, batch: int = 200):
    for i in range(0, len(vectors), batch):
        part = vectors[i:i+batch]
        index.upsert(vectors=part, namespace=namespace)

def main():
    load_dotenv()

    ap = argparse.ArgumentParser(description="Upload token×note keyword vectors to Pinecone")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="Path to dataset/key_word.csv")
    ap.add_argument("--index", default=DEFAULT_INDEX, help="Pinecone index name")
    ap.add_argument("--namespace", default=DEFAULT_NAMESPACE, help="Pinecone namespace (e.g., keywords)")
    ap.add_argument("--batch", type=int, default=200, help="Upsert batch size")
    ap.add_argument("--dryrun", action="store_true", help="Preview only")
    args = ap.parse_args()

    oa_key = os.getenv("OPENAI_API_KEY")
    pc_key = os.getenv("PINECONE_API_KEY")
    if not oa_key or not pc_key:
        raise RuntimeError("OPENAI_API_KEY / PINECONE_API_KEY가 .env에 없습니다.")

    pairs = load_token_note_pairs(args.csv)
    if not pairs:
        raise RuntimeError(f"No token-note pairs found in {args.csv}")

    oa = OpenAI(api_key=oa_key)
    pc = Pinecone(api_key=pc_key)
    idx = pc.Index(args.index)

    vecs = build_vectors(oa, pairs)

    if args.dryrun:
        print(f"[Dry-run] total pairs = {len(vecs)}")
        for v in vecs[:8]:
            meta = dict(v["metadata"]); meta["values_dim"] = len(v["values"])
            print({"id": v["id"], **meta})
        return

    try:
        upsert(idx, vecs, args.namespace, batch=args.batch)
        print(f"Uploaded {len(vecs)} vectors to index='{args.index}', namespace='{args.namespace}'")
    except PineconeApiException as e:
        print("Pinecone error:", e)
        raise

if __name__ == "__main__":
    main()
