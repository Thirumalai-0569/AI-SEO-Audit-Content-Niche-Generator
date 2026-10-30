"""Rule-based niche recommendations; replace/augment with validated market data."""
from typing import List, Dict
import pandas as pd
from src.keyword_analyzer import keyword_opportunities

def generate_niche_ideas(topic: str, platform: str, keyword_df: pd.DataFrame, audience: str = "Beginners", count: int = 10) -> List[Dict]:
    ranked = keyword_opportunities(keyword_df, topic, platform)
    topic = (topic or "digital skills").strip()
    audience = (audience or "Beginners").strip()
    ideas = []
    templates = [
        ("Beginner tutorials", f"{topic} explained simply for {audience.lower()}"),
        ("Common mistakes", f"Common {topic} mistakes and how to fix them"),
        ("Step-by-step projects", f"Build a practical {topic} project from scratch"),
        ("Tools and comparisons", f"Best tools for {topic}: features and trade-offs"),
        ("Myth vs fact", f"{topic} myths beginners should stop believing"),
        ("Career and use cases", f"Real-world {topic} use cases and career paths"),
        ("Quick tips", f"Five actionable {topic} tips in under one minute"),
        ("Case study", f"A real-world style case study about {topic}"),
        ("Frequently asked questions", f"Answer the top beginner questions about {topic}"),
        ("Challenge series", f"A 7-day {topic} learning challenge"),
    ]
    for i, (category, idea) in enumerate(templates[:count]):
        score = float(ranked.iloc[i % len(ranked)]["opportunity_score"]) if not ranked.empty else max(30, 70-i*4)
        keyword = str(ranked.iloc[i % len(ranked)]["keyword"]) if not ranked.empty else topic
        ideas.append({
            "content_pillar": category,
            "idea": idea,
            "suggested_keyword": keyword,
            "opportunity_score": round(max(0,min(100,score)),1),
            "platform": platform,
            "note": "Opportunity score is a dataset-based heuristic, not a forecast of views or revenue."
        })
    return ideas
