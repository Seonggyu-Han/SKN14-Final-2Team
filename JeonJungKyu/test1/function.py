# function.py
import requests
import re
import os
from dotenv import load_dotenv
from langchain.tools import tool

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
def perfume_recommendation_tool():
    pass