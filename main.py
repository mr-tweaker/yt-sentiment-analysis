#!/usr/bin/env python3
"""
Main entry point for YouTube Sentiment Analysis project
"""
import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import load_comments, load_video_metadata, prepare_data
from src.config import COMMENTS_CSV, VIDEOS_CSV
from src.sentiment_analyzer import analyze_sentiment_batch, add_sentiment_categories, calculate_impact_score
from src.visualizations import (
    plot_sentiment_distribution, plot_wordcloud, plot_emoji_sentiment,
    plot_sentiment_by_category, plot_correlation_heatmap, plot_sentiment_categories
)
from src.features.basic_features import (
    analyze_emoji_sentiment, analyze_comment_length_sentiment,
    calculate_sentiment_statistics, rank_comments_by_impact
)
from src.features.medium_features import (
    analyze_sentiment_engagement_correlation, analyze_category_sentiment,
    analyze_channel_sentiment, create_sentiment_heatmap
)
from src.features.advanced_features import (
    perform_topic_modeling, create_comment_network,
    analyze_aspect_sentiment, analyze_time_trends
)
from src.config import OUTPUT_DIR, REPORTS_DIR, DATABASE_PATH
import pandas as pd
import sqlite3


def generate_report(df, stats_dict, output_file=None):
    """Generate text report with analysis results"""
    if output_file is None:
        output_file = REPORTS_DIR / 'sentiment_analysis_report.txt'
    
    report = []
    report.append("=" * 80)
    report.append("YOUTUBE SENTIMENT ANALYSIS REPORT")
    report.append("=" * 80)
    report.append(f"\nGenerated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\nDataset Overview:")
    report.append(f"  - Total comments analyzed: {len(df)}")
    
    report.append(f"\nSentiment Statistics:")
    report.append(f"  - Mean sentiment: {stats_dict['mean']:.3f}")
    report.append(f"  - Median sentiment: {stats_dict['median']:.3f}")
    report.append(f"  - Std deviation: {stats_dict['std']:.3f}")
    report.append(f"  - Positive comments: {stats_dict['positive_pct']:.1f}%")
    report.append(f"  - Neutral comments: {stats_dict['neutral_pct']:.1f}%")
    report.append(f"  - Negative comments: {stats_dict['negative_pct']:.1f}%")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
    
    print(f"\nReport saved to {output_file}")


def export_to_database(df, db_path=None):
    """Export results to SQLite database"""
    if db_path is None:
        db_path = DATABASE_PATH
    
    conn = sqlite3.connect(db_path)
    
    # Export comments with sentiment
    columns_to_export = ['comment_text', 'Polarity']
    for col in ['video_id', 'likes', 'replies', 'sentiment_category', 'topic',
                'comment_length', 'word_count', 'impact_score']:
        if col in df.columns:
            columns_to_export.append(col)
    
    export_data = df[columns_to_export].copy()
    export_data.to_sql('comments_with_sentiment', conn, if_exists='replace', index=False)
    print(f"Exported {len(export_data)} comments to database")
    
    # Export summary statistics
    stats_dict = calculate_sentiment_statistics(df)
    summary_stats = pd.DataFrame({
        'metric': ['total_comments', 'mean_sentiment', 'median_sentiment', 'std_sentiment',
                  'positive_pct', 'neutral_pct', 'negative_pct'],
        'value': [
            len(df),
            stats_dict['mean'],
            stats_dict['median'],
            stats_dict['std'],
            stats_dict['positive_pct'],
            stats_dict['neutral_pct'],
            stats_dict['negative_pct']
        ]
    })
    summary_stats.to_sql('summary_statistics', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"Database export complete: {db_path}")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='YouTube Sentiment Analysis')
    parser.add_argument('--comments', '-c', type=str, 
                       help='Path to comments CSV file')
    parser.add_argument('--videos', '-v', type=str,
                       help='Path to videos CSV file (optional)')
    parser.add_argument('--sample-size', '-s', type=int, default=None,
                       help='Number of comments to sample (default: 1000)')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("YouTube Sentiment Analysis")
    print("=" * 80)
    
    # Determine file paths
    comments_path = args.comments or os.getenv('COMMENTS_CSV') or COMMENTS_CSV
    videos_path = args.videos or os.getenv('VIDEOS_CSV') or VIDEOS_CSV
    
    # Load data
    print("\n[1/8] Loading data...")
    try:
        comments_df = load_comments(file_path=comments_path, sample_size=args.sample_size)
        video_df = load_video_metadata(file_path=videos_path if Path(videos_path).exists() else None)
        df = prepare_data(comments_df, video_df)
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Quick Setup:")
        print("   1. Create a 'data' directory: mkdir -p data")
        print("   2. Place your CSV file there: mv your_file.csv data/UScomments.csv")
        print("   3. Or run with: python main.py --comments /path/to/your/file.csv")
        return
    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Sentiment analysis
    print("\n[2/8] Performing sentiment analysis...")
    df = analyze_sentiment_batch(df)
    df = add_sentiment_categories(df)
    df = calculate_impact_score(df)
    
    # Basic features
    print("\n[3/8] Running basic features...")
    emoji_df = analyze_emoji_sentiment(df)
    df, length_stats = analyze_comment_length_sentiment(df)
    stats_dict = calculate_sentiment_statistics(df)
    ranked_df = rank_comments_by_impact(df)
    
    # Medium features
    print("\n[4/8] Running medium features...")
    if video_df is not None and len(video_df) > 0:
        engagement_corr = analyze_sentiment_engagement_correlation(df, video_df)
        category_sentiment = analyze_category_sentiment(df)
        channel_sentiment = analyze_channel_sentiment(df)
        heatmap_data = create_sentiment_heatmap(df)
    else:
        engagement_corr = None
        category_sentiment = None
        channel_sentiment = None
        heatmap_data = None
    
    # Advanced features
    print("\n[5/8] Running advanced features...")
    topic_results = perform_topic_modeling(df)
    if topic_results:
        df = topic_results['df_with_topics']
    
    network_graph = create_comment_network(df)
    aspect_df = analyze_aspect_sentiment(df)
    time_trends = analyze_time_trends(df)
    
    # Visualizations
    print("\n[6/8] Generating visualizations...")
    plot_sentiment_distribution(df)
    plot_wordcloud(df, sentiment_filter='positive')
    plot_wordcloud(df, sentiment_filter='negative')
    if len(emoji_df) > 0:
        plot_emoji_sentiment(emoji_df)
    if category_sentiment is not None:
        plot_sentiment_by_category(category_sentiment)
    if engagement_corr and engagement_corr.get('correlation_matrix') is not None:
        plot_correlation_heatmap(engagement_corr['correlation_matrix'])
    plot_sentiment_categories(df)
    
    # Generate report
    print("\n[7/8] Generating report...")
    generate_report(df, stats_dict)
    
    # Export to database
    print("\n[8/8] Exporting to database...")
    export_to_database(df)
    
    print("\n" + "=" * 80)
    print("Analysis complete!")
    print(f"Results saved to: {OUTPUT_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
