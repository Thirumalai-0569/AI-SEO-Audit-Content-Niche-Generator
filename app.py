"""Streamlit front end for AI SEO Audit and Content Niche Generator."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import pandas as pd
import plotly.express as px

from config import SAMPLE_POSTS_PATH, NICHE_KEYWORDS_PATH
from src.seo_audit import audit_content
from src.keyword_analyzer import keyword_opportunities
from src.niche_generator import generate_niche_ideas
from src.probability_model import train_model, load_model, predict_success_probability
from src.content_generator import generate_content
from src.database import init_db, save_analysis, get_recent_analyses

st.set_page_config(page_title="AI SEO & Niche Generator", page_icon="", layout="wide")
init_db()

@st.cache_data
def read_csv(path):
    return pd.read_csv(path)

st.title("AI SEO Audit & Content Niche Generator")
st.caption("Instagram + YouTube | SEO checks, niche opportunities, content ideas and ML-based probability estimates")
st.warning("Demo disclaimer: bundled post data is synthetic. Scores and probabilities are not guarantees of views, virality, followers or revenue.")

with st.sidebar:
    st.header("Creator settings")
    platform = st.selectbox("Platform", ["YouTube", "YouTube Shorts", "Instagram Reels", "Instagram Posts"])
    topic = st.text_input("Main niche / topic", "Python and Artificial Intelligence")
    audience = st.selectbox("Target audience", ["Beginners", "Students", "Working professionals", "Small businesses", "Content creators"])
    st.divider()
    st.subheader("Optional local LLM")
    use_ollama = st.checkbox("Use Ollama locally", value=False)
    ollama_model = st.text_input("Ollama model name", "llama3.2", disabled=not use_ollama)

try:
    posts = read_csv(str(SAMPLE_POSTS_PATH))
except Exception:
    posts = pd.DataFrame()
try:
    keywords = read_csv(str(NICHE_KEYWORDS_PATH))
except Exception:
    keywords = pd.DataFrame(columns=["keyword","platform","search_demand","competition"])

tab1, tab2, tab3, tab4, tab5 = st.tabs(["SEO Audit", "Niche & Keywords", "Performance Probability", "Content Generator", "Saved Analyses"])

with tab1:
    st.subheader("Audit a planned post")
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Post / video title", "Python AI Projects for Beginners: 5 Ideas")
        description = st.text_area("Description / caption", "Learn five beginner-friendly Python and AI project ideas, with simple steps and practical examples. Follow for more tutorials.")
    with col2:
        hashtags = st.text_input("Hashtags (include #)", "#Python #AI #MachineLearning #Coding")
        st.caption("This audit checks text fields you provide. It does not automatically access private account analytics.")
        if st.button("Run SEO audit", type="primary"):
            audit = audit_content(title, description, hashtags, platform)
            st.session_state["last_audit"] = audit
            st.session_state["last_title"] = title
            st.session_state["last_description"] = description
            st.session_state["last_hashtags"] = hashtags
            st.session_state["last_platform"] = platform
            st.session_state["last_topic"] = topic
    if "last_audit" in st.session_state:
        audit = st.session_state["last_audit"]
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Heuristic SEO score", f'{audit["score"]}/100')
        m2.metric("Title characters", audit["title_length"])
        m3.metric("Description characters", audit["description_length"])
        m4.metric("Hashtags found", audit["hashtags_found"])
        st.progress(audit["score"]/100)
        st.write(f'**Assessment:** {audit["grade"]}')
        for rec in audit["recommendations"]:
            st.write("• " + rec)
        st.caption(audit["disclaimer"])
        if st.button("Save SEO audit"):
            result = {"audit": audit, "title": st.session_state.get("last_title",""),
                      "description": st.session_state.get("last_description",""),
                      "hashtags": st.session_state.get("last_hashtags","")}
            row_id = save_analysis(st.session_state.get("last_platform", platform),
                                   st.session_state.get("last_topic", topic), audit["score"], result)
            st.success(f"Saved analysis #{row_id}.")

with tab2:
    st.subheader("Find content niche opportunities")
    st.write("Ranks the bundled example keyword list using demand, competition and topic relevance. Replace it with trusted, current keyword research for real market decisions.")
    if not keywords.empty:
        ranked = keyword_opportunities(keywords, topic, "Both" if platform.startswith("YouTube") else "Instagram")
        if not ranked.empty:
            st.dataframe(ranked[["keyword","platform","search_demand","competition","relevance","opportunity_score"]].head(20),
                         use_container_width=True, hide_index=True)
            chart = px.bar(ranked.head(10), x="opportunity_score", y="keyword", orientation="h",
                           title="Top keyword opportunities (heuristic)")
            chart.update_layout(yaxis={"categoryorder":"total ascending"})
            st.plotly_chart(chart, use_container_width=True)
            ideas = generate_niche_ideas(topic, platform, keywords, audience, 10)
            st.subheader("Suggested content niches and ideas")
            st.dataframe(pd.DataFrame(ideas), use_container_width=True, hide_index=True)
            st.download_button("Download niche ideas CSV", pd.DataFrame(ideas).to_csv(index=False).encode("utf-8"),
                               "niche_ideas.csv", "text/csv")
    else:
        st.info("No keyword dataset found. Check data/niche_keywords.csv.")

with tab3:
    st.subheader("Estimate probability of exceeding the defined engagement threshold")
    st.write("The sample model is trained on synthetic data for demonstration. Do not use its probability as a real-world forecast until retrained and calibrated on representative historical account data.")
    with st.expander("Input features", expanded=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            duration = st.number_input("Duration (seconds)", min_value=1, max_value=3600, value=45)
            title_score = st.slider("Title keyword score", 0.0, 1.0, 0.75, 0.05)
        with c2:
            hashtag_score = st.slider("Hashtag relevance", 0.0, 1.0, 0.70, 0.05)
            historical_rate = st.number_input("Historical engagement rate (%)", 0.0, 100.0, 4.0, 0.25)
        with c3:
            posting_time = st.selectbox("Planned posting time", ["Morning", "Afternoon", "Evening", "Night"])
            st.caption("Use comparable posts from the same platform and account where possible.")
    if st.button("Train / refresh demonstration model"):
        try:
            with st.spinner("Training model..."):
                metrics, _ = train_model()
            st.session_state["model_metrics"] = metrics
            st.success("Model trained and saved.")
        except Exception as e:
            st.error(f"Training failed: {e}")
    model = load_model()
    if model is None:
        st.info("No saved model yet. Click 'Train / refresh demonstration model' to create it.")
    else:
        if st.button("Estimate probability"):
            try:
                prob = predict_success_probability(model, platform, topic, posting_time, duration, title_score, hashtag_score, historical_rate)
                st.metric("Estimated probability", f"{prob:.0%}")
                st.progress(prob)
                st.caption("This is the model's probability for the dataset's defined success label. The bundled synthetic data makes it demonstration-only.")
            except Exception as e:
                st.error(f"Prediction failed: {e}")
    if "model_metrics" in st.session_state:
        metrics = st.session_state["model_metrics"]
        st.subheader("Hold-out evaluation metrics")
        cols = st.columns(5)
        for col, key in zip(cols, ["accuracy","precision","recall","roc_auc","brier_score"]):
            col.metric(key.replace("_"," ").title(), "N/A" if metrics.get(key) is None else str(metrics[key]))
        st.json(metrics)

with tab4:
    st.subheader("Generate a content concept")
    st.write("Template mode works without an API key. Optional Ollama mode sends the prompt to your local Ollama service.")
    if st.button("Generate content plan", type="primary"):
        try:
            result = generate_content(topic, platform, audience, use_ollama, ollama_model)
            st.session_state["generated_content"] = result
        except Exception as e:
            st.error(str(e))
    if "generated_content" in st.session_state:
        result = st.session_state["generated_content"]
        st.markdown(f"### {result.get('title','Content idea')}")
        st.markdown(f"**Hook:** {result.get('hook','')}")
        st.markdown(f"**Description:** {result.get('description','')}")
        st.markdown("**Hashtags:** " + " ".join(result.get("hashtags", [])))
        st.markdown("**Script outline:**")
        for item in result.get("script_outline", []):
            st.write("• " + item)
        st.markdown(f"**Call to action:** {result.get('call_to_action','')}")
        st.download_button("Download content plan JSON", pd.Series(result).to_json(indent=2, force_ascii=False),
                           "content_plan.json", "application/json")

with tab5:
    st.subheader("Recent saved analyses")
    rows = get_recent_analyses(50)
    if rows:
        history = pd.DataFrame(rows, columns=["ID","Created (UTC)","Platform","Topic","SEO score"])
        st.dataframe(history, use_container_width=True, hide_index=True)
    else:
        st.info("No saved analyses yet. Run and save an SEO audit first.")
