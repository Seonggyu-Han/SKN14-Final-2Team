import os
import re
import time
import uuid
import argparse
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, PineconeApiException

MODEL = "text-embedding-3-small"
EMBED_DIM = 1536

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CSV_PATH = str((BASE_DIR / "dataset" / "perfume_final.csv").resolve())
DEFAULT_INDEX = "perfume-rag"
DEFAULT_NAMESPACE = "catalog"
DEFAULT_BATCH = 128

def clean_int(x):
    if not x:
        return None
    s = re.sub(r"[^\d]", "", str(x))
    return int(s) if s else None

def split_list(x) -> List[str]:
    if not x:
        return []
    parts = re.split(r"[\/,;·•\|\n]+|\s-\s|\s–\s|\s—\s", str(x))
    seen, out = set(), []
    for p in (p.strip().lower() for p in parts if p and p.strip()):
        if p not in seen:
            seen.add(p); out.append(p)
    return out

def normalize_brand(x):
    return str(x).strip().lower() if x else None

def normalize_name(x):
    return str(x).strip() if x else None

def normalize_concentration(raw):
    if not raw:
        return None
    s = str(raw).strip().lower()
    if "extrait" in s: return "extrait de parfum"
    if "edp" in s or "eau de parfum" in s or "parfum" in s: return "eau de parfum"
    if "edt" in s or "toilette" in s: return "eau de toilette"
    if "cologne" in s or "edc" in s: return "eau de cologne"
    return s

def backoff_sleep(attempt: int):
    time.sleep(min(2 ** attempt, 30))

def load_and_prepare(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False, encoding="utf-8-sig")

    def get(col):
        return df[col] if col in df.columns else pd.Series([""] * len(df))

    brand = get("brand")
    name = get("name")
    size_ml = get("size_ml")
    price_krw = get("price_krw")
    description = get("description")
    conc_raw = get("부향률")
    accords = get("메인 어코드")
    top_notes = get("탑 노트")
    middle_notes = get("미들 노트")
    base_notes = get("베이스 노트")
    desc_ko = get("향 설명")

    rows = []
    for i in range(len(df)):
        b  = normalize_brand(brand.iloc[i])
        n  = normalize_name(name.iloc[i])
        sz = clean_int(size_ml.iloc[i])
        pr = clean_int(price_krw.iloc[i])
        conc = normalize_concentration(conc_raw.iloc[i])

        mac = split_list(accords.iloc[i])
        tn  = split_list(top_notes.iloc[i])
        mn  = split_list(middle_notes.iloc[i])
        bn  = split_list(base_notes.iloc[i])

        desc_en = description.iloc[i].strip() if description.iloc[i] else ""
        desc_k  = desc_ko.iloc[i].strip() if desc_ko.iloc[i] else ""

        text_parts = []
        if desc_k: text_parts.append(desc_k)
        if desc_en: text_parts.append(desc_en)
        if mac: text_parts.append("메인 어코드: " + ", ".join(mac))
        if tn:  text_parts.append("탑 노트: " + ", ".join(tn))
        if mn:  text_parts.append("미들 노트: " + ", ".join(mn))
        if bn:  text_parts.append("베이스 노트: " + ", ".join(bn))
        if b or n: text_parts.append(f"브랜드 {b or ''} 제품명 {n or ''}".strip())
        text = " | ".join([p for p in text_parts if p]) or (n or b or "")
        if not text.strip():
            continue
        metadata = {
            "brand": b,
            "name": n,
            "size_ml": sz,
            "price_krw": pr,
            "concentration": conc,
            "main_accords": mac,
            "top_notes": tn,
            "middle_notes": mn,
            "base_notes": bn,
        }
        metadata = {k: v for k, v in metadata.items()
                    if v is not None and not (isinstance(v, list) and len(v) == 0)}

        rows.append({
            "id": str(uuid.uuid4()),
            "text": text,
            "metadata": metadata
        })

    return pd.DataFrame(rows)

def embed_batch(client: OpenAI, texts: List[str]) -> List[List[float]]:
    attempt = 0
    while True:
        try:
            resp = client.embeddings.create(model=MODEL, input=texts)
            return [d.embedding for d in resp.data]
        except Exception as e:
            attempt += 1
            print(f"[OpenAI] retry {attempt}: {e}")
            backoff_sleep(attempt)

def upsert_batch(index, vectors: List[Dict[str, Any]], namespace: str):
    attempt = 0
    while True:
        try:
            index.upsert(vectors=vectors, namespace=namespace)
            return
        except PineconeApiException as e:
            attempt += 1
            print(f"[Pinecone] retry {attempt}: {e}")
            backoff_sleep(attempt)
        except Exception as e:
            attempt += 1
            print(f"[Pinecone] retry {attempt}: {e}")
            backoff_sleep(attempt)

def main():
    load_dotenv()

    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=DEFAULT_CSV_PATH, help="CSV file path")
    ap.add_argument("--index", default=DEFAULT_INDEX, help="Pinecone index name")
    ap.add_argument("--namespace", default=DEFAULT_NAMESPACE, help="Pinecone namespace")
    ap.add_argument("--batch", type=int, default=DEFAULT_BATCH, help="Batch size")
    ap.add_argument("--dryrun", action="store_true", help="Show first 3 items and exit")
    args = ap.parse_args()

    oa_key = os.getenv("OPENAI_API_KEY")
    pc_key = os.getenv("PINECONE_API_KEY")
    if not oa_key or not pc_key:
        raise RuntimeError("OPENAI_API_KEY / PINECONE_API_KEY가 환경변수(.env)에 없습니다.")

    oa = OpenAI(api_key=oa_key)
    pc = Pinecone(api_key=pc_key)
    index = pc.Index(args.index)

    df = load_and_prepare(args.csv)
    if df.empty:
        raise RuntimeError("유효한 행이 없습니다. CSV 컬럼/값을 확인하세요.")

    if args.dryrun:
        print("[Dry-run] first 3 rows:")
        print(df.head(3).to_dict(orient="records"))
        print(f"[info] CSV: {args.csv}")
        print(f"[info] Index: {args.index}, Namespace: {args.namespace}, Batch: {args.batch}")
        return

    print(f"Uploading {len(df)} rows → index='{args.index}', namespace='{args.namespace}'")
    print(f"[info] CSV: {args.csv}")

    B = args.batch
    for s in range(0, len(df), B):
        e = min(s + B, len(df))
        chunk = df.iloc[s:e]

        embeddings = embed_batch(oa, chunk["text"].tolist())
        vectors = []
        for (rid, md), emb in zip(chunk[["id","metadata"]].to_records(index=False), embeddings):
            vectors.append({"id": rid, "values": emb, "metadata": md})

        upsert_batch(index, vectors, args.namespace)
        print(f"Upserted {e}/{len(df)}")

    print("Done.")

if __name__ == "__main__":
    main()