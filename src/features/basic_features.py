"""
Basic enhancement features
"""
import pandas as pd
import numpy as np
import emoji
from collections import Counter
from scipy import stats

from ..utils import extract_emojis, calculate_comment_metrics, get_word_sentiment_mapping


def analyze_emoji_sentiment(df):
    """
    Analyze sentiment correlation with emojis
    
    Args:
        df: DataFrame with 'comment_text' and 'Polarity' columns
    
    Returns:
        DataFrame with emoji sentiment analysis
    """
    emoji_sentiment = []
    
    for idx, row in df.iterrows():
        comment = str(row['comment_text'])
        sentiment = row['Polarity']
        emojis_in_comment = extract_emojis(comment)
        
        for emoji_char in emojis_in_comment:
            emoji_sentiment.append({'emoji': emoji_char, 'sentiment': sentiment})
    
    emoji_df = pd.DataFrame(emoji_sentiment)
    
    if len(emoji_df) > 0:
        emoji_sentiment_avg = emoji_df.groupby('emoji')['sentiment'].agg(['mean', 'count']).reset_index()
        emoji_sentiment_avg.columns = ['emoji', 'avg_sentiment', 'frequency']
        emoji_sentiment_avg = emoji_sentiment_avg.sort_values('avg_sentiment', ascending=False)
        emoji_sentiment_avg = emoji_sentiment_avg[emoji_sentiment_avg['frequency'] >= 3]
        return emoji_sentiment_avg
    
    return pd.DataFrame()


def analyze_comment_length_sentiment(df):
    """
    Analyze relationship between comment length and sentiment
    
    Args:
        df: DataFrame with 'comment_text' and 'Polarity' columns
    
    Returns:
        DataFrame with length metrics and analysis
    """
    df = calculate_comment_metrics(df)
    
    # Create length buckets
    df['length_bucket'] = pd.cut(
        df['comment_length'],
        bins=[0, 50, 100, 200, 500, float('inf')],
        labels=['0-50', '50-100', '100-200', '200-500', '500+']
    )
    
    # Calculate statistics by length bucket
    sentiment_by_length = df.groupby('length_bucket')['Polarity'].agg(['mean', 'std', 'count']).reset_index()
    sentiment_by_length.columns = ['length_bucket', 'avg_sentiment', 'std_sentiment', 'count']
    
    return df, sentiment_by_length


def calculate_sentiment_statistics(df):
    """
    Calculate comprehensive sentiment statistics
    
    Args:
        df: DataFrame with 'Polarity' column
    
    Returns:
        Dictionary with statistics
    """
    stats_dict = {}
    
    # Basic statistics
    stats_dict['mean'] = df['Polarity'].mean()
    stats_dict['median'] = df['Polarity'].median()
    stats_dict['std'] = df['Polarity'].std()
    stats_dict['min'] = df['Polarity'].min()
    stats_dict['max'] = df['Polarity'].max()
    
    # Advanced statistics
    stats_dict['skewness'] = stats.skew(df['Polarity'])
    stats_dict['kurtosis'] = stats.kurtosis(df['Polarity'])
    
    # Category counts
    positive_count = (df['Polarity'] > 0.1).sum()
    negative_count = (df['Polarity'] < -0.1).sum()
    neutral_count = ((df['Polarity'] >= -0.1) & (df['Polarity'] <= 0.1)).sum()
    
    stats_dict['positive_count'] = positive_count
    stats_dict['negative_count'] = negative_count
    stats_dict['neutral_count'] = neutral_count
    stats_dict['positive_pct'] = positive_count / len(df) * 100
    stats_dict['negative_pct'] = negative_count / len(df) * 100
    stats_dict['neutral_pct'] = neutral_count / len(df) * 100
    
    # Outliers (IQR method)
    Q1 = df['Polarity'].quantile(0.25)
    Q3 = df['Polarity'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df['Polarity'] < lower_bound) | (df['Polarity'] > upper_bound)]
    stats_dict['outlier_count'] = len(outliers)
    stats_dict['outlier_pct'] = len(outliers) / len(df) * 100
    
    return stats_dict


def rank_comments_by_impact(df):
    """
    Rank comments by impact score (sentiment × engagement)
    
    Args:
        df: DataFrame with sentiment and engagement data
    
    Returns:
        DataFrame sorted by impact score
    """
    from ..sentiment_analyzer import calculate_impact_score
    
    df = calculate_impact_score(df)
    df = df.sort_values('impact_score', ascending=False)
    
    return df
