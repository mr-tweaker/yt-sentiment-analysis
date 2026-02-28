"""
Configuration file for YouTube Sentiment Analysis project
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data paths (update these to match your data location)
DATA_DIR = PROJECT_ROOT / "data"
COMMENTS_CSV = DATA_DIR / "UScomments.csv"
VIDEOS_CSV = DATA_DIR / "USvideos.csv"  # If you have video metadata
ADDITIONAL_DATA_DIR = DATA_DIR / "additional_data"

# Output paths
OUTPUT_DIR = PROJECT_ROOT / "output"
REPORTS_DIR = OUTPUT_DIR / "reports"
FIGURES_DIR = OUTPUT_DIR / "figures"
DATABASE_PATH = OUTPUT_DIR / "youtube_sentiment_analysis.db"

# Create output directories if they don't exist
OUTPUT_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

# Analysis parameters
SAMPLE_SIZE = 1000  # Number of comments to analyze (None for all)
SENTIMENT_THRESHOLD_POSITIVE = 0.1
SENTIMENT_THRESHOLD_NEGATIVE = -0.1

# Topic modeling parameters
N_TOPICS = 5
MAX_FEATURES = 1000

# Visualization parameters
FIGURE_SIZE = (12, 6)
DPI = 100

# Database settings
DB_NAME = "youtube_sentiment_analysis.db"

# YouTube API Configuration
# Set via environment variable YOUTUBE_API_KEY or in dashboard UI
DEFAULT_YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
