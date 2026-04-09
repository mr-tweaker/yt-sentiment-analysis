"""
Sentiment analysis module with pluggable backends (TextBlob / transformer)
and optional language detection.
"""
import pandas as pd
import numpy as np
from functools import lru_cache
from tqdm import tqdm

from .config import (
    SENTIMENT_THRESHOLD_POSITIVE,
    SENTIMENT_THRESHOLD_NEGATIVE,
    SENTIMENT_BACKEND,
    TRANSFORMER_MODEL_NAME,
)

_backend = SENTIMENT_BACKEND or "textblob"

_textblob_available = False
try:
    from textblob import TextBlob
    _textblob_available = True
except Exception:
    TextBlob = None  # type: ignore

_transformer_available = False
_hf_pipeline = None
if _backend == "transformer":
    try:
        from transformers import pipeline

        _hf_pipeline = pipeline(
            "sentiment-analysis",
            model=TRANSFORMER_MODEL_NAME,
            top_k=None,
        )
        _transformer_available = True
    except Exception:
        _hf_pipeline = None
        _transformer_available = False

_langdetect_available = False
try:
    from langdetect import detect as _ld_detect

    _langdetect_available = True
except Exception:
    _langdetect_available = False


@lru_cache(maxsize=50000)
def _sentiment_textblob_cached(text: str) -> float:
    if not _textblob_available or TextBlob is None:
        return 0.0
    try:
        return float(TextBlob(text).sentiment.polarity)
    except Exception:
        return 0.0


@lru_cache(maxsize=50000)
def _sentiment_transformer_cached(text: str) -> float:
    if not _transformer_available or _hf_pipeline is None:
        return _sentiment_textblob_cached(text)
    try:
        # Expect labels like NEGATIVE/NEUTRAL/POSITIVE or 1/2/3 labels
        res = _hf_pipeline(text, truncation=True)[0]
        label = str(res.get("label", "")).upper()
        score = float(res.get("score", 0.0))
        # Map to [-1, 1]
        if "NEG" in label or label.endswith("0"):
            return -score
        if "POS" in label or label.endswith("2") or label.endswith("4"):
            return score
        # neutral or unknown
        return 0.0
    except Exception:
        return _sentiment_textblob_cached(text)


def calculate_sentiment(comment_text):
    """
    Calculate sentiment polarity for a single comment
    
    Args:
        comment_text: Text of the comment
    
    Returns:
        Sentiment polarity score (-1 to 1)
    """
    text = str(comment_text or "")
    if not text.strip():
        return 0.0

    if _backend == "transformer" and _transformer_available:
        return _sentiment_transformer_cached(text)
    # Fallback: TextBlob (if available)
    if _textblob_available:
        return _sentiment_textblob_cached(text)
    return 0.0


@lru_cache(maxsize=50000)
def _detect_language_cached(text: str) -> str:
    if not _langdetect_available:
        return "unknown"
    try:
        lang = _ld_detect(text)
        return lang or "unknown"
    except Exception:
        return "unknown"


def analyze_sentiment_batch(comments_df, show_progress=True):
    """
    Calculate sentiment for all comments in DataFrame
    
    Args:
        comments_df: DataFrame with 'comment_text' column
        show_progress: Whether to show progress bar
    
    Returns:
        DataFrame with added 'Polarity' column
    """
    df = comments_df.copy()
    
    print(f"Calculating sentiment for comments using backend='{_backend}'...")
    
    if show_progress:
        tqdm.pandas(desc="Processing comments")
        df['Polarity'] = df['comment_text'].progress_apply(calculate_sentiment)
    else:
        df['Polarity'] = df['comment_text'].apply(calculate_sentiment)

    # Optional language detection
    print("Detecting comment languages..." if _langdetect_available else "Language detection disabled or langdetect not installed.")
    if _langdetect_available:
        if show_progress:
            tqdm.pandas(desc="Detecting languages")
            df['language'] = df['comment_text'].progress_apply(lambda x: _detect_language_cached(str(x or "")[:500]))
        else:
            df['language'] = df['comment_text'].apply(lambda x: _detect_language_cached(str(x or "")[:500]))
    else:
        df['language'] = "unknown"
    
    print(f"Sentiment analysis complete. Mean polarity: {df['Polarity'].mean():.3f}")
    
    return df


def categorize_sentiment(polarity, positive_threshold=None, negative_threshold=None):
    """
    Categorize sentiment into 5 categories
    
    Args:
        polarity: Sentiment polarity score
        positive_threshold: Threshold for positive sentiment
        negative_threshold: Threshold for negative sentiment
    
    Returns:
        Sentiment category string
    """
    if positive_threshold is None:
        positive_threshold = SENTIMENT_THRESHOLD_POSITIVE
    if negative_threshold is None:
        negative_threshold = SENTIMENT_THRESHOLD_NEGATIVE
    
    if polarity < -0.5:
        return 'Very Negative'
    elif polarity < negative_threshold:
        return 'Negative'
    elif polarity <= positive_threshold:
        return 'Neutral'
    elif polarity <= 0.5:
        return 'Positive'
    else:
        return 'Very Positive'


def add_sentiment_categories(df):
    """
    Add sentiment category column to DataFrame
    
    Args:
        df: DataFrame with 'Polarity' column
    
    Returns:
        DataFrame with added 'sentiment_category' column
    """
    df = df.copy()
    df['sentiment_category'] = df['Polarity'].apply(categorize_sentiment)
    return df


def calculate_impact_score(df):
    """
    Calculate impact score combining sentiment and engagement
    
    Args:
        df: DataFrame with 'Polarity' and optionally 'likes', 'replies' columns
    
    Returns:
        DataFrame with added 'impact_score' column
    """
    df = df.copy()
    
    # Normalize sentiment to 0-1 scale
    df['sentiment_normalized'] = (df['Polarity'] + 1) / 2
    
    # Calculate engagement score
    if 'likes' in df.columns and 'replies' in df.columns:
        df['likes_numeric'] = pd.to_numeric(df['likes'], errors='coerce').fillna(0)
        df['replies_numeric'] = pd.to_numeric(df['replies'], errors='coerce').fillna(0)
        df['engagement_score'] = df['likes_numeric'] + df['replies_numeric']
        df['engagement_log'] = np.log1p(df['engagement_score'])
        df['impact_score'] = df['sentiment_normalized'] * (1 + df['engagement_log'])
    else:
        # If no engagement data, use absolute sentiment
        df['impact_score'] = df['Polarity'].abs()
    
    return df
