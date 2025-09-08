# function.py
import requests
import re
import os
from dotenv import load_dotenv
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from openai import OpenAI
from langgraph import State, StateNode, StateEdge

# === .env 불러오기 ===
load_dotenv()
naver_client_id = os.getenv("NAVER_CLIENT_ID")
naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")

@tool
def price_tool(user_query: str) -> str:
    """A tool that uses the Naver Shopping API to look up perfume prices (results are returned as formatted strings)"""
    
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": naver_client_id,
        "X-Naver-Client-Secret": naver_client_secret
    }
    params = {"query": user_query, "display": 5, "sort": "sim"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
    except Exception as e:
        return f"❌ 요청 오류: {e}"
    
    if response.status_code != 200:
        return f"❌ API 오류: {response.status_code}"
    
    data = response.json()
    if not data or "items" not in data or len(data["items"]) == 0:
        return f"😔 '{user_query}'에 대한 검색 결과가 없습니다."
    
    # HTML 태그 제거 함수
    def remove_html_tags(text: str) -> str:
        return re.sub(r"<[^>]+>", "", text)
    
    # 상위 3개만 정리
    products = data["items"][:3]
    output = f"🔍 '{user_query}' 검색 결과:\n\n"
    for i, item in enumerate(products, 1):
        title = remove_html_tags(item.get("title", ""))
        lprice = item.get("lprice", "0")
        mall = item.get("mallName", "정보 없음")
        link = item.get("link", "정보 없음")
        
        output += f"📦 {i}. {title}\n"
        if lprice != "0":
            output += f"   💰 가격: {int(lprice):,}원\n"
        output += f"   🏪 판매처: {mall}\n"
        output += f"   🔗 링크: {link}\n\n"
    
    return output

def human_fallback(state: dict) -> str:
    """향수 관련 복잡한 질문에 대한 기본 응답"""
    query = state.get("input", "")
    return (
        f"❓ '{query}' 더 명확한 설명이 필요합니다.\n"
        f"👉 질문을 구체적으로 다시 작성해 주세요.\n"
        f"💡 또는 향수에 관한 멋진 질문을 해보시는 건 어떨까요?"
    )

# -------------------------------
# LLM 파서 함수
# -------------------------------
def query_parser_node(state: AgentState) -> AgentState:
    user_query = state["messages"][-1] if state.get("messages") else ""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""
            너는 향수 쿼리 파서야.
            사용자의 질문에서 brand, concentration, day_night_score, gender,
            name, season_score, sizes 같은 정보를 JSON 형식으로 뽑아줘.
            없는 값은 null로 두고, 반드시 JSON만 출력해.

            질문: {user_query}
            """
        }],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "PerfumeQuery",
                "schema": {
                    "type": "object",
                    "properties": {
                        "brand": {"type": ["string", "null"]},
                        "concentration": {"type": ["string", "null"]},
                        "day_night_score": {"type": ["string", "null"]},
                        "gender": {"type": ["string", "null"]},
                        "season_score": {"type": ["string", "null"]},
                        "sizes": {"type": ["string", "null"]}
                    }
                }
            }
        }
    )

    parsed = response.choices[0].message.parsed
    state["parsed"] = parsed
    return state

import json
import joblib
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from rank_bm25 import BM25Okapi
from typing import List, Dict, Tuple, Optional


class PerfumeRecommender:
    """향수 추천 시스템 클래스"""
    
    def __init__(self, 
                 model_pkl_path: str = "./models.pkl", 
                 perfume_json_path: str = "perfumes.json",
                 model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 max_len: int = 256):
        
        self.model_name = model_name
        self.max_len = max_len
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[Device] {self.device}")
        
        # 모델 및 데이터 로드
        self._load_ml_model(model_pkl_path)
        self._load_transformer_model()
        self._load_perfume_data(perfume_json_path)
        self._build_bm25_index()
    
    def _load_ml_model(self, pkl_path: str):
        """저장된 ML 모델 불러오기"""
        data = joblib.load(pkl_path)
        self.clf = data["classifier"]
        self.mlb = data["mlb"]
        self.thresholds = data["thresholds"]
        
        print(f"[Loaded model from {pkl_path}]")
        print(f"Labels: {list(self.mlb.classes_)}")
    
    def _load_transformer_model(self):
        """Transformer 모델 로드"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.base_model = AutoModel.from_pretrained(self.model_name).to(self.device)
        self.base_model.eval()
    
    def _load_perfume_data(self, json_path: str):
        """향수 데이터 로드"""
        with open(json_path, "r", encoding="utf-8") as f:
            self.perfumes = json.load(f)
        print(f"[Loaded {len(self.perfumes)} perfumes from {json_path}]")
    
    def _build_bm25_index(self):
        """BM25 인덱스 구축"""
        self.corpus = [item.get("fragrances", "") for item in self.perfumes]
        tokenized_corpus = [doc.lower().split() for doc in self.corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)
        print("[BM25 index built]")
    
    def encode_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """텍스트를 임베딩으로 변환"""
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            enc = self.tokenizer(
                batch, 
                padding=True, 
                truncation=True, 
                max_length=self.max_len, 
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                model_out = self.base_model(**enc)
                emb = model_out.last_hidden_state.mean(dim=1)
            
            all_embeddings.append(emb.cpu().numpy())
        
        return np.vstack(all_embeddings)
    
    def predict_labels(self, text: str, topk: int = 3, use_thresholds: bool = True) -> List[str]:
        """텍스트에서 향수 라벨 예측"""
        emb = self.encode_texts([text], batch_size=1)
        proba = self.clf.predict_proba(emb)[0]
        
        if use_thresholds and self.thresholds:
            # threshold 기반 선택
            pick = [
                i for i, p in enumerate(proba) 
                if p >= self.thresholds.get(self.mlb.classes_[i], 0.5)
            ]
            # threshold를 넘는 것이 없으면 topk 선택
            if not pick:
                pick = np.argsort(-proba)[:topk]
        else:
            # 상위 topk 선택
            pick = np.argsort(-proba)[:topk]
        
        return [self.mlb.classes_[i] for i in pick]
    
    def search_perfumes(self, labels: List[str], top_n: int = 5) -> List[Tuple[int, float, Dict]]:
        """BM25를 사용해 향수 검색"""
        query = " ".join(labels)
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # 상위 N개 인덱스 선택
        top_idx = np.argsort(scores)[-top_n:][::-1]
        
        results = []
        for idx in top_idx:
            results.append((idx, scores[idx], self.perfumes[idx]))
        
        return results
    
    def recommend(self, 
                  user_text: str, 
                  topk_labels: int = 4, 
                  top_n_perfumes: int = 5,
                  use_thresholds: bool = True,
                  verbose: bool = True) -> Dict:
        """전체 추천 파이프라인"""
        
        # 1. ML 모델로 라벨 예측
        predicted_labels = self.predict_labels(
            user_text, 
            topk=topk_labels, 
            use_thresholds=use_thresholds
        )
        
        # 2. BM25로 향수 검색
        search_results = self.search_perfumes(predicted_labels, top_n=top_n_perfumes)
        
        if verbose:
            print("=== ML 예측 라벨 ===")
            print(predicted_labels)
            print(f"\n=== BM25 Top-{top_n_perfumes} 결과 ===")
            
            for rank, (idx, score, perfume) in enumerate(search_results, 1):
                print(f"[Rank {rank}] Score: {score:.2f}")
                print(f"  Brand      : {perfume.get('brand', 'N/A')}")
                print(f"  Name       : {perfume.get('name_perfume', 'N/A')}")
                print(f"  Fragrances : {perfume.get('fragrances', 'N/A')}")
                print()
        
        return {
            "user_input": user_text,
            "predicted_labels": predicted_labels,
            "recommendations": [
                {
                    "rank": rank,
                    "score": score,
                    "brand": perfume.get('brand', 'N/A'),
                    "name": perfume.get('name_perfume', 'N/A'),
                    "fragrances": perfume.get('fragrances', 'N/A'),
                    "perfume_data": perfume
                }
                for rank, (idx, score, perfume) in enumerate(search_results, 1)
            ]
        }


# 사용 예시
def main():
    # 추천 시스템 초기화
    recommender = PerfumeRecommender()
    
    # 사용자 입력 예시들
    test_inputs = [
        "시트러스하고 프루티한 향수 추천해줘",
        "로맨틱하고 플로랄한 향 원해",
        "우디하고 스파이시한 향수",
        "깔끔하고 상쾌한 향"
    ]
    
    for user_input in test_inputs:
        print(f"\n{'='*50}")
        print(f"사용자 입력: {user_input}")
        print(f"{'='*50}")
        
        # 추천 실행
        result = recommender.recommend(
            user_text=user_input,
            topk_labels=4,
            top_n_perfumes=3,
            verbose=True
        )


if __name__ == "__main__":
    main()
    parsed = response.choices[0].message.parsed

    # state에 파싱 결과 저장
    state["parsed"] = parsed
    return state