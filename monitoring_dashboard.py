#!/usr/bin/env python3
"""
Streamlit Dashboard for Real-time YouTube Sentiment Monitoring
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import sys
from pathlib import Path
import gc  # Garbage collection for memory management
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def _redact_secrets(text: object) -> str:
    """
    Redact obvious secrets from error messages before displaying them.
    This dashboard may receive HttpError strings that include full request URLs
    with `key=...` query params; never surface those verbatim.
    """
    try:
        s = str(text)
    except Exception:
        return "<unprintable>"

    import re

    # Redact YouTube/Google API key query param
    s = re.sub(r"([?&]key=)[^&\s]+", r"\1<redacted>", s)
    # Generic bearer-style tokens
    s = re.sub(r"(?i)(authorization:\s*bearer\s+)[^\s]+", r"\1<redacted>", s)
    return s

try:
    from src.youtube_monitor import YouTubeSentimentMonitor
    from src.config import DEFAULT_YOUTUBE_API_KEY
    MONITOR_AVAILABLE = True
except ImportError as e:
    MONITOR_AVAILABLE = False
    st.error(f"Monitoring module not available: {_redact_secrets(e)}")


def extract_video_id(input_str: str) -> str:
    """
    Extract YouTube video ID from various input formats:
    - Full URL: https://www.youtube.com/watch?v=VIDEO_ID
    - Short URL: https://youtu.be/VIDEO_ID
    - URL with timestamp: https://www.youtube.com/watch?v=VIDEO_ID&t=1s
    - Just video ID: VIDEO_ID
    
    Args:
        input_str: User input (URL or video ID)
    
    Returns:
        Clean video ID or empty string if not found
    """
    if not input_str or not input_str.strip():
        return ""
    
    input_str = input_str.strip()
    
    # If it's already a clean video ID (11 characters, alphanumeric)
    if len(input_str) == 11 and input_str.replace('-', '').replace('_', '').isalnum():
        return input_str
    
    # Handle full YouTube URLs
    if 'youtube.com/watch' in input_str or 'youtu.be/' in input_str:
        # Extract from youtu.be short URLs
        if 'youtu.be/' in input_str:
            video_id = input_str.split('youtu.be/')[-1].split('?')[0].split('&')[0].split('#')[0]
            return video_id.strip()
        
        # Extract from full YouTube URLs
        if 'v=' in input_str:
            video_id = input_str.split('v=')[-1].split('&')[0].split('?')[0].split('#')[0]
            return video_id.strip()
    
    # If it contains &t= or other query params, try to extract just the video ID part
    if '&' in input_str or '?' in input_str:
        # Try to find a 11-character alphanumeric string (YouTube video ID format)
        import re
        match = re.search(r'[a-zA-Z0-9_-]{11}', input_str)
        if match:
            return match.group(0)
    
    # Return as-is if it looks like a video ID
    if len(input_str) <= 20 and input_str.replace('-', '').replace('_', '').isalnum():
        return input_str
    
    return ""

st.set_page_config(
    page_title="YouTube Sentiment Monitoring",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set matplotlib backend to avoid memory issues
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

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
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-negative {
        background-color: #fee;
        border-left: 4px solid #d00;
    }
    .alert-positive {
        background-color: #efe;
        border-left: 4px solid #0d0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_monitor(api_key):
    """Get monitor instance with caching"""
    if not api_key:
        return None
    try:
        return YouTubeSentimentMonitor(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing monitor: {_redact_secrets(e)}")
        return None

def main():
    """Main dashboard function"""
    st.markdown('<div class="main-header">📊 Real-time YouTube Sentiment Monitoring</div>', unsafe_allow_html=True)
    
    if not MONITOR_AVAILABLE:
        st.error("Monitoring features not available. Please install required packages:")
        st.code("pip install google-api-python-client")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Use default API key if available
        default_key = DEFAULT_YOUTUBE_API_KEY if DEFAULT_YOUTUBE_API_KEY else ''
        api_key = st.text_input(
            "YouTube API Key",
            value=st.session_state.get('api_key', default_key),
            type="password",
            help="Get your API key from https://console.cloud.google.com/apis/credentials"
        )
        
        if api_key:
            st.session_state['api_key'] = api_key
        
        if st.button("🔑 Save API Key"):
            st.session_state['api_key'] = api_key
            st.success("API key saved!")
        
        if default_key and api_key == default_key:
            st.info("✅ Using preconfigured API key")
        
        st.divider()
        
        # Channel/Video management
        st.subheader("📹 Channel & Video Management")
        
        if api_key:
            monitor = get_monitor(api_key)
            
            if monitor:
                # Channel-based monitoring
                st.write("**Add Channel to Monitor:**")
                channel_input = st.text_input(
                    "Channel ID, Username, or URL",
                    placeholder="e.g., UCuAXFkgsw1L7xaCfnd5JJOw or @channelname",
                    key="sidebar_channel_input",
                    help="Enter channel ID, username (with or without @), or full channel URL"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    max_fetch = st.number_input("Max Videos", min_value=10, max_value=100, value=50, step=10, key="sidebar_max_videos")
                with col2:
                    if st.button("🔍 Fetch Channel Videos", key="sidebar_fetch_channel"):
                        if channel_input:
                            with st.spinner("Fetching videos from channel..."):
                                try:
                                    # Determine input type
                                    if channel_input.startswith('http'):
                                        videos = monitor.fetch_channel_videos(
                                            channel_url=channel_input,
                                            max_results=max_fetch,
                                            order="date"
                                        )
                                    elif channel_input.startswith('UC') and len(channel_input) == 24:
                                        videos = monitor.fetch_channel_videos(
                                            channel_id=channel_input,
                                            max_results=max_fetch,
                                            order="date"
                                        )
                                    else:
                                        videos = monitor.fetch_channel_videos(
                                            channel_username=channel_input,
                                            max_results=max_fetch,
                                            order="date"
                                        )
                                    
                                    if videos:
                                        st.session_state['sidebar_fetched_videos'] = videos
                                        st.success(f"✅ Fetched {len(videos)} videos!")
                                    else:
                                        st.warning("No videos found. Check channel ID/username.")
                                except Exception as e:
                                    st.error(f"Error: {_redact_secrets(e)}")
                        else:
                            st.warning("Please enter a channel ID, username, or URL")
                
                # Display fetched videos for selection
                if 'sidebar_fetched_videos' in st.session_state and st.session_state['sidebar_fetched_videos']:
                    st.write("**Select Videos to Monitor:**")
                    videos = st.session_state['sidebar_fetched_videos']
                    
                    # Quick add buttons
                    if st.button("➕ Add All Videos", key="add_all_videos"):
                        added = 0
                        for video in videos:
                            if video['video_id'] not in monitor.video_ids:
                                monitor.add_video(video['video_id'])
                                added += 1
                        if added > 0:
                            st.success(f"Added {added} video(s) to monitoring!")
                            st.rerun()
                    
                    # Video selection with expandable sections
                    for video in videos[:20]:  # Show first 20 to avoid clutter
                        video_id = video['video_id']
                        is_monitored = video_id in monitor.video_ids
                        
                        with st.expander(f"📹 {video['title'][:60]}{'...' if len(video['title']) > 60 else ''} {'✅ Monitored' if is_monitored else ''}", expanded=False):
                            st.caption(f"**Channel:** {video['channel_title']}")
                            st.caption(f"**Published:** {video['published_at'][:10] if video['published_at'] else 'Unknown'}")
                            st.caption(f"**Video ID:** `{video_id}`")
                            
                            if is_monitored:
                                if st.button("➖ Remove from Monitoring", key=f"remove_sidebar_{video_id}"):
                                    monitor.remove_video(video_id)
                                    st.success(f"Removed: {video['title']}")
                                    st.rerun()
                            else:
                                if st.button("➕ Add to Monitoring", key=f"add_sidebar_{video_id}"):
                                    monitor.add_video(video_id)
                                    st.success(f"Added: {video['title']}")
                                    st.rerun()
                    
                    if len(videos) > 20:
                        st.caption(f"💡 Showing first 20 videos. Use **Video Browser** tab to see all {len(videos)} videos and search/filter.")
                
                st.divider()
                
                # Direct video ID input (for individual videos)
                st.write("**Or Add Individual Video:**")
                new_video_id = st.text_input("Video ID", placeholder="Enter YouTube video ID", key="sidebar_video_id")
                if st.button("➕ Add Video ID", key="sidebar_add_video") and new_video_id:
                    monitor.add_video(new_video_id)
                    st.success(f"Added video: {new_video_id}")
                    st.rerun()
                
                st.divider()
                
                # List monitored videos
                if monitor.video_ids:
                    st.write(f"**Monitored Videos ({len(monitor.video_ids)}):**")
                    for vid in monitor.video_ids:
                        video_info = monitor.get_cached_video_info(vid)
                        if not video_info:
                            # Try to fetch and cache
                            video_info = monitor.cache_video_info(vid)
                        
                        video_title = video_info['title'] if video_info else vid
                        channel = video_info['channel_title'] if video_info else "Unknown"
                        
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"**{video_title[:50]}{'...' if len(video_title) > 50 else ''}**")
                            st.caption(f"Channel: {channel} | ID: `{vid[:15]}...`")
                        with col2:
                            if st.button("🗑️", key=f"remove_{vid}"):
                                monitor.remove_video(vid)
                                st.rerun()
                    
                    if st.button("🗑️ Clear All", key="clear_all_videos"):
                        for vid in monitor.video_ids.copy():
                            monitor.remove_video(vid)
                        st.rerun()
                else:
                    st.info("No videos being monitored. Add a channel or video ID above.")
        else:
            st.warning("Enter API key to manage videos")
    
    # Use default API key if not provided
    if not api_key and DEFAULT_YOUTUBE_API_KEY:
        api_key = DEFAULT_YOUTUBE_API_KEY
        st.session_state['api_key'] = api_key
        st.info("✅ Using preconfigured API key")
    
    if not api_key:
        st.warning("⚠️ Please enter your YouTube API key in the sidebar to start monitoring")
        st.info("""
        **How to get a YouTube API key:**
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Create a new project or select existing one
        3. Enable YouTube Data API v3
        4. Create credentials (API Key)
        5. Copy the API key and paste it in the sidebar
        """)
        st.stop()
    
    monitor = get_monitor(api_key)
    if not monitor:
        st.error("Failed to initialize monitor. Check your API key.")
        st.stop()
    
    if not monitor.video_ids:
        st.info("📹 Add a channel or video IDs in the sidebar to start monitoring")
        st.stop()
    
    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📹 Video Browser",
        "📈 Live Monitoring",
        "📊 Sentiment History",
        "🚨 Alerts",
        "⚙️ Manual Check"
    ])
    
    # Tab 1: Video Browser
    with tab1:
        st.subheader("Browse and Select Videos")
        st.markdown("Fetch videos from a YouTube channel and select them for analysis")
        
        st.info("💡 **Tip**: You can enter:\n- Channel ID (e.g., `UCuAXFkgsw1L7xaCfnd5JJOw`)\n- Channel username (e.g., `rickastley` or `@rickastley`)\n- Channel URL (e.g., `https://www.youtube.com/@rickastley`)")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            channel_input = st.text_input(
                "Channel ID, Username, or URL",
                placeholder="Enter channel ID, username, or full URL",
                help="Find your channel ID in YouTube Studio > Settings > Channel > Advanced settings"
            )
        
        with col2:
            max_videos = st.number_input("Max Videos", min_value=10, max_value=100, value=50, step=10)
        
        # Analysis settings
        st.markdown("**Analysis Settings:**")
        col_settings1, col_settings2 = st.columns(2)
        
        with col_settings1:
            max_comments_analysis = st.number_input(
                "Max Comments per Video",
                min_value=10,
                max_value=1000,
                value=st.session_state.get('max_comments_analysis', 100),
                step=10,
                help="Number of comments to analyze when clicking 'Analyze Now'"
            )
            st.session_state['max_comments_analysis'] = max_comments_analysis
        
        with col_settings2:
            order_by = st.selectbox("Order By", ["date", "rating", "relevance", "title", "viewCount"], index=0)
        
        # Fetch button
        if st.button("🔍 Fetch Videos", type="primary"):
            if channel_input:
                with st.spinner("Fetching videos from channel..."):
                    try:
                        # Determine input type
                        if channel_input.startswith('http'):
                            # Full URL
                            videos = monitor.fetch_channel_videos(
                                channel_url=channel_input,
                                max_results=max_videos,
                                order=order_by
                            )
                        elif channel_input.startswith('UC') and len(channel_input) == 24:
                            # Channel ID
                            videos = monitor.fetch_channel_videos(
                                channel_id=channel_input,
                                max_results=max_videos,
                                order=order_by
                            )
                        else:
                            # Username (with or without @)
                            videos = monitor.fetch_channel_videos(
                                channel_username=channel_input,
                                max_results=max_videos,
                                order=order_by
                            )
                        
                        if videos:
                            st.session_state['fetched_videos'] = videos
                            st.success(f"✅ Fetched {len(videos)} videos!")
                        else:
                            st.warning("No videos found. Check channel ID/username.")
                    except Exception as e:
                        st.error(f"Error fetching videos: {_redact_secrets(e)}")
            else:
                st.warning("Please enter a channel ID or username")
        
        # Display analysis settings info
        if 'max_comments_analysis' in st.session_state:
            st.caption(f"ℹ️ Analysis will use up to **{st.session_state['max_comments_analysis']} comments** per video")
        
        # Display fetched videos
        if 'fetched_videos' in st.session_state and st.session_state['fetched_videos']:
            videos = st.session_state['fetched_videos']
            st.subheader(f"📹 Found {len(videos)} Videos")
            
            # Search/filter
            search_term = st.text_input("🔍 Search videos by title", key="video_search")
            if search_term:
                filtered_videos = [v for v in videos if search_term.lower() in v['title'].lower()]
            else:
                filtered_videos = videos
            
            # Display videos in a selectable list
            selected_video_idx = None
            for idx, video in enumerate(filtered_videos):
                with st.expander(f"🎬 {video['title']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Channel:** {video['channel_title']}")
                        st.write(f"**Published:** {video['published_at'][:10] if video['published_at'] else 'Unknown'}")
                        st.write(f"**Video ID:** `{video['video_id']}`")
                        if video['description']:
                            st.caption(f"*{video['description']}*")
                    with col2:
                        if st.button("➕ Add to Monitoring", key=f"add_{video['video_id']}"):
                            monitor.add_video(video['video_id'])
                            st.success(f"Added: {video['title']}")
                            st.rerun()
                        
                        if st.button("📊 Analyze Now", key=f"analyze_{video['video_id']}"):
                            selected_video_idx = idx
                            st.session_state['analyze_video'] = video['video_id']
                            st.rerun()
            
            # Analysis results
            if 'analyze_video' in st.session_state:
                st.divider()
                st.subheader("📊 Analysis Results")
                
                # Get max comments from session state or use default
                max_comments = st.session_state.get('max_comments_analysis', 100)
                
                with st.spinner(f"Analyzing up to {max_comments} comments..."):
                    # Use analyze_video_comments to get detailed results with comments_df
                    result = monitor.analyze_video_comments(st.session_state['analyze_video'], max_comments=max_comments)
                    
                    if result['status'] == 'success':
                        # Save snapshot to database for Sentiment History
                        monitor.monitor_video(st.session_state['analyze_video'], max_comments, check_alerts=False)
                        
                        # Add video to monitoring list so it appears in Live Monitoring tab
                        if st.session_state['analyze_video'] not in monitor.video_ids:
                            monitor.add_video(st.session_state['analyze_video'])
                        
                        st.success(f"✅ Analysis complete for: **{result['video_title']}**")
                        
                        # Store analyzed video in session state for Sentiment History
                        if 'analyzed_videos' not in st.session_state:
                            st.session_state['analyzed_videos'] = {}
                        st.session_state['analyzed_videos'][st.session_state['analyze_video']] = {
                            'video_id': st.session_state['analyze_video'],
                            'video_title': result['video_title'],
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Avg Sentiment", f"{result['avg_sentiment']:.3f}")
                        with col2:
                            st.metric("Total Comments", f"{result['total_comments']:,}")
                        with col3:
                            st.metric("Positive", f"{result['positive_pct']:.1f}%")
                        with col4:
                            st.metric("Negative", f"{result['negative_pct']:.1f}%")
                        
                        # Sentiment distribution
                        if 'comments_df' in result and not result['comments_df'].empty:
                            comments_df = result['comments_df']
                            
                            # Sentiment Distribution Chart
                            st.subheader("📊 Sentiment Distribution")
                            fig, ax = plt.subplots(figsize=(10, 6))
                            sns.histplot(comments_df['Polarity'], kde=True, bins=30, ax=ax, color='steelblue')
                            ax.axvline(result['avg_sentiment'], color='r', linestyle='--', 
                                     label=f"Mean: {result['avg_sentiment']:.3f}")
                            ax.set_xlabel('Sentiment Polarity', fontsize=12)
                            ax.set_ylabel('Frequency', fontsize=12)
                            ax.set_title('Sentiment Distribution', fontsize=14, fontweight='bold')
                            ax.legend()
                            ax.grid(alpha=0.3)
                            st.pyplot(fig)
                            plt.close()
                            
                            # Sentiment Category Breakdown
                            st.subheader("📈 Sentiment Category Breakdown")
                            if 'sentiment_category' in comments_df.columns:
                                sentiment_counts = comments_df['sentiment_category'].value_counts()
                                sentiment_order = ['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive']
                                
                                # Filter out categories with zero count
                                filtered_counts = {cat: sentiment_counts.get(cat, 0) for cat in sentiment_order if sentiment_counts.get(cat, 0) > 0}
                                filtered_order = list(filtered_counts.keys())
                                filtered_values = list(filtered_counts.values())
                                
                                if filtered_values:
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        # Pie chart with improved label positioning
                                        colors = ['#d62728', '#ff7f0e', '#bcbd22', '#2ca02c', '#1f77b4']
                                        color_map = {cat: colors[sentiment_order.index(cat)] for cat in filtered_order if cat in sentiment_order}
                                        pie_colors = [color_map.get(cat, '#808080') for cat in filtered_order]
                                        
                                        fig, ax = plt.subplots(figsize=(8, 8))
                                        
                                        # Use wedges to control label positioning
                                        wedges, texts, autotexts = ax.pie(
                                            filtered_values, 
                                            labels=filtered_order, 
                                            autopct='%1.1f%%',
                                            colors=pie_colors, 
                                            startangle=90,
                                            pctdistance=0.85,  # Distance of percentage labels from center
                                            labeldistance=1.1,  # Distance of category labels from center
                                            textprops={'fontsize': 10, 'fontweight': 'bold'},
                                            explode=[0.05 if v < sum(filtered_values) * 0.05 else 0 for v in filtered_values]  # Slight explode for small slices
                                        )
                                        
                                        # Improve text readability
                                        for autotext in autotexts:
                                            autotext.set_color('white')
                                            autotext.set_fontweight('bold')
                                            autotext.set_fontsize(9)
                                        
                                        # Adjust label positions to prevent overlap
                                        for text in texts:
                                            text.set_fontsize(10)
                                            text.set_fontweight('bold')
                                        
                                        ax.set_title('Sentiment Distribution (Pie Chart)', fontsize=13, fontweight='bold', pad=20)
                                        plt.tight_layout()
                                        st.pyplot(fig)
                                        plt.close()
                                    
                                    with col2:
                                        # Bar chart
                                        fig, ax = plt.subplots(figsize=(8, 6))
                                        bars = ax.bar(filtered_order, filtered_values, 
                                                     color=[color_map.get(cat, '#808080') for cat in filtered_order], 
                                                     alpha=0.8, edgecolor='black')
                                        ax.set_xlabel('Sentiment Category', fontsize=12, fontweight='bold')
                                        ax.set_ylabel('Number of Comments', fontsize=12, fontweight='bold')
                                        ax.set_title('Sentiment Category Distribution', fontsize=14, fontweight='bold')
                                        ax.tick_params(axis='x', rotation=15)
                                        ax.grid(axis='y', alpha=0.3)
                                        
                                        # Add percentage labels on bars
                                        for i, bar in enumerate(bars):
                                            height = bar.get_height()
                                            percentage = (filtered_values[i] / sum(filtered_values)) * 100
                                            ax.text(bar.get_x() + bar.get_width()/2., height,
                                                   f'{int(height)}\n({percentage:.1f}%)',
                                                   ha='center', va='bottom', fontsize=10, fontweight='bold')
                                        st.pyplot(fig)
                                        plt.close()
                            
                            # Top Comments Section
                            st.subheader("💬 Sample Comments")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Most Positive Comments:**")
                                top_positive = comments_df.nlargest(5, 'Polarity')
                                for idx, (_, row) in enumerate(top_positive.iterrows(), 1):
                                    comment_text = str(row['comment_text'])[:150]
                                    st.markdown(f"""
                                    <div style="background-color: #e8f5e9; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #4caf50;">
                                        <strong>[{row['Polarity']:.3f}]</strong> {comment_text}
                                        {('...' if len(str(row['comment_text'])) > 150 else '')}
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            with col2:
                                st.write("**Most Negative Comments:**")
                                top_negative = comments_df.nsmallest(5, 'Polarity')
                                for idx, (_, row) in enumerate(top_negative.iterrows(), 1):
                                    comment_text = str(row['comment_text'])[:150]
                                    st.markdown(f"""
                                    <div style="background-color: #ffebee; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #f44336;">
                                        <strong>[{row['Polarity']:.3f}]</strong> {comment_text}
                                        {('...' if len(str(row['comment_text'])) > 150 else '')}
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Statistics Summary
                            st.subheader("📋 Statistics Summary")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Positive Comments", f"{result.get('positive_count', 0):,}", 
                                         f"{result['positive_pct']:.1f}%")
                            with col2:
                                st.metric("Neutral Comments", f"{result.get('neutral_count', 0):,}", 
                                         f"{result.get('neutral_pct', 0):.1f}%")
                            with col3:
                                st.metric("Negative Comments", f"{result.get('negative_count', 0):,}", 
                                         f"{result['negative_pct']:.1f}%")
                            
                            # Download option
                            st.subheader("💾 Export Data")
                            csv = comments_df[['comment_text', 'Polarity', 'sentiment_category']].to_csv(index=False)
                            st.download_button(
                                label="📥 Download Comments CSV",
                                data=csv,
                                file_name=f"sentiment_analysis_{st.session_state['analyze_video']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    else:
                        st.error(f"❌ {result.get('message', 'Analysis failed')}")
                    
                    # Clear analyze_video after showing results
                    if st.button("Clear Results"):
                        st.session_state.pop('analyze_video', None)
                        st.rerun()
    
    # Tab 2: Live Monitoring
    with tab2:
        st.subheader("Current Sentiment Status")
        
        # Select video with titles - include both monitored videos and analyzed videos from Video Browser
        video_options = []
        video_id_to_title = {}
        
        # Add monitored videos
        for vid in monitor.video_ids:
            video_info = monitor.get_cached_video_info(vid)
            if not video_info:
                video_info = monitor.cache_video_info(vid)
            title = video_info['title'] if video_info else vid
            video_options.append(f"{title} ({vid})")
            video_id_to_title[vid] = title
        
        # Add analyzed videos from Video Browser (if any)
        if 'analyzed_videos' in st.session_state and st.session_state['analyzed_videos']:
            for vid, info in st.session_state['analyzed_videos'].items():
                if vid not in video_id_to_title:
                    title = info.get('video_title', vid)
                    video_options.append(f"{title} ({vid})")
                    video_id_to_title[vid] = title
                # Also add to monitoring if not already there (for tracking)
                if vid not in monitor.video_ids:
                    monitor.add_video(vid)
        
        if video_options:
            col_select, col_refresh = st.columns([3, 1])
            with col_select:
                selected_option = st.selectbox("Select Video", video_options, key="live_monitoring_video")
                selected_video = selected_option.split(" (")[-1].rstrip(")")
            with col_refresh:
                st.write("")  # Spacer
                st.write("")  # Spacer
                if st.button("🔄 Refresh Now", type="primary"):
                    with st.spinner("Refreshing comments..."):
                        max_comments = st.session_state.get('max_comments_analysis', 100)
                        result = monitor.monitor_video(selected_video, max_comments, check_alerts=True)
                        if result['status'] == 'success':
                            st.success("✅ Comments refreshed!")
                            st.rerun()
                        else:
                            st.error(f"❌ Refresh failed: {result.get('message', 'Unknown error')}")
        else:
            selected_video = None
        
        if selected_video:
            # Display video info
            video_info = monitor.get_cached_video_info(selected_video)
            if not video_info:
                video_info = monitor.cache_video_info(selected_video)
            
            if video_info:
                st.markdown(f"### 📹 {video_info['title']}")
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.caption(f"**Channel:** {video_info['channel_title']}")
                with col_info2:
                    st.caption(f"**Views:** {int(video_info['view_count']):,}")
                with col_info3:
                    st.caption(f"**Video ID:** `{selected_video}`")
            
            # Get latest sentiment
            history = monitor.get_sentiment_history(selected_video, hours=24)
            
            if not history.empty:
                latest = history.iloc[-1]
                
                # Convert to numeric types to avoid division errors
                total_comments = pd.to_numeric(latest['total_comments'], errors='coerce')
                positive_count = pd.to_numeric(latest['positive_count'], errors='coerce')
                negative_count = pd.to_numeric(latest['negative_count'], errors='coerce')
                avg_sentiment = pd.to_numeric(latest['avg_sentiment'], errors='coerce')
                
                # Handle division by zero or None values
                if pd.isna(total_comments) or total_comments == 0:
                    positive_pct = 0.0
                    negative_pct = 0.0
                else:
                    positive_pct = (positive_count / total_comments * 100) if not pd.isna(positive_count) else 0.0
                    negative_pct = (negative_count / total_comments * 100) if not pd.isna(negative_count) else 0.0
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Avg Sentiment", f"{avg_sentiment:.3f}" if not pd.isna(avg_sentiment) else "N/A")
                
                with col2:
                    st.metric("Total Comments", f"{int(total_comments):,}" if not pd.isna(total_comments) else "0")
                
                with col3:
                    st.metric("Positive", f"{positive_pct:.1f}%")
                
                with col4:
                    st.metric("Negative", f"{negative_pct:.1f}%")

                st.divider()
                st.subheader("💬 Top Comments (latest snapshot)")

                colf1, colf2, colf3, colf4 = st.columns([1.2, 1.2, 1, 1.6])
                with colf1:
                    order_by = st.selectbox(
                        "Sort",
                        options=[("most_liked", "Most liked"), ("newest", "Newest")],
                        format_func=lambda x: x[1],
                        index=0,
                        key="top_comments_sort",
                    )[0]
                with colf2:
                    sentiment_filter = st.selectbox(
                        "Sentiment",
                        options=[("all", "All"), ("positive", "Positive"), ("neutral", "Neutral"), ("negative", "Negative")],
                        format_func=lambda x: x[1],
                        index=0,
                        key="top_comments_sentiment",
                    )[0]
                with colf3:
                    min_likes = st.number_input("Min likes", min_value=0, max_value=100000, value=0, step=1, key="top_comments_min_likes")
                with colf4:
                    keyword = st.text_input("Keyword", value="", placeholder="search in comment text", key="top_comments_keyword")

                limit = st.slider("Max comments to show", min_value=10, max_value=200, value=50, step=10, key="top_comments_limit")

                try:
                    top_df = monitor.get_latest_comments_snapshot(
                        selected_video,
                        limit=int(limit),
                        order_by=order_by,
                        sentiment_filter=sentiment_filter,
                        keyword=keyword,
                        min_likes=int(min_likes),
                    )
                except Exception as e:
                    st.error(f"Failed to load comments snapshot: {_redact_secrets(e)}")
                    top_df = pd.DataFrame()

                if top_df.empty:
                    st.info("No snapshot comments found yet. Click **Refresh Now** to fetch and analyze comments.")
                else:
                    # Compact rendering
                    for _, row in top_df.iterrows():
                        bucket = str(row.get("sentiment_bucket", "neutral"))
                        s = row.get("sentiment", None)
                        likes = int(row.get("like_count", 0) or 0)
                        author = str(row.get("author", ""))
                        published_at = str(row.get("published_at", "") or "")
                        text = str(row.get("comment_text", "") or "")

                        if bucket == "positive":
                            border = "#2ca02c"
                            bg = "#e8f5e9"
                        elif bucket == "negative":
                            border = "#d62728"
                            bg = "#ffebee"
                        else:
                            border = "#6c757d"
                            bg = "#f1f3f5"

                        score_str = f"{float(s):.3f}" if s is not None and pd.notna(s) else "N/A"
                        meta = f"{author} • 👍 {likes}"
                        if published_at:
                            meta = f"{meta} • {published_at[:19].replace('T', ' ')}"

                        st.markdown(
                            f"""
                            <div style="background-color: {bg}; padding: 10px; margin: 6px 0; border-radius: 6px; border-left: 4px solid {border};">
                              <div style="font-weight: 700;">[{bucket}] Polarity: {score_str}</div>
                              <div style="color: #333; margin-top: 4px;">{text[:400]}{'...' if len(text) > 400 else ''}</div>
                              <div style="color: #555; font-size: 0.85rem; margin-top: 6px;">{meta}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    # Per-language sentiment summary from latest snapshot
                    lang_df = monitor.get_latest_comments_snapshot(
                        selected_video,
                        limit=5000,
                        order_by="most_liked",
                        sentiment_filter="all",
                        keyword="",
                        min_likes=0,
                    )
                    if not lang_df.empty and "language" in lang_df.columns:
                        lang_stats = (
                            lang_df.groupby("language")
                            .agg(
                                count=("comment_id", "count"),
                                avg_sentiment=("sentiment", "mean"),
                            )
                            .reset_index()
                            .sort_values("count", ascending=False)
                        )

                        # Map ISO codes to human-friendly names (fallback to code)
                        iso_map = {
                            "en": "English",
                            "de": "German",
                            "fr": "French",
                            "es": "Spanish",
                            "it": "Italian",
                            "pt": "Portuguese",
                            "ru": "Russian",
                            "ja": "Japanese",
                            "ko": "Korean",
                            "hi": "Hindi",
                            "id": "Indonesian",
                            "pl": "Polish",
                            "ro": "Romanian",
                            "nl": "Dutch",
                            "tr": "Turkish",
                            "sv": "Swedish",
                            "fi": "Finnish",
                            "da": "Danish",
                            "no": "Norwegian",
                            "cs": "Czech",
                            "bg": "Bulgarian",
                            "hr": "Croatian",
                            "el": "Greek",
                            "uk": "Ukrainian",
                            "ar": "Arabic",
                            "fa": "Persian",
                            "he": "Hebrew",
                            "th": "Thai",
                            "vi": "Vietnamese",
                            "zh-cn": "Chinese (Simplified)",
                            "zh-tw": "Chinese (Traditional)",
                            "unknown": "Unknown",
                        }

                        lang_stats["language_name"] = lang_stats["language"].astype(str).map(
                            lambda c: iso_map.get(c.lower(), c)
                        )
                        st.subheader("🌍 Per-language Sentiment (latest snapshot)")
                        col_l1, col_l2 = st.columns([2, 1])
                        with col_l1:
                            fig_lang = px.bar(
                                lang_stats,
                                x="language_name",
                                y="avg_sentiment",
                                hover_data=["count"],
                                title="Average sentiment by language",
                            )
                            fig_lang.update_layout(height=320)
                            st.plotly_chart(fig_lang, width="stretch")
                            del fig_lang
                            gc.collect()
                        with col_l2:
                            st.dataframe(
                                lang_stats[["language_name", "language", "count", "avg_sentiment"]],
                                width="stretch",
                                hide_index=True,
                            )
                
                # Ensure numeric types for plotting (create a copy to avoid modifying original)
                history_plot = history.copy()
                history_plot['avg_sentiment'] = pd.to_numeric(history_plot['avg_sentiment'], errors='coerce')
                history_plot['positive_count'] = pd.to_numeric(history_plot['positive_count'], errors='coerce').fillna(0)
                history_plot['negative_count'] = pd.to_numeric(history_plot['negative_count'], errors='coerce').fillna(0)
                history_plot['neutral_count'] = pd.to_numeric(history_plot['neutral_count'], errors='coerce').fillna(0)
                
                # Sentiment trend
                st.subheader("Sentiment Trend (Last 24 Hours)")
                fig = go.Figure()
                
                # Sort by timestamp to ensure proper line plotting
                history_sorted = history_plot.sort_values('timestamp')
                
                fig.add_trace(go.Scatter(
                    x=history_sorted['timestamp'],
                    y=history_sorted['avg_sentiment'],
                    mode='lines+markers',
                    name='Average Sentiment',
                    line=dict(color='steelblue', width=2),
                    marker=dict(size=8)
                ))
                fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                             annotation_text="Neutral")
                fig.update_layout(
                    xaxis_title="Time",
                    yaxis_title="Sentiment",
                    height=400,
                    hovermode='x unified',
                    showlegend=True
                )
                st.plotly_chart(fig, width='stretch')
                del fig  # Explicit cleanup
                gc.collect()  # Force garbage collection
                
                # Comment counts over time
                st.subheader("Comment Distribution Over Time")
                fig = go.Figure()
                
                # Use bar chart if only one data point, otherwise use stacked area
                if len(history_sorted) == 1:
                    # Single data point - use bar chart
                    fig.add_trace(go.Bar(
                        x=['Positive', 'Negative', 'Neutral'],
                        y=[
                            float(history_sorted['positive_count'].iloc[0]),
                            float(history_sorted['negative_count'].iloc[0]),
                            float(history_sorted['neutral_count'].iloc[0])
                        ],
                        marker=dict(color=['green', 'red', 'gray']),
                        name='Comments'
                    ))
                    fig.update_layout(
                        xaxis_title="Sentiment Category",
                        yaxis_title="Number of Comments",
                        height=400,
                        showlegend=False
                    )
                else:
                    # Multiple data points - use stacked area chart
                    fig.add_trace(go.Scatter(
                        x=history_sorted['timestamp'],
                        y=history_sorted['positive_count'],
                        mode='lines',
                        name='Positive',
                        stackgroup='one',
                        fillcolor='green',
                        line=dict(width=0)
                    ))
                    fig.add_trace(go.Scatter(
                        x=history_sorted['timestamp'],
                        y=history_sorted['negative_count'],
                        mode='lines',
                        name='Negative',
                        stackgroup='one',
                        fillcolor='red',
                        line=dict(width=0)
                    ))
                    fig.add_trace(go.Scatter(
                        x=history_sorted['timestamp'],
                        y=history_sorted['neutral_count'],
                        mode='lines',
                        name='Neutral',
                        stackgroup='one',
                        fillcolor='gray',
                        line=dict(width=0)
                    ))
                    fig.update_layout(
                        xaxis_title="Time",
                        yaxis_title="Number of Comments",
                        height=400,
                        hovermode='x unified',
                        showlegend=True
                    )
                st.plotly_chart(fig, width='stretch')
                del fig, history_sorted, history_plot  # Explicit cleanup
                gc.collect()  # Force garbage collection
            else:
                st.info("No monitoring data yet. Run a manual check or start the monitoring service.")
    
    # Tab 3: Sentiment History
    with tab3:
        st.subheader("Historical Sentiment Analysis")
        
        # Collect videos from both monitored videos and analyzed videos from Video Browser
        video_options = []
        video_id_to_title = {}
        
        # Add monitored videos
        for vid in monitor.video_ids:
            video_info = monitor.get_cached_video_info(vid)
            if not video_info:
                video_info = monitor.cache_video_info(vid)
            title = video_info['title'] if video_info else vid
            video_options.append(f"{title} ({vid})")
            video_id_to_title[vid] = title
        
        # Add analyzed videos from Video Browser (if any)
        if 'analyzed_videos' in st.session_state and st.session_state['analyzed_videos']:
            for vid, info in st.session_state['analyzed_videos'].items():
                if vid not in video_id_to_title:
                    title = info.get('video_title', vid)
                    video_options.append(f"{title} ({vid})")
                    video_id_to_title[vid] = title
        
        if video_options:
            selected_option = st.selectbox("Select Video", video_options, key="history_video")
            selected_video = selected_option.split(" (")[-1].rstrip(")")
        else:
            selected_video = None
            st.info("No videos available. Analyze videos in the Video Browser tab or add videos to monitoring.")
        
        hours = st.slider("Hours of History", 1, 168, 24, key="history_hours")
        
        if selected_video:
            # Check if video has history in database, if not, try to get from analyzed videos
            history = monitor.get_sentiment_history(selected_video, hours=hours)
            
            # If no history in database but video was analyzed, show message
            if history.empty:
                if 'analyzed_videos' in st.session_state and selected_video in st.session_state['analyzed_videos']:
                    st.info("💡 This video was analyzed but has no historical data yet. Use the refresh button in Live Monitoring to create a snapshot.")
                else:
                    st.info("No historical data available. Run analysis in Video Browser or start monitoring.")
            
            if not history.empty:
                # Ensure numeric types for calculations
                history['avg_sentiment'] = pd.to_numeric(history['avg_sentiment'], errors='coerce')
                
                # Statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_sent = history['avg_sentiment'].mean()
                    st.metric("Avg Sentiment", f"{avg_sent:.3f}" if not pd.isna(avg_sent) else "N/A")
                with col2:
                    min_sent = history['avg_sentiment'].min()
                    st.metric("Min Sentiment", f"{min_sent:.3f}" if not pd.isna(min_sent) else "N/A")
                with col3:
                    max_sent = history['avg_sentiment'].max()
                    st.metric("Max Sentiment", f"{max_sent:.3f}" if not pd.isna(max_sent) else "N/A")
                
                # Detailed table
                st.subheader("Detailed History")
                st.dataframe(history, width='stretch')
                
                # Download button
                csv = history.to_csv(index=False)
                st.download_button(
                    label="📥 Download History CSV",
                    data=csv,
                    file_name=f"sentiment_history_{selected_video}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No historical data available")

            st.divider()
            st.subheader("🔎 Keyword & Hashtag Trends")

            colk1, colk2, colk3, colk4, colk5 = st.columns([1, 1, 1, 1, 1.2])
            with colk1:
                trend_hours = st.slider("Window (hours)", 1, 168, min(24, int(hours)), key="trend_hours")
            with colk2:
                top_n = st.number_input("Top terms", min_value=3, max_value=30, value=10, step=1, key="trend_top_n")
            with colk3:
                ngram = st.selectbox("N-gram", options=[1, 2, 3], index=0, key="trend_ngram")
            with colk4:
                bucket_minutes = st.selectbox("Bucket", options=[5, 15, 30, 60, 120, 240], index=3, key="trend_bucket")
            with colk5:
                include_hashtags = st.checkbox("Include hashtags", value=True, key="trend_hashtags")

            time_basis = st.radio(
                "Time basis",
                options=[("snapshot", "Snapshot time (when you refreshed)"), ("published", "Comment published time")],
                format_func=lambda x: x[1],
                horizontal=True,
                index=0,
                key="trend_time_basis",
            )[0]

            min_term_count = st.number_input("Min total count", min_value=1, max_value=50, value=2, step=1, key="trend_min_count")

            try:
                trend = monitor.get_keyword_trends(
                    selected_video,
                    hours=int(trend_hours),
                    top_n=int(top_n),
                    ngram=int(ngram),
                    include_hashtags=bool(include_hashtags),
                    bucket_minutes=int(bucket_minutes),
                    min_term_count=int(min_term_count),
                    time_basis=time_basis,
                )
                top_terms_df = trend.get("top_terms", pd.DataFrame())
                ts_df = trend.get("timeseries", pd.DataFrame())
            except Exception as e:
                st.error(f"Failed to compute trends: {_redact_secrets(e)}")
                top_terms_df = pd.DataFrame()
                ts_df = pd.DataFrame()

            if top_terms_df.empty or ts_df.empty:
                st.info("No trends yet. Click **Refresh Now** a few times over time to build snapshots, then come back here.")
            else:
                # Line chart: term frequency over time (bucketed)
                fig = px.line(
                    ts_df,
                    x="timestamp",
                    y="count",
                    color="term",
                    markers=True,
                    title="Top terms over time (counts per bucket)",
                )
                fig.update_layout(height=420, hovermode="x unified", legend_title_text="Term")
                st.plotly_chart(fig, width="stretch")
                del fig
                gc.collect()

                col_tbl1, col_tbl2 = st.columns([1, 1])
                with col_tbl1:
                    st.markdown("**Top terms (total in window)**")
                    st.dataframe(top_terms_df, width="stretch", hide_index=True)
                with col_tbl2:
                    st.markdown("**Raw time series (bucketed)**")
                    st.dataframe(ts_df.sort_values(["timestamp", "count"], ascending=[False, False]), width="stretch", hide_index=True)
    
    # Tab 4: Alerts
    with tab4:
        st.subheader("Recent Alerts")
        
        hours = st.slider("Hours to Look Back", 1, 168, 24, key="alert_hours")
        
        alerts_df = monitor.get_recent_alerts(hours=hours)
        
        if not alerts_df.empty:
            st.write(f"**{len(alerts_df)} alert(s) in the last {hours} hours**")
            
            for _, alert in alerts_df.iterrows():
                # Get video title for alert
                video_info = monitor.get_cached_video_info(alert['video_id'])
                if not video_info:
                    video_info = monitor.cache_video_info(alert['video_id'])
                video_title = video_info['title'] if video_info else alert['video_id']
                
                alert_class = "alert-negative" if alert['current_value'] < 0 else "alert-positive"
                alert_type = str(alert.get("alert_type", "alert"))
                msg = _redact_secrets(alert.get("message", ""))
                ts = str(alert.get("timestamp", ""))
                vid = str(alert.get("video_id", ""))

                # Parse details JSON (if present)
                details_raw = alert.get("details", None)
                details = None
                if details_raw is not None and str(details_raw).strip():
                    try:
                        details = json.loads(str(details_raw))
                    except Exception:
                        details = {"raw": _redact_secrets(details_raw)}

                header = f"{alert_type} — {video_title}"
                with st.expander(header, expanded=False):
                    st.markdown(f"""
                    <div class="alert-box {alert_class}">
                        <strong>{alert_type}</strong> - {video_title}<br>
                        {msg}<br>
                        <small>Video ID: {vid} | {ts}</small>
                    </div>
                    """, unsafe_allow_html=True)

                    if details:
                        reason = details.get("reason")
                        if reason:
                            st.caption(f"**Reason:** `{reason}`")

                        # Show key numeric fields if present
                        numeric_keys = ["z", "value", "mean", "std", "ewma_mean", "ewma_std", "delta", "sigma", "alpha"]
                        present = {k: details.get(k) for k in numeric_keys if details.get(k) is not None}
                        if present:
                            st.markdown("**Signals**")
                            st.json(present)

                        examples = details.get("examples") or []
                        if isinstance(examples, list) and examples:
                            st.markdown("**Example comments**")
                            for ex in examples[:5]:
                                st.markdown(f"- {_redact_secrets(ex)}")

                        if "raw" in details:
                            st.markdown("**Details (raw)**")
                            st.code(str(details["raw"]))
                    else:
                        st.caption("No structured details available for this alert.")
            
            # Alerts table
            st.subheader("Alerts Table")
            st.dataframe(alerts_df, width='stretch')
        else:
            st.info("No alerts in the selected time period")
    
    # Tab 5: Manual Check
    with tab5:
        st.subheader("Manual Video Check")
        st.info("💡 You can enter a YouTube URL or just the video ID (e.g., `dQw4w9WgXcQ` or `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)")
        
        video_input = st.text_input("Video ID or URL to Check", placeholder="Enter YouTube video ID or URL")
        max_comments = st.slider("Max Comments", 10, 500, 100)
        
        # Extract video ID from input
        video_id = extract_video_id(video_input) if video_input else ""
        
        if video_input and not video_id:
            st.warning("⚠️ Could not extract video ID from input. Please enter a valid YouTube URL or video ID.")
        
        if st.button("🔍 Check Now") and video_id:
            with st.spinner(f"Fetching and analyzing comments for video ID: {video_id}..."):
                try:
                    # Cache video info first
                    video_info = monitor.cache_video_info(video_id)
                    if video_info:
                        st.info(f"📹 **{video_info['title']}** by {video_info['channel_title']}")
                    else:
                        st.warning(f"⚠️ Could not fetch video info. Proceeding with analysis...")
                    
                    result = monitor.monitor_video(video_id, max_comments, check_alerts=True)
                    
                    if result['status'] == 'no_comments':
                        st.error("❌ No comments found for this video. The video might have comments disabled, be private, or the video ID might be incorrect.")
                        st.info(f"Video ID used: `{video_id}`")
                        if video_input != video_id:
                            st.caption(f"Original input: `{video_input}`")
                    elif result['status'] == 'analysis_failed':
                        st.error("❌ Failed to analyze comments. Please check the video ID and try again.")
                        st.info(f"Video ID used: `{video_id}`")
                    elif result['status'] == 'success':
                        st.success("✅ Analysis complete!")
                        
                        # Metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Avg Sentiment", f"{result['avg_sentiment']:.3f}")
                        with col2:
                            st.metric("Total Comments", f"{result['total_comments']:,}")
                        with col3:
                            st.metric("Positive", f"{result['positive_pct']:.1f}%")
                        with col4:
                            st.metric("Negative", f"{result['negative_pct']:.1f}%")
                        
                        if result.get('alerts', 0) > 0:
                            st.warning(f"🚨 {result['alerts']} alert(s) triggered!")
                        
                        # Visualizations
                        if 'comments_df' in result and not result['comments_df'].empty:
                            comments_df = result['comments_df']
                            
                            # Sentiment Distribution Chart
                            st.subheader("📊 Sentiment Distribution")
                            fig, ax = plt.subplots(figsize=(10, 6))
                            sns.histplot(comments_df['Polarity'], kde=True, bins=30, ax=ax, color='steelblue')
                            ax.axvline(result['avg_sentiment'], color='r', linestyle='--', 
                                     label=f"Mean: {result['avg_sentiment']:.3f}")
                            ax.set_xlabel('Sentiment Polarity', fontsize=12)
                            ax.set_ylabel('Frequency', fontsize=12)
                            ax.set_title('Sentiment Distribution', fontsize=14, fontweight='bold')
                            ax.legend()
                            ax.grid(alpha=0.3)
                            st.pyplot(fig)
                            plt.close()
                            
                            # Sentiment Category Breakdown
                            st.subheader("📈 Sentiment Category Breakdown")
                            if 'sentiment_category' in comments_df.columns:
                                sentiment_counts = comments_df['sentiment_category'].value_counts()
                                sentiment_order = ['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive']
                                
                                # Filter out categories with zero count
                                filtered_counts = {cat: sentiment_counts.get(cat, 0) for cat in sentiment_order if sentiment_counts.get(cat, 0) > 0}
                                filtered_order = list(filtered_counts.keys())
                                filtered_values = list(filtered_counts.values())
                                
                                if filtered_values:
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        # Pie chart with improved label positioning
                                        colors = ['#d62728', '#ff7f0e', '#bcbd22', '#2ca02c', '#1f77b4']
                                        color_map = {cat: colors[sentiment_order.index(cat)] for cat in filtered_order if cat in sentiment_order}
                                        pie_colors = [color_map.get(cat, '#808080') for cat in filtered_order]
                                        
                                        fig, ax = plt.subplots(figsize=(8, 8))
                                        
                                        # Use wedges to control label positioning
                                        wedges, texts, autotexts = ax.pie(
                                            filtered_values, 
                                            labels=filtered_order, 
                                            autopct='%1.1f%%',
                                            colors=pie_colors, 
                                            startangle=90,
                                            pctdistance=0.85,  # Distance of percentage labels from center
                                            labeldistance=1.1,  # Distance of category labels from center
                                            textprops={'fontsize': 10, 'fontweight': 'bold'},
                                            explode=[0.05 if v < sum(filtered_values) * 0.05 else 0 for v in filtered_values]  # Slight explode for small slices
                                        )
                                        
                                        # Improve text readability
                                        for autotext in autotexts:
                                            autotext.set_color('white')
                                            autotext.set_fontweight('bold')
                                            autotext.set_fontsize(9)
                                        
                                        # Adjust label positions to prevent overlap
                                        for text in texts:
                                            text.set_fontsize(10)
                                            text.set_fontweight('bold')
                                        
                                        ax.set_title('Sentiment Distribution (Pie Chart)', fontsize=13, fontweight='bold', pad=20)
                                        plt.tight_layout()
                                        st.pyplot(fig)
                                        plt.close()
                                    
                                    with col2:
                                        # Bar chart
                                        fig, ax = plt.subplots(figsize=(8, 6))
                                        bars = ax.bar(filtered_order, filtered_values, 
                                                     color=[color_map.get(cat, '#808080') for cat in filtered_order], 
                                                     alpha=0.8, edgecolor='black')
                                        ax.set_xlabel('Sentiment Category', fontsize=12, fontweight='bold')
                                        ax.set_ylabel('Number of Comments', fontsize=12, fontweight='bold')
                                        ax.set_title('Sentiment Category Distribution', fontsize=14, fontweight='bold')
                                        ax.tick_params(axis='x', rotation=15)
                                        ax.grid(axis='y', alpha=0.3)
                                        
                                        # Add percentage labels on bars
                                        for i, bar in enumerate(bars):
                                            height = bar.get_height()
                                            percentage = (filtered_values[i] / sum(filtered_values)) * 100
                                            ax.text(bar.get_x() + bar.get_width()/2., height,
                                                   f'{int(height)}\n({percentage:.1f}%)',
                                                   ha='center', va='bottom', fontsize=10, fontweight='bold')
                                        st.pyplot(fig)
                                        plt.close()
                            
                            # Top Comments Section
                            st.subheader("💬 Sample Comments")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Most Positive Comments:**")
                                top_positive = comments_df.nlargest(5, 'Polarity')
                                for idx, (_, row) in enumerate(top_positive.iterrows(), 1):
                                    st.markdown(f"""
                                    <div style="background-color: #e8f5e9; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #4caf50;">
                                        <strong>[{row['Polarity']:.3f}]</strong> {str(row['comment_text'])[:150]}
                                        {('...' if len(str(row['comment_text'])) > 150 else '')}
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            with col2:
                                st.write("**Most Negative Comments:**")
                                top_negative = comments_df.nsmallest(5, 'Polarity')
                                for idx, (_, row) in enumerate(top_negative.iterrows(), 1):
                                    st.markdown(f"""
                                    <div style="background-color: #ffebee; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #f44336;">
                                        <strong>[{row['Polarity']:.3f}]</strong> {str(row['comment_text'])[:150]}
                                        {('...' if len(str(row['comment_text'])) > 150 else '')}
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Statistics Summary
                            st.subheader("📋 Statistics Summary")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Positive Comments", f"{result.get('positive_count', 0):,}", 
                                         f"{result['positive_pct']:.1f}%")
                            with col2:
                                st.metric("Neutral Comments", f"{result.get('neutral_count', 0):,}", 
                                         f"{result.get('neutral_pct', 0):.1f}%")
                            with col3:
                                st.metric("Negative Comments", f"{result.get('negative_count', 0):,}", 
                                         f"{result['negative_pct']:.1f}%")
                            
                            # Download option
                            st.subheader("💾 Export Data")
                            csv = comments_df[['comment_text', 'Polarity', 'sentiment_category', 'author', 'like_count']].to_csv(index=False)
                            st.download_button(
                                label="📥 Download Comments CSV",
                                data=csv,
                                file_name=f"sentiment_analysis_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    else:
                        st.error(f"❌ {result.get('status', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error: {_redact_secrets(e)}")
                    import traceback
                    st.code(_redact_secrets(traceback.format_exc()))

if __name__ == "__main__":
    main()
