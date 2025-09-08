import json, re, joblib, numpy as np, torch
# ---------- Simple ML recommender ----------


def recommend_perfume_simple_core(user_text: str,
topk_labels: int = 4,
top_n_perfumes: int = 5,
use_thresholds: bool = True,
model_pkl_path: str = "./models.pkl",
perfume_json_path: str = "perfumes.json",
model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
max_len: int = 256) -> Dict[str, Any]:
device = "cuda" if torch.cuda.is_available() else "cpu"
data = joblib.load(model_pkl_path)
clf = data["classifier"]; mlb = data["mlb"]; thresholds = data.get("thresholds", {}) or {}


tok = AutoTokenizer.from_pretrained(model_name)
enc = AutoModel.from_pretrained(model_name).to(device)
enc.eval()


with open(perfume_json_path, 'r', encoding='utf-8') as f:
perfumes = json.load(f)
if not isinstance(perfumes, list):
raise ValueError("perfumes.json must contain a list of perfume objects")


def doc_of(p):
fr = p.get('fragrances')
if isinstance(fr, list):
text = ' '.join(map(str, fr))
elif isinstance(fr, str):
text = fr
else:
parts = [p.get('description',''), p.get('main_accords',''), p.get('name_perfume') or p.get('name',''), p.get('brand','')]
text = ' '.join([str(x) for x in parts if x])
return (text or 'unknown').lower()


tokenized = [doc_of(p).split() for p in perfumes]
bm25 = BM25Okapi(tokenized)


batch = tok([user_text], padding=True, truncation=True, max_length=max_len, return_tensors='pt').to(device)
with torch.no_grad():
out = enc(**batch)
emb = out.last_hidden_state.mean(dim=1).cpu().numpy()


if hasattr(clf, 'predict_proba'):
proba = clf.predict_proba(emb)[0]
elif hasattr(clf, 'decision_function'):
logits = np.asarray(clf.decision_function(emb)[0], dtype=float)
proba = 1.0/(1.0+np.exp(-logits))
else:
proba = np.asarray(clf.predict(emb)[0], dtype=float)


classes = list(mlb.classes_)
if use_thresholds and thresholds:
idx = [i for i, p in enumerate(proba) if p >= float(thresholds.get(classes[i], 0.5))]
if not idx:
idx = np.argsort(-proba)[:topk_labels].tolist()
else:
idx = np.argsort(-proba)[:topk_labels].tolist()


labels = [classes[i] for i in idx]
scores = bm25.get_scores(' '.join(labels).split())
top_idx = np.argsort(scores)[-top_n_perfumes:][::-1]


def _safe(d, *keys, default="N/A"):
for k in keys:
if k in d and d[k]:
return d[k]
return default


recs = []
for rnk, i in enumerate(top_idx, 1):
p = perfumes[int(i)]
fr = p.get('fragrances')
fr_text = ', '.join(map(str, fr)) if isinstance(fr, list) else (fr if isinstance(fr, str) else _safe(p, 'main_accords', default='N/A'))
recs.append({
'rank': int(rnk), 'index': int(i), 'score': float(scores[int(i)]),
'brand': _safe(p, 'brand'), 'name': _safe(p, 'name_perfume', 'name'),
'fragrances': fr_text, 'perfume_data': p,
})


return {
'user_input': user_text,
'predicted_labels': labels,
'recommendations': recs,
'meta': {'model_name': model_name, 'device': device, 'max_len': int(max_len), 'db_size': int(len(perfumes))},
}