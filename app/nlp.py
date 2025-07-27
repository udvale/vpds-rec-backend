from sentence_transformers import SentenceTransformer, util
import json
import os

model = SentenceTransformer("all-MiniLM-L6-v2")
with open("components.json", "r", encoding="utf-8") as f:
    COMPONENTS_DATA = json.load(f)

component_descriptions = [c["description"] for c in COMPONENTS_DATA]
description_embeddings = model.encode(component_descriptions, convert_to_tensor=True)

def suggest_components(user_input: str, top_k: int = 5):
    user_embedding = model.encode(user_input, convert_to_tensor=True)
    similarities = util.cos_sim(user_embedding, description_embeddings)[0]

    top_results = similarities.topk(k=top_k)

    suggestions = []
    for score, idx in zip(top_results.values, top_results.indices):
        component = COMPONENTS_DATA[idx]
        suggestions.append({
            "name": component["component"],
            "score": float(score),
            "description": component["description"],
            "category": component.get("category", ""),
            "tags": component.get("tags", []),
            "variants": component.get("variants", [])
        })

    return suggestions