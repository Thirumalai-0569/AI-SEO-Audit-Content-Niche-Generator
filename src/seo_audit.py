"""Rule-based SEO audit helpers for creator content."""
import re
from collections import Counter
from typing import Dict, List

STOPWORDS = {
    "the","a","an","and","or","but","to","of","for","in","on","with","is","are",
    "how","what","why","your","you","my","this","that","from","by","at","as","be",
    "it","into","learn","video","shorts"
}

def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9+#]+", (text or "").lower())

def audit_content(title: str, description: str, hashtags: str = "", platform: str = "YouTube") -> Dict:
    """Return a transparent heuristic audit score and recommendations.

    This is not an official Instagram/YouTube ranking score.
    """
    title = title or ""
    description = description or ""
    tags = hashtags or ""
    tips = []
    score = 100

    # Title length: practical heuristic, not a platform ranking rule.
    title_len = len(title.strip())
    if title_len == 0:
        score -= 25
        tips.append("Add a clear, specific title that communicates the value of the content.")
    elif title_len < 20:
        score -= 8
        tips.append("Consider adding context to the title so viewers understand the topic.")
    elif title_len > 70:
        score -= 8
        tips.append("Shorten the title and place the main topic near the beginning.")
    else:
        tips.append("Title length looks reasonable; check that it accurately reflects the content.")

    title_tokens = [t for t in tokenize(title) if t not in STOPWORDS]
    if len(title_tokens) < 2:
        score -= 10
        tips.append("Include a relevant topic keyword and a clear benefit.")
    else:
        tips.append("Use one primary keyword naturally in the title.")

    desc_len = len(description.strip())
    if desc_len == 0:
        score -= 20
        tips.append("Write a useful description with context, key points and a call to action.")
    elif desc_len < 80:
        score -= 8
        tips.append("Expand the description with helpful context and relevant terms.")
    else:
        tips.append("Description has useful length; avoid keyword stuffing.")

    hashtag_list = re.findall(r"#([A-Za-z0-9_]+)", tags)
    if not hashtag_list:
        score -= 10
        tips.append("Add a small set of highly relevant hashtags if they fit the platform and content.")
    elif len(hashtag_list) > 12:
        score -= 5
        tips.append("Reduce broad or repetitive hashtags; prioritize relevance.")
    else:
        tips.append("Hashtag count is reasonable; make sure every hashtag matches the content.")

    repeated = [w for w, c in Counter(tokenize(title + " " + description)).items() if c >= 5 and w not in STOPWORDS]
    if repeated:
        score -= min(10, len(repeated) * 3)
        tips.append("Avoid repeated keyword use: " + ", ".join(repeated[:5]) + ".")

    if platform.lower().startswith("instagram") and title_len > 125:
        tips.append("For Reels, consider a concise on-screen hook; this title field is a planning aid.")
    if platform.lower().startswith("youtube") and desc_len < 150:
        tips.append("For YouTube, include a concise summary, useful links and relevant chapters where appropriate.")

    score = max(0, min(100, score))
    return {
        "score": score,
        "grade": "Strong" if score >= 80 else ("Needs improvement" if score >= 60 else "Needs work"),
        "title_length": title_len,
        "description_length": desc_len,
        "hashtags_found": len(hashtag_list),
        "recommendations": tips,
        "disclaimer": "Heuristic checklist only; not an official platform score or a guarantee of reach."
    }
