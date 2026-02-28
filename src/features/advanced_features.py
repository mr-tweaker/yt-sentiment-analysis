"""
Advanced features: topic modeling, network graphs, aspect analysis, etc.
"""
import pandas as pd
import numpy as np
from datetime import datetime

try:
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.feature_extraction.text import CountVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False


def perform_topic_modeling(df, n_topics=5, max_features=1000):
    """
    Perform topic modeling using LDA
    
    Args:
        df: DataFrame with 'comment_text' column
        n_topics: Number of topics to extract
        max_features: Maximum number of features for vectorization
    
    Returns:
        Dictionary with topic modeling results
    """
    if not SKLEARN_AVAILABLE:
        print("scikit-learn not available. Install with: pip install scikit-learn")
        return None
    
    text_data = df['comment_text'].astype(str).tolist()
    
    # Create document-term matrix
    vectorizer = CountVectorizer(max_features=max_features, stop_words='english',
                                min_df=2, max_df=0.95)
    X = vectorizer.fit_transform(text_data)
    
    # Apply LDA
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42,
                                   max_iter=10, learning_method='online')
    lda.fit(X)
    
    # Get topic distributions
    topic_distributions = lda.transform(X)
    df_with_topics = df.copy()
    df_with_topics['topic'] = topic_distributions.argmax(axis=1)
    
    # Get top words per topic
    feature_names = vectorizer.get_feature_names_out()
    n_top_words = 10
    topics_words = {}
    
    for topic_idx, topic in enumerate(lda.components_):
        top_words_idx = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topics_words[topic_idx] = top_words
    
    # Sentiment by topic
    sentiment_by_topic = df_with_topics.groupby('topic')['Polarity'].agg([
        'mean', 'std', 'count'
    ]).reset_index()
    sentiment_by_topic.columns = ['topic', 'avg_sentiment', 'std_sentiment', 'count']
    
    return {
        'df_with_topics': df_with_topics,
        'lda_model': lda,
        'vectorizer': vectorizer,
        'topics_words': topics_words,
        'sentiment_by_topic': sentiment_by_topic
    }


def create_comment_network(df, max_videos=20, max_comments_per_video=10):
    """
    Create network graph of comments (simplified - connects comments from same video)
    
    Args:
        df: DataFrame with 'video_id' and 'Polarity' columns
        max_videos: Maximum number of videos to include
        max_comments_per_video: Maximum comments per video
    
    Returns:
        NetworkX graph object
    """
    if not NETWORKX_AVAILABLE:
        print("networkx not available. Install with: pip install networkx")
        return None
    
    if 'video_id' not in df.columns:
        return None
    
    G = nx.Graph()
    video_groups = df.groupby('video_id')
    
    for video_id, group in list(video_groups)[:max_videos]:
        comment_list = list(group.iterrows())[:max_comments_per_video]
        
        # Add nodes
        for idx, row in comment_list:
            comment_id = f"{video_id}_{idx}"
            G.add_node(comment_id, sentiment=row['Polarity'],
                      video_id=video_id)
        
        # Connect comments from same video
        comment_ids = [f"{video_id}_{idx}" for idx, _ in comment_list]
        for i, id1 in enumerate(comment_ids):
            for id2 in comment_ids[i+1:]:
                G.add_edge(id1, id2)
    
    return G


def analyze_aspect_sentiment(df, aspect_keywords=None):
    """
    Analyze sentiment by aspect (video quality, content, creator, etc.)
    
    Args:
        df: DataFrame with 'comment_text' and 'Polarity' columns
        aspect_keywords: Dictionary mapping aspect names to keyword lists
    
    Returns:
        DataFrame with aspect sentiment analysis
    """
    if aspect_keywords is None:
        aspect_keywords = {
            'video_quality': ['quality', 'hd', 'resolution', 'clear', 'blurry', 'pixelated'],
            'content': ['content', 'information', 'topic', 'subject', 'material'],
            'creator': ['creator', 'youtuber', 'channel', 'host', 'personality'],
            'audio': ['audio', 'sound', 'voice', 'volume', 'music', 'noise'],
            'editing': ['editing', 'cut', 'transition', 'effects', 'production'],
            'entertainment': ['funny', 'entertaining', 'boring', 'interesting', 'enjoyable'],
            'length': ['long', 'short', 'duration', 'time', 'length'],
            'recommendation': ['recommend', 'suggest', 'watch', 'subscribe', 'like']
        }
    
    aspect_sentiments = {aspect: [] for aspect in aspect_keywords.keys()}
    
    for idx, row in df.iterrows():
        comment_text = str(row['comment_text']).lower()
        sentiment = row['Polarity']
        
        for aspect, keywords in aspect_keywords.items():
            if any(keyword in comment_text for keyword in keywords):
                aspect_sentiments[aspect].append(sentiment)
    
    # Calculate statistics per aspect
    aspect_analysis = []
    for aspect, sentiments in aspect_sentiments.items():
        if len(sentiments) > 0:
            aspect_analysis.append({
                'aspect': aspect,
                'avg_sentiment': np.mean(sentiments),
                'count': len(sentiments),
                'std': np.std(sentiments)
            })
    
    if aspect_analysis:
        aspect_df = pd.DataFrame(aspect_analysis)
        aspect_df = aspect_df.sort_values('avg_sentiment', ascending=False)
        return aspect_df
    
    return pd.DataFrame()


def analyze_time_trends(df, date_column=None):
    """
    Analyze sentiment trends over time
    
    Args:
        df: DataFrame with date and sentiment data
        date_column: Name of date column (if None, tries to find it)
    
    Returns:
        DataFrame with time-based sentiment aggregation
    """
    if date_column is None:
        date_cols = [col for col in df.columns if 'date' in col.lower() or 
                    'time' in col.lower() or 'published' in col.lower()]
        if not date_cols:
            return None
        date_column = date_cols[0]
    
    if date_column not in df.columns:
        return None
    
    try:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df = df[df[date_column].notna()]
        
        df['year_month'] = df[date_column].dt.to_period('M')
        
        time_sentiment = df.groupby('year_month')['Polarity'].agg([
            'mean', 'std', 'count'
        ]).reset_index()
        
        return time_sentiment
    except Exception as e:
        print(f"Error processing time trends: {e}")
        return None
