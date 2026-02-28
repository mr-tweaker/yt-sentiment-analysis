"""
Medium complexity features
"""
import pandas as pd
import numpy as np


def analyze_sentiment_engagement_correlation(comments_df, video_df):
    """
    Analyze correlation between comment sentiment and video engagement
    
    Args:
        comments_df: DataFrame with comments and sentiment
        video_df: DataFrame with video metadata
    
    Returns:
        Dictionary with correlation results
    """
    if 'video_id' not in comments_df.columns or 'video_id' not in video_df.columns:
        return None
    
    # Group comments by video
    video_sentiment = comments_df.groupby('video_id')['Polarity'].agg(['mean', 'std', 'count']).reset_index()
    video_sentiment.columns = ['video_id', 'avg_sentiment', 'std_sentiment', 'comment_count']
    
    # Merge with video metadata
    merged = video_df.merge(video_sentiment, on='video_id', how='inner')
    
    # Convert numeric columns
    for col in ['likes', 'views', 'dislikes', 'comment_count']:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors='coerce')
    
    # Calculate correlation
    numeric_cols = ['avg_sentiment', 'likes', 'views', 'comment_count', 'dislikes']
    available_cols = [col for col in numeric_cols if col in merged.columns]
    
    if len(available_cols) > 1:
        correlation_matrix = merged[available_cols].corr()
        return {
            'merged_data': merged,
            'correlation_matrix': correlation_matrix,
            'video_sentiment': video_sentiment
        }
    
    return None


def analyze_category_sentiment(df):
    """
    Analyze sentiment by video category
    
    Args:
        df: DataFrame with 'category_name' and 'Polarity' columns
    
    Returns:
        DataFrame with category sentiment statistics
    """
    if 'category_name' not in df.columns:
        return None
    
    category_sentiment = df.groupby('category_name')['Polarity'].agg([
        'mean', 'std', 'count', 'min', 'max'
    ]).reset_index()
    
    category_sentiment.columns = ['category', 'avg_sentiment', 'std_sentiment', 
                                 'count', 'min_sentiment', 'max_sentiment']
    category_sentiment = category_sentiment.sort_values('avg_sentiment', ascending=False)
    
    return category_sentiment


def analyze_channel_sentiment(df):
    """
    Analyze sentiment by channel
    
    Args:
        df: DataFrame with 'channel_title' and 'Polarity' columns
    
    Returns:
        DataFrame with channel sentiment statistics
    """
    if 'channel_title' not in df.columns:
        return None
    
    channel_sentiment = df.groupby('channel_title')['Polarity'].agg([
        'mean', 'std', 'count'
    ]).reset_index()
    
    channel_sentiment.columns = ['channel', 'avg_sentiment', 'std_sentiment', 'comment_count']
    channel_sentiment = channel_sentiment[channel_sentiment['comment_count'] >= 10]
    channel_sentiment = channel_sentiment.sort_values('avg_sentiment', ascending=False)
    
    return channel_sentiment


def create_sentiment_heatmap(df, category_col='category_name', channel_col='channel_title'):
    """
    Create sentiment heatmap by category and channel
    
    Args:
        df: DataFrame with category, channel, and sentiment data
        category_col: Name of category column
        channel_col: Name of channel column
    
    Returns:
        Pivot table for heatmap visualization
    """
    if category_col not in df.columns or channel_col not in df.columns:
        return None
    
    # Get top categories and channels
    top_categories = df[category_col].value_counts().head(10).index
    top_channels = df[channel_col].value_counts().head(15).index
    
    # Filter data
    filtered = df[
        (df[category_col].isin(top_categories)) & 
        (df[channel_col].isin(top_channels))
    ]
    
    # Create pivot table
    heatmap_data = filtered.pivot_table(
        values='Polarity',
        index=category_col,
        columns=channel_col,
        aggfunc='mean'
    )
    
    return heatmap_data
