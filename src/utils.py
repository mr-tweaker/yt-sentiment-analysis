"""
Utility functions for the project
"""
import pandas as pd
import numpy as np
import emoji
from collections import Counter
import re
from wordcloud import STOPWORDS


def extract_emojis(text):
    """
    Extract emojis from text
    
    Args:
        text: Input text string
    
    Returns:
        List of emojis found in text
    """
    return [char for char in str(text) if char in emoji.EMOJI_DATA]


def calculate_comment_metrics(df):
    """
    Calculate comment length and word count metrics
    
    Args:
        df: DataFrame with 'comment_text' column
    
    Returns:
        DataFrame with added 'comment_length' and 'word_count' columns
    """
    df = df.copy()
    df['comment_length'] = df['comment_text'].astype(str).str.len()
    df['word_count'] = df['comment_text'].astype(str).str.split().str.len()
    return df


def extract_keywords(text, min_length=3, stopwords=None):
    """
    Extract keywords from text
    
    Args:
        text: Input text
        min_length: Minimum word length
        stopwords: Set of stopwords to exclude
    
    Returns:
        List of keywords
    """
    if stopwords is None:
        stopwords = set(STOPWORDS)
    
    words = re.findall(r'\b[a-z]{' + str(min_length) + r',}\b', str(text).lower())
    return [w for w in words if w not in stopwords]


def get_word_sentiment_mapping(df):
    """
    Create mapping of words to their average sentiment
    
    Args:
        df: DataFrame with 'comment_text' and 'Polarity' columns
    
    Returns:
        Dictionary mapping words to average sentiment scores
    """
    all_word_sentiments = {}
    
    for idx, row in df.iterrows():
        text = str(row['comment_text'])
        sentiment = row['Polarity']
        words = text.lower().split()
        
        for word in words:
            # Remove punctuation
            word = ''.join(c for c in word if c.isalnum())
            if len(word) > 2 and word not in STOPWORDS:
                if word not in all_word_sentiments:
                    all_word_sentiments[word] = []
                all_word_sentiments[word].append(sentiment)
    
    # Calculate average sentiment per word
    word_avg_sentiment = {
        word: np.mean(sents) 
        for word, sents in all_word_sentiments.items() 
        if len(sents) >= 3
    }
    
    return word_avg_sentiment
