"""Keyword matching and lightweight opportunity scoring."""
import re
from typing import Dict, List
import pandas as pd

def extract_keywords(text: str, top_n: int = 12) -> List[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#-]{1,}", (text or "").lower())
    stop = {"the","and","for","with","from","your","this","that","how","what","why","are","you","into","learn","about","video"}
    counts = {}
    for w in words:
        if w not in stop:
            counts[w] = counts.get(w, 0) + 1
    return [w for w, _ in sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:top_n]]

def keyword_opportunities(df: pd.DataFrame, topic: str = "", platform: str = "Both") -> pd.DataFrame:
    """Rank dataset keywords with a transparent demand/competition heuristic."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["keyword","platform","search_demand","competition","relevance","opportunity_score"])
    out = df.copy()
    if topic.strip():
        topic_terms = set(extract_keywords(topic, 50))
        out["relevance"] = out["keyword"].astype(str).str.lower().apply(
            lambda k: 1.0 if any(t in k.lower() or k.lower() in t for t in topic_terms if len(t) > 2) else 0.35
        )
    else:
        out["relevance"] = 0.6
    if platform != "Both" and "platform" in out.columns:
        out = out[(out["platform"] == platform) | (out["platform"] == "Both")]
    for col in ["search_demand", "competition"]:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(50).clip(0,100)
    out["opportunity_score"] = (0.55*out["search_demand"] + 0.45*(100-out["competition"])) * out["relevance"]
    return out.sort_values("opportunity_score", ascending=False).reset_index(drop=True)
