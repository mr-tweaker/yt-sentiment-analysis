#!/usr/bin/env python3
"""
Streamlit Dashboard for YouTube Sentiment Analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import load_comments, load_video_metadata, prepare_data
from src.sentiment_analyzer import analyze_sentiment_batch, add_sentiment_categories, calculate_impact_score
from src.config import DEFAULT_YOUTUBE_API_KEY
from src.features.basic_features import (
    analyze_emoji_sentiment, analyze_comment_length_sentiment,
    calculate_sentiment_statistics, rank_comments_by_impact
)
from src.features.medium_features import (
    analyze_sentiment_engagement_correlation, analyze_category_sentiment,
    analyze_channel_sentiment, create_sentiment_heatmap
)
from src.features.advanced_features import (
    perform_topic_modeling, analyze_aspect_sentiment, analyze_time_trends
)
from src.config import COMMENTS_CSV, VIDEOS_CSV, SAMPLE_SIZE

# Page configuration
st.set_page_config(
    page_title="YouTube Sentiment Analysis Dashboard",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF0000;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF0000;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(comments_path=None, videos_path=None, sample_size=None):
    """Load and process data with caching"""
    try:
        comments_df = load_comments(file_path=comments_path, sample_size=sample_size)
        video_df = load_video_metadata(file_path=videos_path)
        df = prepare_data(comments_df, video_df)
        df = analyze_sentiment_batch(df, show_progress=False)
        df = add_sentiment_categories(df)
        df = calculate_impact_score(df)
        return df, video_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def main():
    """Main dashboard function"""
    # Header
    st.markdown('<div class="main-header">🎥 YouTube Sentiment Analysis Dashboard</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # File paths
        comments_path = st.text_input(
            "Comments CSV Path",
            value=str(COMMENTS_CSV),
            help="Path to your comments CSV file"
        )
        
        videos_path = st.text_input(
            "Videos CSV Path (Optional)",
            value=str(VIDEOS_CSV) if Path(VIDEOS_CSV).exists() else "",
            help="Path to your videos metadata CSV file"
        )
        
        sample_size = st.number_input(
            "Sample Size",
            min_value=100,
            max_value=100000,
            value=SAMPLE_SIZE,
            step=100,
            help="Number of comments to analyze"
        )
        
        # Load data button
        if st.button("🔄 Load Data", type="primary"):
            with st.spinner("Loading data..."):
                df, video_df = load_data(comments_path if Path(comments_path).exists() else None,
                                       videos_path if videos_path and Path(videos_path).exists() else None,
                                       sample_size)
                if df is not None:
                    st.session_state['df'] = df
                    st.session_state['video_df'] = video_df
                    st.success(f"✅ Loaded {len(df)} comments!")
        
        # Check if data is loaded
        if 'df' not in st.session_state:
            st.warning("⚠️ Please load data first")
            st.stop()
    
    df = st.session_state['df']
    video_df = st.session_state.get('video_df', None)
    
    # Main metrics
    st.header("📊 Overview Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Comments", f"{len(df):,}")
    
    with col2:
        mean_sentiment = df['Polarity'].mean()
        st.metric("Avg Sentiment", f"{mean_sentiment:.3f}")
    
    with col3:
        positive = (df['Polarity'] > 0.1).sum()
        st.metric("Positive", f"{positive:,}", f"{(positive/len(df)*100):.1f}%")
    
    with col4:
        negative = (df['Polarity'] < -0.1).sum()
        st.metric("Negative", f"{negative:,}", f"{(negative/len(df)*100):.1f}%")
    
    with col5:
        neutral = len(df) - positive - negative
        st.metric("Neutral", f"{neutral:,}", f"{(neutral/len(df)*100):.1f}%")
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Sentiment Distribution",
        "😀 Emoji Analysis",
        "📝 Comment Analysis",
        "🎯 Category & Channel",
        "🔍 Advanced Features",
        "💬 Top Comments"
    ])
    
    # Tab 1: Sentiment Distribution
    with tab1:
        st.subheader("Sentiment Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.histplot(df['Polarity'], kde=True, bins=50, ax=ax, color='steelblue', alpha=0.7)
            ax.axvline(df['Polarity'].mean(), color='r', linestyle='--', linewidth=2, 
                      label=f"Mean: {df['Polarity'].mean():.3f}")
            ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.5, label='Neutral')
            ax.set_xlabel('Sentiment Polarity')
            ax.set_ylabel('Frequency')
            ax.set_title('Sentiment Distribution')
            ax.legend()
            ax.grid(alpha=0.3)
            st.pyplot(fig)
            plt.close()
        
        with col2:
            # Sentiment categories
            if 'sentiment_category' in df.columns:
                sentiment_counts = df['sentiment_category'].value_counts()
                sentiment_order = ['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive']
                sentiment_counts_ordered = [sentiment_counts.get(cat, 0) for cat in sentiment_order]
                
                fig, ax = plt.subplots(figsize=(10, 6))
                colors = ['#d62728', '#ff7f0e', '#bcbd22', '#2ca02c', '#1f77b4']
                bars = ax.bar(sentiment_order, sentiment_counts_ordered, color=colors, alpha=0.8, edgecolor='black')
                ax.set_xlabel('Sentiment Category')
                ax.set_ylabel('Number of Comments')
                ax.set_title('Sentiment Category Distribution')
                ax.tick_params(axis='x', rotation=15)
                ax.grid(axis='y', alpha=0.3)
                
                # Add value labels
                for bar, val in zip(bars, sentiment_counts_ordered):
                    if val > 0:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{int(val)}\n({val/len(df)*100:.1f}%)',
                               ha='center', va='bottom', fontsize=9)
                st.pyplot(fig)
                plt.close()
        
        # Statistics
        st.subheader("Statistical Summary")
        stats_dict = calculate_sentiment_statistics(df)
        stats_df = pd.DataFrame([
            ['Mean', f"{stats_dict['mean']:.3f}"],
            ['Median', f"{stats_dict['median']:.3f}"],
            ['Std Deviation', f"{stats_dict['std']:.3f}"],
            ['Skewness', f"{stats_dict['skewness']:.3f}"],
            ['Kurtosis', f"{stats_dict['kurtosis']:.3f}"],
            ['Min', f"{stats_dict['min']:.3f}"],
            ['Max', f"{stats_dict['max']:.3f}"]
        ], columns=['Metric', 'Value'])
        st.dataframe(stats_df, use_container_width=True)
    
    # Tab 2: Emoji Analysis
    with tab2:
        st.subheader("Emoji Sentiment Analysis")
        
        emoji_df = analyze_emoji_sentiment(df)
        
        if len(emoji_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Top 15 Positive Emojis**")
                top_positive = emoji_df.head(15)
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.barplot(x=top_positive['avg_sentiment'], y=top_positive['emoji'],
                           palette='Greens_r', ax=ax)
                ax.set_xlabel('Average Sentiment')
                ax.set_title('Most Positive Emojis')
                st.pyplot(fig)
                plt.close()
            
            with col2:
                st.write("**Top 15 Negative Emojis**")
                top_negative = emoji_df.tail(15).sort_values('avg_sentiment')
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.barplot(x=top_negative['avg_sentiment'], y=top_negative['emoji'],
                           palette='Reds_r', ax=ax)
                ax.set_xlabel('Average Sentiment')
                ax.set_title('Most Negative Emojis')
                st.pyplot(fig)
                plt.close()
            
            # Emoji table
            st.subheader("Emoji Statistics")
            st.dataframe(emoji_df.head(30), use_container_width=True)
        else:
            st.info("No emojis found in comments")
    
    # Tab 3: Comment Analysis
    with tab3:
        st.subheader("Comment Length vs. Sentiment")
        
        df_with_length, length_stats = analyze_comment_length_sentiment(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.scatterplot(x='comment_length', y='Polarity', data=df_with_length,
                          alpha=0.4, s=20, ax=ax)
            ax.set_xlabel('Comment Length (characters)')
            ax.set_ylabel('Sentiment Polarity')
            ax.set_title('Comment Length vs. Sentiment')
            ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
            st.pyplot(fig)
            plt.close()
        
        with col2:
            if 'length_bucket' in df_with_length.columns:
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.boxplot(x='length_bucket', y='Polarity', data=df_with_length,
                           palette='viridis', ax=ax)
                ax.set_xlabel('Comment Length (characters)')
                ax.set_ylabel('Sentiment Polarity')
                ax.set_title('Sentiment by Length Bucket')
                ax.axhline(0, color='red', linestyle='--', linewidth=1, alpha=0.5)
                plt.xticks(rotation=15)
                st.pyplot(fig)
                plt.close()
        
        st.subheader("Length Statistics")
        st.dataframe(length_stats, use_container_width=True)
    
    # Tab 4: Category & Channel
    with tab4:
        st.subheader("Category and Channel Analysis")
        
        if 'category_name' in df.columns:
            category_sentiment = analyze_category_sentiment(df)
            
            if category_sentiment is not None and len(category_sentiment) > 0:
                st.write("**Sentiment by Category**")
                fig, ax = plt.subplots(figsize=(12, 8))
                top_cats = category_sentiment.head(15)
                sns.barplot(x='avg_sentiment', y='category', data=top_cats,
                           palette='coolwarm', ax=ax)
                ax.set_xlabel('Average Sentiment')
                ax.set_title('Top 15 Categories by Average Sentiment')
                ax.axvline(0, color='black', linestyle='-', linewidth=1)
                st.pyplot(fig)
                plt.close()
                
                st.dataframe(category_sentiment, use_container_width=True)
        
        if 'channel_title' in df.columns:
            channel_sentiment = analyze_channel_sentiment(df)
            
            if channel_sentiment is not None and len(channel_sentiment) > 0:
                st.write("**Sentiment by Channel**")
                top_channels = channel_sentiment.head(20)
                
                fig = px.bar(
                    top_channels,
                    x='avg_sentiment',
                    y='channel',
                    orientation='h',
                    title='Top 20 Channels by Average Sentiment',
                    color='avg_sentiment',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(channel_sentiment.head(30), use_container_width=True)
        
        # Heatmap
        if 'category_name' in df.columns and 'channel_title' in df.columns:
            st.subheader("Category-Channel Heatmap")
            heatmap_data = create_sentiment_heatmap(df)
            if heatmap_data is not None and len(heatmap_data) > 0:
                fig, ax = plt.subplots(figsize=(14, 10))
                sns.heatmap(heatmap_data, annot=True, fmt='.2f', cmap='RdYlGn', center=0,
                           cbar_kws={'label': 'Average Sentiment'}, linewidths=0.5, ax=ax)
                ax.set_xlabel('Channel')
                ax.set_ylabel('Category')
                ax.set_title('Sentiment Heatmap: Category vs. Channel')
                plt.xticks(rotation=45, ha='right', fontsize=8)
                plt.yticks(rotation=0, fontsize=9)
                st.pyplot(fig)
                plt.close()
    
    # Tab 5: Advanced Features
    with tab5:
        st.subheader("Advanced Analysis")
        
        # Topic Modeling
        if st.checkbox("Run Topic Modeling"):
            with st.spinner("Performing topic modeling (this may take a while)..."):
                topic_results = perform_topic_modeling(df)
                if topic_results:
                    st.write("**Sentiment by Topic**")
                    sentiment_by_topic = topic_results['sentiment_by_topic']
                    st.dataframe(sentiment_by_topic, use_container_width=True)
                    
                    # Visualize
                    fig = px.bar(
                        sentiment_by_topic,
                        x='topic',
                        y='avg_sentiment',
                        title='Average Sentiment by Topic',
                        color='avg_sentiment',
                        color_continuous_scale='RdYlGn'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Top words per topic
                    st.write("**Top Words per Topic**")
                    for topic_idx, words in topic_results['topics_words'].items():
                        st.write(f"**Topic {topic_idx}:** {', '.join(words[:10])}")
        
        # Aspect Analysis
        if st.checkbox("Run Aspect-Based Analysis"):
            aspect_df = analyze_aspect_sentiment(df)
            if len(aspect_df) > 0:
                st.write("**Sentiment by Aspect**")
                fig = px.bar(
                    aspect_df,
                    x='aspect',
                    y='avg_sentiment',
                    title='Average Sentiment by Aspect',
                    color='avg_sentiment',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(aspect_df, use_container_width=True)
        
        # Engagement Correlation
        if video_df is not None and st.checkbox("Show Engagement Correlation"):
            engagement_corr = analyze_sentiment_engagement_correlation(df, video_df)
            if engagement_corr and engagement_corr.get('correlation_matrix') is not None:
                st.write("**Correlation Matrix**")
                corr_matrix = engagement_corr['correlation_matrix']
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                           square=True, linewidths=1, cbar_kws={"shrink": 0.8}, fmt='.3f', ax=ax)
                st.pyplot(fig)
                plt.close()
    
    # Tab 6: Top Comments
    with tab6:
        st.subheader("Top Comments by Impact")
        
        ranked_df = rank_comments_by_impact(df)
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            sentiment_filter = st.selectbox(
                "Filter by Sentiment",
                ["All", "Positive", "Negative", "Neutral"]
            )
        with col2:
            num_comments = st.slider("Number of Comments", 10, 100, 20)
        
        # Filter data
        if sentiment_filter == "Positive":
            filtered_df = ranked_df[ranked_df['Polarity'] > 0.1]
        elif sentiment_filter == "Negative":
            filtered_df = ranked_df[ranked_df['Polarity'] < -0.1]
        elif sentiment_filter == "Neutral":
            filtered_df = ranked_df[(ranked_df['Polarity'] >= -0.1) & (ranked_df['Polarity'] <= 0.1)]
        else:
            filtered_df = ranked_df
        
        # Display top comments
        top_comments = filtered_df.head(num_comments)
        
        for idx, row in top_comments.iterrows():
            with st.expander(f"Comment {idx+1} | Sentiment: {row['Polarity']:.3f} | Impact: {row['impact_score']:.3f}"):
                st.write(f"**Comment:** {row['comment_text']}")
                if 'engagement_score' in row:
                    st.write(f"**Engagement:** {row['engagement_score']:.0f}")
                if 'category_name' in row and pd.notna(row['category_name']):
                    st.write(f"**Category:** {row['category_name']}")
                if 'channel_title' in row and pd.notna(row['channel_title']):
                    st.write(f"**Channel:** {row['channel_title']}")

if __name__ == "__main__":
    main()
