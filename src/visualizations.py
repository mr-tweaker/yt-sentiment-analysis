"""
Visualization functions
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from wordcloud import WordCloud, STOPWORDS
from pathlib import Path

from .config import FIGURES_DIR, FIGURE_SIZE, DPI


def setup_style():
    """Setup matplotlib style"""
    sns.set_style("whitegrid")
    plt.rcParams['figure.dpi'] = DPI
    plt.rcParams['savefig.dpi'] = DPI


def plot_sentiment_distribution(df, save_path=None):
    """
    Plot sentiment distribution histogram
    
    Args:
        df: DataFrame with 'Polarity' column
        save_path: Path to save figure (optional)
    """
    setup_style()
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    sns.histplot(df['Polarity'], kde=True, bins=50, ax=ax, color='steelblue', alpha=0.7)
    ax.axvline(df['Polarity'].mean(), color='r', linestyle='--', linewidth=2, label=f"Mean: {df['Polarity'].mean():.3f}")
    ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.5, label='Neutral')
    ax.set_xlabel('Sentiment Polarity', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Sentiment Distribution', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.savefig(FIGURES_DIR / 'sentiment_distribution.png')
    plt.close()


def plot_wordcloud(df, sentiment_filter=None, save_path=None):
    """
    Generate word cloud for comments
    
    Args:
        df: DataFrame with 'comment_text' column
        sentiment_filter: Filter by sentiment ('positive', 'negative', or None)
        save_path: Path to save figure (optional)
    """
    if sentiment_filter == 'positive':
        filtered_df = df[df['Polarity'] > 0.1]
        colormap = 'Greens'
        title = 'Positive Comments Word Cloud'
    elif sentiment_filter == 'negative':
        filtered_df = df[df['Polarity'] < -0.1]
        colormap = 'Reds'
        title = 'Negative Comments Word Cloud'
    else:
        filtered_df = df
        colormap = 'viridis'
        title = 'All Comments Word Cloud'
    
    if len(filtered_df) == 0:
        print(f"No comments found for {sentiment_filter} filter")
        return
    
    text = ' '.join(filtered_df['comment_text'].astype(str))
    
    wordcloud = WordCloud(stopwords=set(STOPWORDS), width=1200, height=600,
                         background_color='white', colormap=colormap,
                         max_words=200).generate(text)
    
    plt.figure(figsize=(16, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    else:
        filename = f'wordcloud_{sentiment_filter or "all"}.png'
        plt.savefig(FIGURES_DIR / filename)
    plt.close()


def plot_emoji_sentiment(emoji_df, save_path=None):
    """
    Plot emoji sentiment analysis
    
    Args:
        emoji_df: DataFrame with emoji sentiment data
        save_path: Path to save figure (optional)
    """
    if len(emoji_df) == 0:
        return
    
    setup_style()
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Top positive emojis
    top_positive = emoji_df.head(15)
    sns.barplot(x=top_positive['avg_sentiment'], y=top_positive['emoji'],
               palette='Greens_r', ax=axes[0])
    axes[0].set_title('Top 15 Emojis by Average Sentiment (Most Positive)', 
                     fontsize=13, fontweight='bold')
    axes[0].set_xlabel('Average Sentiment Polarity', fontsize=11)
    
    # Top negative emojis
    top_negative = emoji_df.tail(15).sort_values('avg_sentiment')
    sns.barplot(x=top_negative['avg_sentiment'], y=top_negative['emoji'],
               palette='Reds_r', ax=axes[1])
    axes[1].set_title('Top 15 Emojis by Average Sentiment (Most Negative)',
                     fontsize=13, fontweight='bold')
    axes[1].set_xlabel('Average Sentiment Polarity', fontsize=11)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.savefig(FIGURES_DIR / 'emoji_sentiment.png')
    plt.close()


def plot_sentiment_by_category(category_df, save_path=None):
    """
    Plot sentiment by category
    
    Args:
        category_df: DataFrame with category sentiment data
        save_path: Path to save figure (optional)
    """
    if category_df is None or len(category_df) == 0:
        return
    
    setup_style()
    fig, ax = plt.subplots(figsize=(14, 8))
    
    sns.boxplot(x='category', y='avg_sentiment', data=category_df, palette='Set3', ax=ax)
    ax.set_xlabel('Video Category', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Sentiment', fontsize=12, fontweight='bold')
    ax.set_title('Sentiment Distribution by Video Category', fontsize=14, fontweight='bold')
    ax.axhline(0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    plt.xticks(rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.savefig(FIGURES_DIR / 'sentiment_by_category.png')
    plt.close()


def plot_correlation_heatmap(correlation_matrix, save_path=None):
    """
    Plot correlation heatmap
    
    Args:
        correlation_matrix: Correlation matrix DataFrame
        save_path: Path to save figure (optional)
    """
    if correlation_matrix is None or len(correlation_matrix) == 0:
        return
    
    setup_style()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
               square=True, linewidths=1, cbar_kws={"shrink": 0.8}, fmt='.3f')
    plt.title('Correlation Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.savefig(FIGURES_DIR / 'correlation_heatmap.png')
    plt.close()


def plot_sentiment_categories(df, save_path=None):
    """
    Plot sentiment category distribution
    
    Args:
        df: DataFrame with 'sentiment_category' column
        save_path: Path to save figure (optional)
    """
    if 'sentiment_category' not in df.columns:
        return
    
    setup_style()
    sentiment_counts = df['sentiment_category'].value_counts()
    sentiment_order = ['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive']
    sentiment_counts_ordered = [sentiment_counts.get(cat, 0) for cat in sentiment_order]
    
    # Filter out zero counts to avoid pie chart errors
    filtered_data = [(cat, count) for cat, count in zip(sentiment_order, sentiment_counts_ordered) if count > 0]
    if not filtered_data:
        print("No sentiment categories found to plot")
        return
    
    filtered_cats, filtered_counts = zip(*filtered_data)
    colors = ['#d62728', '#ff7f0e', '#bcbd22', '#2ca02c', '#1f77b4']
    filtered_colors = [colors[sentiment_order.index(cat)] for cat in filtered_cats]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Pie chart (only with non-zero values)
    if len(filtered_counts) > 0 and sum(filtered_counts) > 0:
        axes[0].pie(filtered_counts, labels=filtered_cats, autopct='%1.1f%%',
                   colors=filtered_colors, startangle=90, textprops={'fontsize': 11})
        axes[0].set_title('Sentiment Distribution (Pie Chart)', fontsize=13, fontweight='bold')
    
    # Bar chart (show all categories, even if zero)
    bars = axes[1].bar(sentiment_order, sentiment_counts_ordered, color=colors, alpha=0.8, edgecolor='black')
    axes[1].set_xlabel('Sentiment Category', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Number of Comments', fontsize=12, fontweight='bold')
    axes[1].set_title('Sentiment Category Distribution', fontsize=14, fontweight='bold')
    axes[1].tick_params(axis='x', rotation=15)
    axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.savefig(FIGURES_DIR / 'sentiment_categories.png')
    plt.close()
