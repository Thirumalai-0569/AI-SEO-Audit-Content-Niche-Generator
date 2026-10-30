"""Content generation using templates; optional local Ollama integration."""
import json
import urllib.request
import urllib.error

def generate_content(topic: str, platform: str, audience: str = "Beginners", use_ollama: bool = False,
                    ollama_model: str = "llama3.2") -> dict:
    topic = (topic or "AI").strip()
    audience = (audience or "Beginners").strip()
    if use_ollama:
        prompt = f"""Create a practical content plan for {platform} about {topic} for {audience}.
Return valid JSON with keys: title, hook, description, hashtags (array), script_outline (array), call_to_action.
Do not promise virality. Keep suggestions accurate and specific."""
        payload = json.dumps({"model": ollama_model, "prompt": prompt, "stream": False, "format": "json"}).encode()
        req = urllib.request.Request("http://localhost:11434/api/generate", data=payload,
                                     headers={"Content-Type":"application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                data = json.loads(response.read().decode("utf-8"))
            return json.loads(data.get("response", "{}"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Could not use Ollama. Check Ollama is running and model '{ollama_model}' is installed. Details: {exc}")
    clean_topic = topic.replace("#","").strip()
    return {
        "title": f"{clean_topic}: 5 Practical Tips for {audience}",
        "hook": f"Want to understand {clean_topic}? Start with this simple example.",
        "description": f"In this post, we explore {clean_topic} for {audience.lower()}. Save this guide and share the tip that helped you most.",
        "hashtags": ["#"+w.replace(" ","") for w in [clean_topic, "Learn", "Tutorial", platform.replace(" ","")]][:4],
        "script_outline": [
            f"Hook: introduce a common problem related to {clean_topic}.",
            "Explain the key concept in one or two simple points.",
            "Demonstrate a practical example.",
            "Summarize the takeaway and invite a genuine question."
        ],
        "call_to_action": "Ask viewers which related topic they want explained next.",
        "note": "Template-based output. Enable Ollama for local LLM-generated variations."
    }
