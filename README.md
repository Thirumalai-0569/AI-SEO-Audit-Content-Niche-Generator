# AI SEO Audit & Content Niche Generator

A beginner-friendly Streamlit project for Instagram and YouTube content planning.

## Features
- Rule-based SEO audit for title, description and hashtags
- Keyword opportunity ranking from a supplied CSV
- Content niche and topic ideas
- Logistic Regression classifier estimating the probability of a **defined synthetic success label**
- Template-based content generation without an API key
- Optional local Ollama content generation
- SQLite history for saved SEO audits
- Three Jupyter notebooks for analysis, SEO checks and model training

## Important data disclaimer
`data/sample_posts.csv` and `data/niche_keywords.csv` are example datasets. The post dataset is synthetic. The model output is a software demonstration, not a validated prediction of views, virality, followers or revenue. Keyword demand and competition numbers are illustrative scores, not measured search volume. Replace them with authorized, representative data before making real decisions.

## 1. Requirements
- Python 3.10 or 3.11 recommended
- Windows, macOS or Linux
- Optional: Ollama for local LLM generation

## 2. Setup on Windows (Anaconda Prompt)
```bash
cd path\to\ai_seo_niche_generator
conda create -n seo_ai python=3.11 -y
conda activate seo_ai
pip install -r requirements.txt
```

Or use a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## 3. Run the Streamlit app
```bash
streamlit run app.py
```
A local browser tab should open. If it does not, use the local URL printed in the terminal.

## 4. Train / refresh the demonstration model
Open the **Performance Probability** tab and click **Train / refresh demonstration model**. The app also includes model artifacts created from the bundled sample dataset. To train from a notebook:
- Open Jupyter from the project root.
- Open `notebooks/03_model_training.ipynb`.
- Run the cells in order.

## 5. Optional local Ollama setup
1. Install Ollama from its official website.
2. In a terminal, pull a model, for example:
   ```bash
   ollama pull llama3.2
   ```
3. Ensure Ollama is running, then enable **Use Ollama locally** in the app.

Template mode works without Ollama or any API key.

## 6. Dataset columns
`sample_posts.csv` includes:
- `post_id`, `platform`, `topic`, `posting_time`
- `duration_seconds`, `title_keyword_score`, `hashtag_relevance`
- `historical_engagement_rate`, `success`
- `views`, `likes`, `comments`, `shares`

The `success` target is synthetic and generated for demo purposes. Define your own target from real data before retraining.

`niche_keywords.csv` includes `keyword`, `platform`, `search_demand`, and `competition`. Values are illustrative 0–100 scores, not live market metrics.

## 7. Project structure
```text
ai_seo_niche_generator/
├── app.py
├── requirements.txt
├── config.py
├── data/
├── models/
├── notebooks/
├── src/
└── reports/
```

## Troubleshooting
- **ModuleNotFoundError:** Run commands from the project root and install `pip install -r requirements.txt` in the same environment used by Streamlit.
- **streamlit not recognized:** Run `python -m streamlit run app.py`.
- **Ollama connection error:** Disable Ollama mode or start Ollama and verify the model is installed.
- **Model training error:** Check the CSV has the required columns and at least two examples for each target class.
- **Port already in use:** Run `python -m streamlit run app.py --server.port 8502`.

## Next improvements
- Connect authorized YouTube Analytics / Instagram Insights data
- Add keyword provider integrations
- Add proper probability calibration and time-based evaluation
- Add multilingual (including Tamil) content generation
- Add exports to PDF and Excel
