"""
Sentiment analysis module using TextBlob
"""
import pandas as pd
import numpy as np
from textblob import TextBlob
from tqdm import tqdm

from .config import SENTIMENT_THRESHOLD_POSITIVE, SENTIMENT_THRESHOLD_NEGATIVE


def calculate_sentiment(comment_text):
    """
    Calculate sentiment polarity for a single comment
    
    Args:
        comment_text: Text of the comment
    
    Returns:
        Sentiment polarity score (-1 to 1)
    """
    try:
        return TextBlob(str(comment_text)).sentiment.polarity
    except:
        return 0.0


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
    
    print("Calculating sentiment for comments...")
    
    if show_progress:
        tqdm.pandas(desc="Processing comments")
        df['Polarity'] = df['comment_text'].progress_apply(calculate_sentiment)
    else:
        df['Polarity'] = df['comment_text'].apply(calculate_sentiment)
    
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
