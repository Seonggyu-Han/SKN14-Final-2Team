import os
import re
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from langchain_core.documents import Document

# =========================================
# .env 로드
# =========================================
load_dotenv()

# =========================================
# 유틸
# =========================================
def _norm(s: Any) -> str:
    s = "" if s is None else str(s)
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s

def make_stable_id(brand: str, name: str) -> str:
    """브랜드+이름 기반 안정적 ID"""
    base = f"{brand.strip()}::{name.strip()}".lower()
    hid = hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]
    return f"perfume_{hid}"

class PerfumeVectorUploader:
    def __init__(self):
        """Pinecone / OpenAI 초기화 & 설정"""
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        if not self.pinecone_api_key:
            raise ValueError("❌ PINECONE_API_KEY가 .env에 없습니다.")
        if not self.openai_api_key:
            raise ValueError("❌ OPENAI_API_KEY가 .env에 없습니다.")

        print("✅ 환경 변수 로드 완료")

        # Pinecone
        try:
            self.pc = Pinecone(api_key=self.pinecone_api_key)
            print("✅ Pinecone 클라이언트 초기화 완료")
        except Exception as e:
            raise ValueError(f"❌ Pinecone 초기화 실패: {e}")

        # OpenAI
        try:
            self.openai = OpenAI(api_key=self.openai_api_key)
            print("✅ OpenAI 클라이언트 초기화 완료")
        except Exception as e:
            raise ValueError(f"❌ OpenAI 초기화 실패: {e}")

        # ===== 설정 =====
        self.index_name = "perfume-vectordb"
        self.dimension = 1536
        self.embedding_model = "text-embedding-3-small"

        self.namespace = ""   # 필요 시 분리
        self.embed_batch_size = 128
        self.upsert_batch_size = 100

    # -------------------------------------
    # 인덱스 재생성 (존재하면 삭제 후 생성)
    # -------------------------------------
    def recreate_index(self) -> None:
        try:
            names = [idx.name for idx in self.pc.list_indexes()]
            if self.index_name in names:
                print(f"🧨 인덱스 '{self.index_name}' 삭제 중...")
                self.pc.delete_index(self.index_name)

            print(f"🔨 인덱스 '{self.index_name}' 생성 중...")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            print(f"✅ 인덱스 '{self.index_name}' 생성 완료")
            self.wait_until_ready()
        except Exception as e:
            raise ValueError(f"❌ 인덱스 재생성 실패: {e}")

    def wait_until_ready(self, timeout_sec: int = 10, interval_sec: float = 1.0) -> None:
        """
        인덱스가 ready 될 때까지 짧게 폴링.
        - 기본: 최대 10초 동안 1초 간격으로 확인
        - 그 이후에는 강제로 진행
        """
        print(f"⏳ 인덱스 준비 상태 확인 중...(최대 {timeout_sec}초)")
        start = time.time()
        while True:
            try:
                desc = self.pc.describe_index(self.index_name)
                status = getattr(desc, "status", {}) or {}
                ready = False
                if isinstance(status, dict):
                    ready = bool(status.get("ready")) or (status.get("state") == "Ready")
                if ready:
                    print("✅ 인덱스 준비 완료")
                    return
            except Exception:
                pass
            if time.time() - start > timeout_sec:
                print("⚠️ 준비 확인 타임아웃 → 강제 진행")
                return
            time.sleep(interval_sec)

    # -------------------------------------
    # CSV → Document
    # -------------------------------------
    def parse_score_string(self, score_str: str) -> Optional[str]:
        if pd.isna(score_str) or not str(score_str).strip() or str(score_str).lower() == "nan":
            return None
        try:
            s = str(score_str).strip()
            scores: Dict[str, float] = {}
            if "(" in s and ")" in s:
                pattern = r"(\w+)\s*\(\s*([\d.]+)\s*\)"
                for key, val in re.findall(pattern, s):
                    try:
                        scores[key.strip()] = float(val.strip())
                    except ValueError:
                        continue
            elif s.startswith("{") and s.endswith("}"):
                try:
                    d = json.loads(s)
                    for k, v in d.items():
                        if isinstance(v, str):
                            cv = v.replace("%", "").strip()
                            if cv:
                                scores[str(k)] = float(cv)
                        elif isinstance(v, (int, float)):
                            scores[str(k)] = float(v)
                except json.JSONDecodeError:
                    pass
            return max(scores, key=scores.get) if scores else None
        except Exception:
            return None

    def csv_to_documents(self, csv_path: str) -> List[Document]:
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")

        print(f"📖 CSV 로딩: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"📊 행 {len(df)}개")

        docs: List[Document] = []
        for _, row in tqdm(df.iterrows(), total=len(df), desc="🔄 Document 생성"):
            description = str(row.get("description", "")).strip()
            if not description or description.lower() == "nan":
                continue

            season_top   = self.parse_score_string(str(row.get("season_score", "")))
            daynight_top = self.parse_score_string(str(row.get("day_night_score", "")))

            brand = _norm(row.get("brand", ""))
            name  = _norm(row.get("name", ""))

            meta: Dict[str, Any] = {
                "id": make_stable_id(brand, name),
                "brand": brand,
                "name": name,
                "concentration": _norm(row.get("concentration", "")),
                "gender": _norm(row.get("gender", "")),
                "sizes": _norm(row.get("sizes", "")),
            }
            if season_top:   meta["season_score"] = season_top
            if daynight_top: meta["day_night_score"] = daynight_top

            docs.append(Document(page_content=description, metadata=meta))

        print(f"✅ Document {len(docs)}개 생성 완료")
        return docs

    def show_sample_documents(self, documents: List[Document], n: int = 3) -> None:
        print("\n" + "=" * 80)
        print("📋 Document 샘플")
        print("=" * 80)
        for i in range(min(n, len(documents))):
            d = documents[i]
            print(f"\n[{i+1}] ID: {d.metadata['id']}")
            print(f"page_content: {d.page_content[:300]}")
            print(f"metadata keys: {list(d.metadata.keys())}")
            print("-" * 60)
        print("=" * 80 + "\n")

    # -------------------------------------
    # 배치 임베딩
    # -------------------------------------
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        resp = self.openai.embeddings.create(model=self.embedding_model, input=texts)
        return [item.embedding for item in resp.data]

    def documents_to_vectors_batched(self, docs: List[Document]) -> List[Dict]:
        vectors: List[Dict] = []
        print(f"🔄 임베딩(배치) 생성: batch={self.embed_batch_size}")
        for i in tqdm(range(0, len(docs), self.embed_batch_size), desc="🧮 임베딩 배치"):
            batch_docs = docs[i : i + self.embed_batch_size]
            texts = [d.page_content for d in batch_docs]
            try:
                embs = self.embed_batch(texts)
                for d, emb in zip(batch_docs, embs):
                    meta = dict(d.metadata)
                    meta["text"] = d.page_content
                    vectors.append({"id": meta["id"], "values": emb, "metadata": meta})
            except Exception as e:
                print(f"⚠️ 임베딩 배치 실패 (i={i}): {e}")
                continue
        print(f"✅ 벡터 {len(vectors)}개 생성 완료")
        return vectors

    # -------------------------------------
    # 업서트(배치)
    # -------------------------------------
    def upsert_vectors_batched(self, vectors: List[Dict]) -> Tuple[int, int]:
        if not vectors:
            return 0, 0
        index = self.pc.Index(self.index_name)
        ok, ng = 0, 0
        calls = 0
        print(f"📤 업서트(배치): batch={self.upsert_batch_size}")
        for i in tqdm(range(0, len(vectors), self.upsert_batch_size), desc="📦 업서트(batched)"):
            batch = vectors[i : i + self.upsert_batch_size]
            try:
                res = index.upsert(vectors=batch, namespace=self.namespace)
                calls += 1
                if hasattr(res, "upserted_count") and isinstance(res.upserted_count, int):
                    ok += res.upserted_count
                else:
                    ok += len(batch)
            except Exception as e:
                ng += len(batch)
                print(f"⚠️ 업서트 실패 (i={i}): {e}")
                continue
            print(f"   ↳ call#{calls} batch_size={len(batch)} (누적 성공={ok}, 실패={ng})")
            time.sleep(0.15)
        print(f"📞 업서트 호출수: {calls}")
        return ok, ng

    # -------------------------------------
    # 실행
    # -------------------------------------
    def run(self, csv_path: str) -> None:
        print("🚀 Perfume 벡터 업로드 시작!\n")

        # (1) 인덱스 재생성: 존재하면 삭제 → 새로 생성
        self.recreate_index()

        # (2) CSV→Documents
        docs = self.csv_to_documents(csv_path)
        if not docs:
            print("❌ 변환할 문서가 없습니다.")
            return
        self.show_sample_documents(docs)

        # (3) Documents→Vectors (배치 임베딩)
        vectors = self.documents_to_vectors_batched(docs)
        if not vectors:
            print("❌ 생성할 벡터가 없습니다.")
            return

        # (4) Upsert (배치)
        ok, ng = self.upsert_vectors_batched(vectors)
        print(f"✅ 업서트 완료 | 성공: {ok}  실패: {ng}")

        # (5) 최종 통계
        try:
            idx = self.pc.Index(self.index_name)
            stats = idx.describe_index_stats()
            after = stats.get("total_vector_count", 0)
            print(f"\n📊 최종 벡터 수: {after}")
        except Exception as e:
            print(f"⚠️ 최종 통계 조회 실패: {e}")

        print("🎉 완료!")

# =========================================
# 메인
# =========================================
def main():
    csv_file = "perfume_final.csv"
    try:
        app = PerfumeVectorUploader()
        app.run(csv_file)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
