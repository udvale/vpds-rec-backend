"""Pick matching components from a query string with proper scoring."""
import json
import re
import pathlib
from typing import List

# Load the data
DATA = json.loads(pathlib.Path("data/components.json").read_text("utf-8"))
NAME2COMP = {c["component"]: c for c in DATA}

def score_component_relevance(component: dict, query: str) -> float:
    """Score how relevant a component is to the query."""
    query_lower = query.lower()
    query_words = set(re.findall(r'\b\w+\b', query_lower))
    
    if not query_words:
        return 0.0
    
    score = 0.0
    
    # Component name exact match (highest weight)
    comp_name = component["component"].lower()
    if comp_name in query_lower:
        score += 20.0
    
    # Component name word matches
    comp_words = set(re.findall(r'\b\w+\b', comp_name))
    name_matches = query_words.intersection(comp_words)
    score += len(name_matches) * 10.0
    
    # Description word matches
    description = component.get("description", "").lower()
    desc_words = set(re.findall(r'\b\w+\b', description))
    desc_matches = query_words.intersection(desc_words)
    score += len(desc_matches) * 3.0
    
    # Tag matches
    tags = component.get("tags", [])
    tag_words = set()
    for tag in tags:
        tag_words.update(re.findall(r'\b\w+\b', tag.lower()))
    
    tag_matches = query_words.intersection(tag_words)
    score += len(tag_matches) * 5.0
    
    # UI pattern bonuses
    ui_patterns = {
        'form': ['input', 'button', 'checkbox', 'textfield', 'select', 'textarea', 'label'],
        'login': ['input', 'button', 'textfield', 'checkbox'],
        'profile': ['avatar', 'badge', 'card', 'image'],
        'navigation': ['button', 'link', 'breadcrumb', 'menu'],
        'layout': ['card', 'container', 'grid', 'box'],
        'data': ['table', 'list', 'card', 'grid'],
        'user': ['avatar', 'badge', 'profile', 'card'],
    }
    
    for pattern, related_components in ui_patterns.items():
        if pattern in query_lower:
            if comp_name in related_components:
                score += 15.0
            elif any(related in comp_name for related in related_components):
                score += 8.0
    
    return score

def top_components(query: str, k: int = 3) -> List[str]:
    """Return top k component names ranked by relevance to query."""
    
    print(f"🔍 Processing query: '{query}'")
    
    if not query.strip():
        # Return first k components as fallback
        fallback = [comp["component"] for comp in DATA[:k]]
        print(f"📦 Empty query, returning: {fallback}")
        return fallback
    
    # Score all components
    scored_components = []
    for component in DATA:
        score = score_component_relevance(component, query)
        if score > 0:
            scored_components.append((component["component"], score))
    
    # Sort by score descending
    scored_components.sort(key=lambda x: x[1], reverse=True)
    
    # Get top k component names
    result = [comp_name for comp_name, score in scored_components[:k]]
    
    # If we don't have enough matches, add some common ones
    if len(result) < k:
        common_components = ["Button", "Input", "Card", "Badge", "Avatar"]
        available_common = [comp for comp in common_components if comp in NAME2COMP]
        
        for comp in available_common:
            if comp not in result:
                result.append(comp)
                if len(result) >= k:
                    break
    
    # Final fallback - just use first k available components
    if len(result) < k:
        all_available = [comp["component"] for comp in DATA]
        for comp in all_available:
            if comp not in result:
                result.append(comp)
                if len(result) >= k:
                    break
    
    final_result = result[:k]
    
    # Debug output
    print(f"📦 Selected components: {final_result}")
    if scored_components:
        print(f"📊 Top scored components: {[(name, f'{score:.1f}') for name, score in scored_components[:5]]}")
    
    return final_result