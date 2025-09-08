import re, requests
from langchain_core.tools import tool
from services import extract_search_keyword_with_llm, answer_faq, recommend_perfume_simple_core




def price_tool_factory(ctx):
@tool
def price_tool(user_query: str) -> str:
kw = extract_search_keyword_with_llm(ctx.llm, user_query)
url = "https://openapi.naver.com/v1/search/shop.json"
headers = {
"X-Naver-Client-Id": ctx.naver_client_id or "",
"X-Naver-Client-Secret": ctx.naver_client_secret or "",
}
params = {"query": kw, "display": 5, "sort": "sim"}
try:
resp = requests.get(url, headers=headers, params=params)
except Exception as e:
return f"❌ 요청 오류: {e}"
if resp.status_code != 200:
return f"❌ API 오류: {resp.status_code}"
data = resp.json()
if not data or not data.get('items'):
return f"😔 '{kw}' 검색 결과가 없습니다. 다른 키워드로 시도해보세요."
def strip_html(t: str) -> str:
return re.sub(r"<[^>]+>", "", t)
out, prices = [f"🔍 '{kw}' 검색 결과:\n"], []
for i, item in enumerate(data['items'][:3], 1):
title = strip_html(item.get('title',''))
lprice = item.get('lprice','0'); mall = item.get('mallName','정보 없음'); link = item.get('link','정보 없음')
out.append(f"📦 {i}. {title}\n")
if lprice != '0':
out.append(f" 💰 가격: {int(lprice):,}원\n"); prices.append(int(lprice))
out.append(f" 🏪 판매처: {mall}\n 🔗 링크: {link}\n\n")
if prices:
mn, mx = min(prices), max(prices)
if len(prices) > 1:
out.append(f"💡 **가격대 정보**\n 📊 {mn:,}원 ~ {mx:,}원\n ⚠️ 정확한 최저/최고가는 각 쇼핑몰에서 확인하세요.\n")
return ''.join(out)
return price_tool




def faq_tool_factory():
@tool
def faq_knowledge_tool(question: str) -> str:
return answer_faq(question)
return faq_knowledge_tool




def recommender_tool_factory():
@tool
def recommend_perfume_simple(user_text: str,
topk_labels: int = 4,
top_n_perfumes: int = 5,
use_thresholds: bool = True,
model_pkl_path: str = "./models.pkl",
perfume_json_path: str = "perfumes.json",
model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
max_len: int = 256):
return recommend_perfume_simple_core(user_text, topk_labels, top_n_perfumes, use_thresholds,
model_pkl_path, perfume_json_path, model_name, max_len)
return recommend_perfume_simple