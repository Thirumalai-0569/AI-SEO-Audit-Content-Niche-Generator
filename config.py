"""Configuration for AI SEO Niche Generator."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"

SAMPLE_POSTS_PATH = DATA_DIR / "sample_posts.csv"
NICHE_KEYWORDS_PATH = DATA_DIR / "niche_keywords.csv"
MODEL_PATH = MODEL_DIR / "performance_model.pkl"
FEATURE_COLUMNS_PATH = MODEL_DIR / "feature_columns.pkl"
DB_PATH = BASE_DIR / "creator_insights.db"

# The target label in sample_posts.csv is synthetic demonstration data.
# Change this threshold to suit your real historical dataset and use case.
SUCCESS_ENGAGEMENT_RATE_THRESHOLD = 4.0
RANDOM_STATE = 42
