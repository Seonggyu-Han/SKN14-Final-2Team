import os
import re
import time
import hashlib
from typing import Any, List, Tuple, Dict

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from langchain_core.documents import Document

# .env 로드
load_dotenv()

# ------------------------------
# 유틸
# ------------------------------
def _norm(s: Any) -> str:
    """공백/소문자/트림/내부공백 정규화."""
    s = "" if s is None else str(s)
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s

def make_stable_id_from_content(content: str) -> str:
    """내용 문자열에서 안정적 벡터 ID 생성 (SHA1 20자)."""
    digest = hashlib.sha1(content.encode("utf-8")).hexdigest()[:20]
    return f"keyword_{digest}"

class KeywordVectorUploader:
    def __init__(self):
        """Pinecone / OpenAI 초기화 + 기본 설정."""
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

        # 설정
        self.index_name = "keyword-vectordb"
        self.dimension = 1536
        self.embedding_model = "text-embedding-3-small"
        self.namespace = ""  # 필요 시 분리 사용
        # 배치 크기
        self.embed_batch_size = 128
        self.upsert_batch_size = 100

    # ------------------------------
    # 인덱스 재생성 (있으면 삭제 → 새로 생성)
    # ------------------------------
    def recreate_index(self) -> None:
        """인덱스가 존재하면 삭제하고 동일 스펙으로 재생성."""
        try:
            names = [idx.name for idx in self.pc.list_indexes()]
            if self.index_name in names:
                print(f"🗑️ 기존 인덱스 '{self.index_name}' 삭제 중...")
                self.pc.delete_index(self.index_name)
                time.sleep(2)
                print("✅ 기존 인덱스 삭제 완료")
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
        """인덱스가 ready 될 때까지 폴링 (최대 10초)."""
        print(f"⏳ 인덱스 준비 상태 확인 중 (최대 {timeout_sec}초)...")
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
                print("⚠️ 준비 확인 타임아웃 도달(계속 진행)")
                return
            time.sleep(interval_sec)

    # ------------------------------
    # CSV → Document 리스트
    # ------------------------------
    def create_key_value_content(self, row: pd.Series, columns: List[str]) -> str:
        """모든 컬럼을 key:value 형태로 이어붙인 content 생성."""
        parts = []
        for col in columns:
            val = row.get(col, "")
            if pd.isna(val):
                continue
            sval = str(val).strip()
            if not sval or sval.lower() == "nan":
                continue
            parts.append(f"{col}: {sval}")
        return " | ".join(parts)

    def csv_to_documents(self, csv_path: str) -> List[Document]:
        """CSV를 LangChain Document 배열로 변환 (안정적 ID 포함)."""
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        print(f"📖 CSV 로딩: {csv_path}")
        df = pd.read_csv(csv_path)
        cols = df.columns.tolist()
        print(f"📊 행 {len(df)}개, 컬럼 {len(cols)}개")
        print(f"📝 컬럼: {cols}")

        docs: List[Document] = []
        for _, row in tqdm(df.iterrows(), total=len(df), desc="🔄 Document 생성"):
            content = self.create_key_value_content(row, cols)
            if not content.strip():
                continue
            rid = make_stable_id_from_content(_norm(content))
            docs.append(Document(page_content=content, metadata={"id": rid}))
        print(f"✅ Document {len(docs)}개 생성 완료")
        return docs

    def show_sample_documents(self, documents: List[Document], n: int = 3) -> None:
        print("\n" + "=" * 80)
        print("📋 Document 샘플")
        print("=" * 80)
        for i in range(min(n, len(documents))):
            d = documents[i]
            print(f"\n[{i+1}] ID: {d.metadata['id']}")
            print(f"Content: {d.page_content[:300]}")
            print("-" * 60)
        print("=" * 80 + "\n")

    # ------------------------------
    # 배치 임베딩
    # ------------------------------
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        resp = self.openai.embeddings.create(model=self.embedding_model, input=texts)
        return [item.embedding for item in resp.data]  # 순서 보장

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
                    # Pinecone 콘솔에서 text 확인 가능하게 추가
                    meta["text"] = d.page_content
                    vectors.append({
                        "id": meta["id"],
                        "values": emb,
                        "metadata": meta
                    })
            except Exception as e:
                print(f"⚠️ 임베딩 배치 실패 (i={i}): {e}")
                continue
        print(f"✅ 벡터 {len(vectors)}개 생성 완료")
        return vectors

    # ------------------------------
    # 업서트(배치)
    # ------------------------------
    def upsert_vectors_batched(self, vectors: List[Dict]) -> Tuple[int, int]:
        if not vectors:
            return 0, 0
        index = self.pc.Index(self.index_name)
        ok, ng = 0, 0
        print(f"📤 업서트(배치): batch={self.upsert_batch_size}")
        for i in tqdm(range(0, len(vectors), self.upsert_batch_size), desc="📦 업서트"):
            batch = vectors[i : i + self.upsert_batch_size]
            try:
                res = index.upsert(vectors=batch, namespace=self.namespace)
                if hasattr(res, "upserted_count") and isinstance(res.upserted_count, int):
                    ok += res.upserted_count
                else:
                    ok += len(batch)
                time.sleep(0.2)  # 레이트리밋 여유
            except Exception as e:
                ng += len(batch)
                print(f"⚠️ 업서트 실패 (i={i}): {e}")
                continue
        return ok, ng

    # ------------------------------
    # 메인 플로우 (인덱스 재생성 후 전량 적재)
    # ------------------------------
    def run(self, csv_path: str) -> None:
        print("🚀 Keyword 벡터 업로드 시작! (인덱스 재생성)\n")
        # 1) 인덱스 재생성 (있으면 삭제 → 새로 생성)
        self.recreate_index()
        index = self.pc.Index(self.index_name)

        # 2) CSV → Documents
        docs = self.csv_to_documents(csv_path)
        if not docs:
            print("❌ 변환할 문서가 없습니다.")
            return
        self.show_sample_documents(docs)

        # 3) Documents → Vectors (배치 임베딩)
        vectors = self.documents_to_vectors_batched(docs)
        if not vectors:
            print("❌ 생성할 벡터가 없습니다.")
            return

        # 4) 모든 벡터 업서트
        ok, ng = self.upsert_vectors_batched(vectors)
        print(f"✅ 업서트 완료 | 성공: {ok}  실패: {ng}")

        # 5) 최종 통계
        try:
            stats = index.describe_index_stats()
            after = stats.get("total_vector_count", 0)
            print(f"\n📊 최종 벡터 수: {after}")
        except Exception as e:
            print(f"⚠️ 최종 통계 조회 실패: {e}")

        print("🎉 완료!")

def main():
    csv_file = "keyword_dictionary_final.csv"
    try:
        app = KeywordVectorUploader()
        app.run(csv_file)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
