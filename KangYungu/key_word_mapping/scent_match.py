import os
import csv
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "dataset", "key_word.csv")

def load_keyword_dict(path: str):
    keyword_dict = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            canonical = row[0].strip()
            synonyms = [w.strip() for w in row[1:] if w.strip()]
            keyword_dict[canonical] = synonyms
    return keyword_dict

def get_embedding(text: str, model="text-embedding-3-small"):
    resp = client.embeddings.create(model=model, input=text)
    return resp.data[0].embedding

def cosine_sim(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def match_scent(question: str, keyword_dict: dict, top_k=3):
    q_emb = get_embedding(question)
    scores = []

    for canonical, synonyms in keyword_dict.items():
        for word in synonyms:
            sim = cosine_sim(q_emb, get_embedding(word))
            scores.append((canonical, word, sim))

    scores.sort(key=lambda x: x[2], reverse=True)

    seen = set()
    matches = []
    for canonical, word, sim in scores:
        if canonical not in seen:
            matches.append((canonical, sim))
            seen.add(canonical)
        if len(matches) >= top_k:
            break

    return matches

if __name__ == "__main__":
    keyword_dict = load_keyword_dict(CSV_PATH)

    q = input("질문을 입력하세요: ").strip()
    matches = match_scent(q, keyword_dict, top_k=3)
    print("향 매핑 결과:", matches)
