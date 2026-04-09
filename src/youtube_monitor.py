"""
Real-time YouTube Sentiment Monitoring Module
Monitors YouTube comments and tracks sentiment changes over time
"""
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import sqlite3
from typing import Optional, Dict, List
import warnings
warnings.filterwarnings('ignore')
import re
from collections import Counter
import math

def _redact_secrets(text: object) -> str:
    try:
        s = str(text)
    except Exception:
        return "<unprintable>"
    import re
    return re.sub(r"([?&]key=)[^&\s]+", r"\1<redacted>", s)

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("Warning: google-api-python-client not installed. Install with: pip install google-api-python-client")

from .sentiment_analyzer import analyze_sentiment_batch, add_sentiment_categories
from .config import OUTPUT_DIR, DATABASE_PATH, DEFAULT_YOUTUBE_API_KEY


class YouTubeSentimentMonitor:
    """
    Monitor YouTube video comments and track sentiment in real-time
    """
    
    def __init__(self, api_key: Optional[str] = None, video_ids: Optional[List[str]] = None):
        """
        Initialize the YouTube Sentiment Monitor
        
        Args:
            api_key: YouTube Data API v3 key (or set YOUTUBE_API_KEY env var)
            video_ids: List of video IDs to monitor
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY') or DEFAULT_YOUTUBE_API_KEY
        if not self.api_key:
            raise ValueError("YouTube API key required. Set YOUTUBE_API_KEY environment variable or pass api_key parameter")
        
        if not YOUTUBE_API_AVAILABLE:
            raise ImportError("google-api-python-client not installed. Install with: pip install google-api-python-client")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.video_ids = video_ids or []
        self.monitoring_db = OUTPUT_DIR / "monitoring.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize monitoring database"""
        conn = sqlite3.connect(self.monitoring_db)
        cursor = conn.cursor()
        
        # Create video info cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_info_cache (
                video_id TEXT PRIMARY KEY,
                title TEXT,
                channel_title TEXT,
                description TEXT,
                published_at TEXT,
                view_count INTEGER,
                like_count INTEGER,
                comment_count INTEGER,
                last_updated DATETIME
            )
        ''')
        
        # Create monitoring tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_sentiment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                avg_sentiment REAL,
                positive_count INTEGER,
                negative_count INTEGER,
                neutral_count INTEGER,
                total_comments INTEGER,
                UNIQUE(video_id, timestamp)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comment_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                comment_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                comment_text TEXT,
                sentiment REAL,
                author TEXT,
                like_count INTEGER,
                published_at TEXT,
                parent_id TEXT,
                language TEXT,
                UNIQUE(video_id, comment_id, timestamp)
            )
        ''')

        # Lightweight migration for existing DBs (add missing columns)
        cursor.execute("PRAGMA table_info(comment_snapshots)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        if "published_at" not in existing_cols:
            cursor.execute("ALTER TABLE comment_snapshots ADD COLUMN published_at TEXT")
        if "parent_id" not in existing_cols:
            cursor.execute("ALTER TABLE comment_snapshots ADD COLUMN parent_id TEXT")
        if "language" not in existing_cols:
            cursor.execute("ALTER TABLE comment_snapshots ADD COLUMN language TEXT")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                message TEXT,
                threshold REAL,
                current_value REAL,
                details TEXT
            )
        ''')

        # Lightweight migration for existing DBs (add missing column)
        cursor.execute("PRAGMA table_info(alerts)")
        existing_alert_cols = {row[1] for row in cursor.fetchall()}
        if "details" not in existing_alert_cols:
            cursor.execute("ALTER TABLE alerts ADD COLUMN details TEXT")
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_video_timestamp 
            ON video_sentiment_history(video_id, timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """
        Get video information (title, channel, etc.)
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Dictionary with video information or None
        """
        try:
            video_response = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()
            
            if video_response.get('items'):
                item = video_response['items'][0]
                snippet = item.get('snippet', {})
                stats = item.get('statistics', {})
                return {
                    'video_id': video_id,
                    'title': snippet.get('title', 'Unknown'),
                    'channel_title': snippet.get('channelTitle', 'Unknown'),
                    'description': snippet.get('description', '')[:200],
                    'published_at': snippet.get('publishedAt', ''),
                    'view_count': stats.get('viewCount', 0),
                    'like_count': stats.get('likeCount', 0),
                    'comment_count': stats.get('commentCount', 0)
                }
        except Exception as e:
            print(f"Error fetching video info for {video_id}: {_redact_secrets(e)}")
        return None
    
    def fetch_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict]:
        """
        Fetch comments for a specific video
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to fetch
        
        Returns:
            List of comment dictionaries
        """
        comments = []
        try:
            # Get video details first
            video_response = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()
            
            if not video_response.get('items'):
                print(f"Video {video_id} not found or not accessible")
                return comments
            
            # Fetch comments
            request = self.youtube.commentThreads().list(
                part='snippet,replies',
                videoId=video_id,
                maxResults=min(max_results, 100),  # API limit is 100 per request
                order='time',  # Get newest comments first
                textFormat='plainText'
            )
            
            while request and len(comments) < max_results:
                response = request.execute()
                
                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'comment_id': item['snippet']['topLevelComment']['id'],
                        'video_id': video_id,
                        'comment_text': comment.get('textDisplay', ''),
                        'author': comment.get('authorDisplayName', ''),
                        'like_count': comment.get('likeCount', 0),
                        'published_at': comment.get('publishedAt', ''),
                        'updated_at': comment.get('updatedAt', '')
                    })
                    
                    # Get replies if any
                    if 'replies' in item:
                        for reply in item['replies']['comments']:
                            reply_snippet = reply['snippet']
                            comments.append({
                                'comment_id': reply['id'],
                                'video_id': video_id,
                                'comment_text': reply_snippet.get('textDisplay', ''),
                                'author': reply_snippet.get('authorDisplayName', ''),
                                'like_count': reply_snippet.get('likeCount', 0),
                                'published_at': reply_snippet.get('publishedAt', ''),
                                'updated_at': reply_snippet.get('updatedAt', ''),
                                'parent_id': item['snippet']['topLevelComment']['id']
                            })
                
                # Check if there are more pages
                if 'nextPageToken' in response and len(comments) < max_results:
                    request = self.youtube.commentThreads().list(
                        part='snippet,replies',
                        videoId=video_id,
                        maxResults=min(max_results - len(comments), 100),
                        pageToken=response['nextPageToken'],
                        order='time',
                        textFormat='plainText'
                    )
                else:
                    break
            
            # Rate limiting - be respectful to API
            time.sleep(0.1)
            
        except HttpError as e:
            if e.resp.status == 403:
                print(f"API quota exceeded or access denied for video {video_id}")
            elif e.resp.status == 404:
                print(f"Video {video_id} not found")
            else:
                print(f"Error fetching comments for video {video_id}: {_redact_secrets(e)}")
        except Exception as e:
            print(f"Unexpected error fetching comments for video {video_id}: {_redact_secrets(e)}")
        
        return comments
    
    def analyze_comments_sentiment(self, comments: List[Dict]) -> pd.DataFrame:
        """
        Analyze sentiment of fetched comments
        
        Args:
            comments: List of comment dictionaries
        
        Returns:
            DataFrame with sentiment analysis
        """
        if not comments:
            return pd.DataFrame()
        
        df = pd.DataFrame(comments)
        df = analyze_sentiment_batch(df, show_progress=False)
        df = add_sentiment_categories(df)
        
        return df
    
    def save_snapshot(self, video_id: str, comments_df: pd.DataFrame):
        """
        Save comment snapshot to database
        
        Args:
            video_id: YouTube video ID
            comments_df: DataFrame with analyzed comments
        """
        if comments_df.empty:
            return
        
        conn = sqlite3.connect(self.monitoring_db)
        timestamp = datetime.now().isoformat()
        
        # Save individual comments
        for _, row in comments_df.iterrows():
            conn.execute('''
                INSERT OR IGNORE INTO comment_snapshots 
                (video_id, comment_id, timestamp, comment_text, sentiment, author, like_count, published_at, parent_id, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_id,
                row.get('comment_id', ''),
                timestamp,
                row.get('comment_text', ''),
                row.get('Polarity', 0.0),
                row.get('author', ''),
                int(row.get('like_count', 0) or 0),
                row.get('published_at', ''),
                row.get('parent_id', None),
                row.get('language', 'unknown')
            ))
        
        # Calculate and save aggregate sentiment
        avg_sentiment = float(comments_df['Polarity'].mean())
        # Cast to native Python ints to ensure SQLite stores INTEGER (not BLOB)
        positive_count = int((comments_df['Polarity'] > 0.1).sum())
        negative_count = int((comments_df['Polarity'] < -0.1).sum())
        neutral_count = int(len(comments_df) - positive_count - negative_count)
        total_comments = int(len(comments_df))
        
        conn.execute('''
            INSERT OR REPLACE INTO video_sentiment_history
            (video_id, timestamp, avg_sentiment, positive_count, negative_count, neutral_count, total_comments)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_id,
            timestamp,
            avg_sentiment,
            positive_count,
            negative_count,
            neutral_count,
            total_comments
        ))
        
        conn.commit()
        conn.close()
    
    def check_sentiment_alerts(self, video_id: str, current_sentiment: float, 
                              thresholds: Optional[Dict] = None):
        """
        Check if sentiment changes trigger alerts
        
        Args:
            video_id: YouTube video ID
            current_sentiment: Current average sentiment
            thresholds: Dictionary with alert thresholds
        """
        if thresholds is None:
            thresholds = {}

        # Legacy absolute thresholds (still supported, but optional)
        negative_threshold = float(thresholds.get("negative_threshold", -0.3))
        positive_threshold = float(thresholds.get("positive_threshold", 0.5))

        # Anomaly detection settings
        lookback_points = int(thresholds.get("lookback_points", 20))  # number of snapshots to learn baseline
        min_points = int(thresholds.get("min_points", 6))            # minimum baseline length
        zscore_threshold = float(thresholds.get("zscore_threshold", 2.5))
        ewma_alpha = float(thresholds.get("ewma_alpha", 0.3))
        ewma_sigma = float(thresholds.get("ewma_sigma", 2.5))

        # "Big move" dynamic threshold: k * rolling std
        change_sigma = float(thresholds.get("change_sigma", 2.5))
        min_std = float(thresholds.get("min_std", 1e-3))
        
        conn = sqlite3.connect(self.monitoring_db)
        timestamp = datetime.now().isoformat()
        
        # Helper: pull a couple example comments from latest snapshot
        def _get_example_comments(conn_: sqlite3.Connection, direction: str, n: int = 2) -> List[str]:
            try:
                cur_ = conn_.cursor()
                cur_.execute(
                    "SELECT MAX(timestamp) FROM comment_snapshots WHERE video_id = ?",
                    (video_id,),
                )
                ts_ = cur_.fetchone()[0]
                if not ts_:
                    return []
                if direction == "negative":
                    order = "sentiment ASC"
                else:
                    order = "sentiment DESC"
                rows_ = cur_.execute(
                    f"""
                    SELECT comment_text
                    FROM comment_snapshots
                    WHERE video_id = ? AND timestamp = ? AND comment_text IS NOT NULL
                    ORDER BY {order}
                    LIMIT ?
                    """,
                    (video_id, ts_, n),
                ).fetchall()
                out = []
                for (t,) in rows_:
                    s = str(t or "").strip().replace("\n", " ")
                    if s:
                        out.append(s[:200] + ("…" if len(s) > 200 else ""))
                return out
            except Exception:
                return []

        # Get previous sentiment (NOTE: snapshot was just saved, so latest row is "current")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT avg_sentiment, timestamp 
            FROM video_sentiment_history 
            WHERE video_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 2
        ''', (video_id,))
        
        rows = cursor.fetchall()
        previous_sentiment = rows[1][0] if len(rows) >= 2 else None
        
        alerts_triggered = []
        
        # Optional absolute thresholds
        if current_sentiment < negative_threshold:
            alerts_triggered.append({
                'type': 'negative_threshold',
                'message': f"⚠️ Avg sentiment below {negative_threshold:.2f}: {current_sentiment:.3f}",
                'threshold': negative_threshold,
                'value': current_sentiment,
                'details': json.dumps({
                    "reason": "absolute_threshold",
                    "examples": _get_example_comments(conn, "negative", 2),
                })
            })
        
        if current_sentiment > positive_threshold:
            alerts_triggered.append({
                'type': 'positive_threshold',
                'message': f"✅ Avg sentiment above {positive_threshold:.2f}: {current_sentiment:.3f}",
                'threshold': positive_threshold,
                'value': current_sentiment,
                'details': json.dumps({
                    "reason": "absolute_threshold",
                    "examples": _get_example_comments(conn, "positive", 2),
                })
            })

        # Pull recent history for anomaly baselines (include current point)
        hist = pd.read_sql_query(
            """
            SELECT timestamp, avg_sentiment
            FROM video_sentiment_history
            WHERE video_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            conn,
            params=(video_id, max(lookback_points + 1, min_points + 1)),
        )
        hist["avg_sentiment"] = pd.to_numeric(hist["avg_sentiment"], errors="coerce")
        hist = hist.dropna(subset=["avg_sentiment"])
        # reverse to chronological
        hist = hist.iloc[::-1].reset_index(drop=True)

        if len(hist) >= (min_points + 1):
            baseline = hist["avg_sentiment"].iloc[:-1]
            current = float(hist["avg_sentiment"].iloc[-1])
            mu = float(baseline.mean())
            sd = float(baseline.std(ddof=0))

            sd_eff = sd if sd and sd > min_std else min_std
            z = (current - mu) / sd_eff

            if abs(z) >= zscore_threshold:
                direction = "negative" if z < 0 else "positive"
                alerts_triggered.append({
                    "type": "sentiment_anomaly_zscore",
                    "message": f"🚨 Sentiment anomaly (z={z:.2f}) current={current:.3f} vs μ={mu:.3f}, σ={sd:.3f}",
                    "threshold": zscore_threshold,
                    "value": z,
                    "details": json.dumps({
                        "reason": "zscore",
                        "z": z,
                        "mean": mu,
                        "std": sd,
                        "examples": _get_example_comments(conn, direction, 2),
                    }),
                })

            # EWMA anomaly on baseline
            ewma_mean = float(baseline.ewm(alpha=ewma_alpha, adjust=False).mean().iloc[-1])
            # EWMA std approximation via residual std on baseline
            resid = baseline - baseline.ewm(alpha=ewma_alpha, adjust=False).mean()
            ewma_sd = float(resid.std(ddof=0))
            ewma_sd_eff = ewma_sd if ewma_sd and ewma_sd > min_std else min_std
            ewma_z = (current - ewma_mean) / ewma_sd_eff

            if abs(ewma_z) >= ewma_sigma:
                direction = "negative" if ewma_z < 0 else "positive"
                alerts_triggered.append({
                    "type": "sentiment_anomaly_ewma",
                    "message": f"🚨 Sentiment EWMA anomaly (z={ewma_z:.2f}) current={current:.3f} vs ewma={ewma_mean:.3f}",
                    "threshold": ewma_sigma,
                    "value": ewma_z,
                    "details": json.dumps({
                        "reason": "ewma",
                        "alpha": ewma_alpha,
                        "ewma_mean": ewma_mean,
                        "ewma_std": ewma_sd,
                        "examples": _get_example_comments(conn, direction, 2),
                    }),
                })

            # Dynamic "big move" based on rolling std
            if previous_sentiment is not None:
                prev = float(previous_sentiment)
                delta = current - prev
                # use baseline std as proxy
                if abs(delta) >= (change_sigma * sd_eff):
                    direction = "negative" if delta < 0 else "positive"
                    alerts_triggered.append({
                        "type": "sentiment_big_move",
                        "message": f"📈📉 Big move Δ={delta:.3f} (≥ {change_sigma:.1f}σ) from {prev:.3f} to {current:.3f}",
                        "threshold": change_sigma,
                        "value": delta,
                        "details": json.dumps({
                            "reason": "delta_vs_sigma",
                            "delta": delta,
                            "sigma": sd_eff,
                            "examples": _get_example_comments(conn, direction, 2),
                        }),
                    })
        
        # Save alerts
        for alert in alerts_triggered:
            conn.execute('''
                INSERT INTO alerts (video_id, alert_type, timestamp, message, threshold, current_value, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_id,
                alert['type'],
                timestamp,
                alert['message'],
                alert['threshold'],
                alert['value'],
                alert.get('details')
            ))
        
        conn.commit()
        conn.close()
        
        return alerts_triggered
    
    def monitor_video(self, video_id: str, max_comments: int = 100, 
                     check_alerts: bool = True) -> Dict:
        """
        Monitor a single video: fetch comments, analyze sentiment, save snapshot
        
        Args:
            video_id: YouTube video ID
            max_comments: Maximum comments to fetch
            check_alerts: Whether to check for alert conditions
        
        Returns:
            Dictionary with monitoring results
        """
        # Get video title for display
        video_title = self.get_video_title(video_id)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Monitoring: {video_title} ({video_id})")
        
        # Fetch comments
        comments = self.fetch_video_comments(video_id, max_comments)
        
        if not comments:
            return {
                'video_id': video_id,
                'status': 'no_comments',
                'timestamp': datetime.now().isoformat()
            }
        
        # Analyze sentiment
        comments_df = self.analyze_comments_sentiment(comments)
        
        if comments_df.empty:
            return {
                'video_id': video_id,
                'status': 'analysis_failed',
                'timestamp': datetime.now().isoformat()
            }
        
        # Save snapshot
        self.save_snapshot(video_id, comments_df)
        
        # Calculate metrics
        avg_sentiment = comments_df['Polarity'].mean()
        positive_pct = (comments_df['Polarity'] > 0.1).sum() / len(comments_df) * 100
        negative_pct = (comments_df['Polarity'] < -0.1).sum() / len(comments_df) * 100
        
        # Check alerts
        alerts = []
        if check_alerts:
            alerts = self.check_sentiment_alerts(video_id, avg_sentiment)
            if alerts:
                for alert in alerts:
                    print(f"  🚨 ALERT: {alert['message']}")
        
        result = {
            'video_id': video_id,
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'total_comments': len(comments_df),
            'avg_sentiment': avg_sentiment,
            'positive_pct': positive_pct,
            'negative_pct': negative_pct,
            'neutral_pct': 100 - positive_pct - negative_pct,
            'positive_count': (comments_df['Polarity'] > 0.1).sum(),
            'negative_count': (comments_df['Polarity'] < -0.1).sum(),
            'neutral_count': len(comments_df) - (comments_df['Polarity'] > 0.1).sum() - (comments_df['Polarity'] < -0.1).sum(),
            'alerts': len(alerts),
            'comments_df': comments_df  # Include full dataframe for visualization
        }
        
        print(f"  ✓ Analyzed {len(comments_df)} comments | Avg sentiment: {avg_sentiment:.3f}")
        
        return result
    
    def monitor_all_videos(self, max_comments: int = 100, check_alerts: bool = True) -> List[Dict]:
        """
        Monitor all videos in the monitoring list
        
        Args:
            max_comments: Maximum comments per video
            check_alerts: Whether to check for alert conditions
        
        Returns:
            List of monitoring results
        """
        if not self.video_ids:
            print("No videos to monitor. Add video IDs using add_video() method.")
            return []
        
        results = []
        for video_id in self.video_ids:
            try:
                result = self.monitor_video(video_id, max_comments, check_alerts)
                results.append(result)
            except Exception as e:
                print(f"Error monitoring video {video_id}: {e}")
                results.append({
                    'video_id': video_id,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    def cache_video_info(self, video_id: str):
        """Cache video information in database"""
        video_info = self.get_video_info(video_id)
        if video_info:
            conn = sqlite3.connect(self.monitoring_db)
            conn.execute('''
                INSERT OR REPLACE INTO video_info_cache
                (video_id, title, channel_title, description, published_at,
                 view_count, like_count, comment_count, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_info['video_id'],
                video_info['title'],
                video_info['channel_title'],
                video_info['description'],
                video_info['published_at'],
                video_info['view_count'],
                video_info['like_count'],
                video_info['comment_count'],
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
            return video_info
        return None
    
    def get_cached_video_info(self, video_id: str) -> Optional[Dict]:
        """Get cached video information"""
        conn = sqlite3.connect(self.monitoring_db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM video_info_cache WHERE video_id = ?', (video_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'video_id': row[0],
                'title': row[1],
                'channel_title': row[2],
                'description': row[3],
                'published_at': row[4],
                'view_count': row[5],
                'like_count': row[6],
                'comment_count': row[7],
                'last_updated': row[8]
            }
        return None
    
    def get_video_title(self, video_id: str) -> str:
        """Get video title (from cache or API)"""
        cached = self.get_cached_video_info(video_id)
        if cached:
            return cached['title']
        
        # Try to fetch and cache
        video_info = self.cache_video_info(video_id)
        if video_info:
            return video_info['title']
        
        return video_id  # Fallback to ID if can't fetch
    
    def add_video(self, video_id: str):
        """Add a video to the monitoring list"""
        if video_id not in self.video_ids:
            self.video_ids.append(video_id)
            # Cache video info when adding
            video_info = self.cache_video_info(video_id)
            if video_info:
                print(f"Added video: {video_info['title']} ({video_id})")
            else:
                print(f"Added video {video_id} to monitoring list")
    
    def remove_video(self, video_id: str):
        """Remove a video from the monitoring list"""
        if video_id in self.video_ids:
            self.video_ids.remove(video_id)
            print(f"Removed video {video_id} from monitoring list")
    
    def get_sentiment_history(self, video_id: str, hours: int = 24) -> pd.DataFrame:
        """
        Get sentiment history for a video
        
        Args:
            video_id: YouTube video ID
            hours: Number of hours of history to retrieve
        
        Returns:
            DataFrame with sentiment history
        """
        conn = sqlite3.connect(self.monitoring_db)
        
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        df = pd.read_sql_query('''
            SELECT * FROM video_sentiment_history
            WHERE video_id = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        ''', conn, params=(video_id, cutoff_time))
        
        conn.close()
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Ensure numeric types for all numeric columns
            numeric_columns = ['avg_sentiment', 'total_comments', 'positive_count', 
                             'negative_count', 'neutral_count']
            for col in numeric_columns:
                if col in df.columns:
                    # sqlite can store numpy scalars as BLOB; convert 8-byte little-endian ints
                    def _coerce_sqlite_num(v):
                        if isinstance(v, (bytes, bytearray)):
                            try:
                                return int.from_bytes(v, byteorder='little', signed=True)
                            except Exception:
                                return None
                        return v
                    df[col] = df[col].map(_coerce_sqlite_num)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def get_recent_alerts(self, hours: int = 24) -> pd.DataFrame:
        """
        Get recent alerts
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            DataFrame with alerts
        """
        conn = sqlite3.connect(self.monitoring_db)
        
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        df = pd.read_sql_query('''
            SELECT * FROM alerts
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        ''', conn, params=(cutoff_time,))
        
        conn.close()
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df

    def get_latest_comments_snapshot(
        self,
        video_id: str,
        limit: int = 50,
        order_by: str = "most_liked",
        sentiment_filter: str = "all",
        keyword: str = "",
        min_likes: int = 0,
    ) -> pd.DataFrame:
        """
        Fetch comments from the most recent snapshot for a video (from SQLite).

        Args:
            video_id: YouTube video ID
            limit: Max rows returned
            order_by: "most_liked" or "newest"
            sentiment_filter: "all" | "positive" | "neutral" | "negative"
            keyword: substring match on comment_text (case-insensitive)
            min_likes: minimum like_count

        Returns:
            DataFrame with snapshot comments (may be empty)
        """
        conn = sqlite3.connect(self.monitoring_db)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT MAX(timestamp) FROM comment_snapshots WHERE video_id = ?",
                (video_id,),
            )
            latest_ts = cursor.fetchone()[0]
            if not latest_ts:
                return pd.DataFrame()

            df = pd.read_sql_query(
                """
                SELECT
                    video_id,
                    comment_id,
                    timestamp,
                    published_at,
                    parent_id,
                    author,
                    like_count,
                    language,
                    comment_text,
                    sentiment
                FROM comment_snapshots
                WHERE video_id = ? AND timestamp = ?
                """,
                conn,
                params=(video_id, latest_ts),
            )

            if df.empty:
                return df

            # Coerce numeric types
            df["like_count"] = pd.to_numeric(df.get("like_count"), errors="coerce").fillna(0).astype(int)
            df["sentiment"] = pd.to_numeric(df.get("sentiment"), errors="coerce")

            # Sentiment bucket (align with rest of monitor)
            pos_thr = 0.1
            neg_thr = -0.1
            df["sentiment_bucket"] = np.where(
                df["sentiment"] > pos_thr,
                "positive",
                np.where(df["sentiment"] < neg_thr, "negative", "neutral"),
            )

            if min_likes and min_likes > 0:
                df = df[df["like_count"] >= int(min_likes)]

            if sentiment_filter and sentiment_filter != "all":
                df = df[df["sentiment_bucket"] == sentiment_filter]

            if keyword:
                k = str(keyword).strip().lower()
                if k:
                    df = df[df["comment_text"].astype(str).str.lower().str.contains(k, na=False)]

            if order_by == "newest":
                # Prefer published_at if present; otherwise fall back to comment_id/like_count ordering
                if "published_at" in df.columns:
                    df["_published_at_dt"] = pd.to_datetime(df["published_at"], errors="coerce")
                    df = df.sort_values(["_published_at_dt", "like_count"], ascending=[False, False]).drop(columns=["_published_at_dt"])
                else:
                    df = df.sort_values(["like_count"], ascending=[False])
            else:
                df = df.sort_values(["like_count", "sentiment"], ascending=[False, False])

            return df.head(int(limit)).reset_index(drop=True)
        finally:
            conn.close()

    def get_keyword_trends(
        self,
        video_id: str,
        hours: int = 24,
        top_n: int = 10,
        ngram: int = 1,
        include_hashtags: bool = True,
        bucket_minutes: int = 60,
        min_term_count: int = 2,
        time_basis: str = "snapshot",
    ) -> Dict[str, pd.DataFrame]:
        """
        Compute keyword/hashtag trends over time from saved snapshots.

        Time-bucketing can be based on:
        - `time_basis="snapshot"`: `comment_snapshots.timestamp` (when snapshot was taken)
        - `time_basis="published"`: `comment_snapshots.published_at` (when comment was published),
           falling back to snapshot timestamp if `published_at` is missing/invalid.

        Returns:
            {
              "top_terms": DataFrame(term, total_count),
              "timeseries": DataFrame(timestamp, term, count)
            }
        """
        hours = int(hours)
        top_n = int(top_n)
        ngram = int(ngram)
        bucket_minutes = int(bucket_minutes)
        min_term_count = int(min_term_count)

        if hours <= 0 or top_n <= 0 or ngram <= 0 or bucket_minutes <= 0:
            return {"top_terms": pd.DataFrame(), "timeseries": pd.DataFrame()}

        # Very small stopword list (kept local to avoid extra deps)
        stopwords = {
            "a","an","and","are","as","at","be","but","by","for","from","has","have","he","her","his","i","if","in",
            "is","it","its","me","my","not","of","on","or","our","she","so","that","the","their","them","they","this",
            "to","was","we","were","what","when","who","why","will","with","you","your","im","ive","dont","cant","wont",
        }

        def tokenize(text: str) -> List[str]:
            t = (text or "").lower()
            # keep hashtags as tokens (without '#') so they can be mixed with keywords
            tags = re.findall(r"#([a-z0-9_]{2,})", t)
            # remove URLs
            t = re.sub(r"https?://\\S+|www\\.\\S+", " ", t)
            # keep words
            words = re.findall(r"[a-z0-9']{2,}", t)
            words = [w.strip("'") for w in words if w and w not in stopwords]
            if include_hashtags:
                # prefix to distinguish hashtags in UI
                tags = [f"#{x}" for x in tags]
                return tags + words
            return words

        def make_ngrams(tokens: List[str], n: int) -> List[str]:
            if n <= 1:
                return tokens
            out: List[str] = []
            for i in range(0, max(0, len(tokens) - n + 1)):
                gram = " ".join(tokens[i : i + n])
                # avoid grams that are entirely hashtags (often redundant)
                if gram:
                    out.append(gram)
            return out

        conn = sqlite3.connect(self.monitoring_db)
        try:
            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            df = pd.read_sql_query(
                """
                SELECT timestamp, published_at, comment_text
                FROM comment_snapshots
                WHERE video_id = ? AND timestamp >= ?
                """,
                conn,
                params=(video_id, cutoff),
            )
        finally:
            conn.close()

        if df.empty:
            return {"top_terms": pd.DataFrame(), "timeseries": pd.DataFrame()}

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["published_at"] = pd.to_datetime(df.get("published_at"), errors="coerce")

        if time_basis == "published":
            # Use published_at if available, else fallback to snapshot timestamp
            df["basis_ts"] = df["published_at"].where(df["published_at"].notna(), df["timestamp"])
        else:
            df["basis_ts"] = df["timestamp"]

        df = df.dropna(subset=["basis_ts"])
        if df.empty:
            return {"top_terms": pd.DataFrame(), "timeseries": pd.DataFrame()}

        # Bucket timestamps
        bucket_rule = f"{bucket_minutes}min"
        df["bucket_ts"] = df["basis_ts"].dt.floor(bucket_rule)

        # Count terms per bucket
        bucket_counts: Dict[pd.Timestamp, Counter] = {}
        overall = Counter()

        for bucket_ts, group in df.groupby("bucket_ts"):
            c = Counter()
            for text in group["comment_text"].astype(str).tolist():
                toks = tokenize(text)
                terms = make_ngrams(toks, ngram)
                c.update(terms)
            # Filter trivial terms early
            c = Counter({k: v for k, v in c.items() if v >= 1 and len(k) >= 2})
            bucket_counts[bucket_ts] = c
            overall.update(c)

        # Drop low-frequency terms overall
        overall = Counter({k: v for k, v in overall.items() if v >= min_term_count})
        if not overall:
            return {"top_terms": pd.DataFrame(), "timeseries": pd.DataFrame()}

        top_terms = [t for t, _ in overall.most_common(top_n)]
        top_df = pd.DataFrame(
            [{"term": t, "total_count": int(overall[t])} for t in top_terms]
        ).sort_values("total_count", ascending=False, ignore_index=True)

        rows = []
        for ts in sorted(bucket_counts.keys()):
            c = bucket_counts[ts]
            for term in top_terms:
                rows.append({"timestamp": ts, "term": term, "count": int(c.get(term, 0))})
        ts_df = pd.DataFrame(rows)
        return {"top_terms": top_df, "timeseries": ts_df}
    
    def fetch_channel_videos(self, channel_id: str = None, channel_username: str = None, 
                            channel_url: str = None, max_results: int = 50, order: str = 'date') -> List[Dict]:
        """
        Fetch videos from a YouTube channel
        
        Args:
            channel_id: YouTube channel ID (e.g., 'UCuAXFkgsw1L7xaCfnd5JJOw')
            channel_username: YouTube channel username (e.g., 'rickastley' or '@rickastley')
            channel_url: Full YouTube channel URL (e.g., 'https://www.youtube.com/@rickastley')
            max_results: Maximum number of videos to fetch
            order: Order of results ('date', 'rating', 'relevance', 'title', 'videoCount', 'viewCount')
        
        Returns:
            List of video dictionaries with id, title, channel, etc.
        """
        videos = []
        
        try:
            # Extract channel ID from URL if provided
            if channel_url:
                if '/channel/' in channel_url:
                    channel_id = channel_url.split('/channel/')[-1].split('/')[0].split('?')[0]
                elif '/@' in channel_url:
                    channel_username = channel_url.split('/@')[-1].split('/')[0].split('?')[0]
                elif '/c/' in channel_url or '/user/' in channel_url:
                    username = channel_url.split('/')[-1].split('?')[0]
                    channel_username = username
            
            # Clean username (remove @ if present)
            if channel_username:
                channel_username = channel_username.lstrip('@')
            
            # If username provided, get channel ID first
            if channel_username and not channel_id:
                try:
                    # Try forUsername first (legacy)
                    channels_response = self.youtube.channels().list(
                        part='id',
                        forUsername=channel_username
                    ).execute()
                    
                    if channels_response.get('items'):
                        channel_id = channels_response['items'][0]['id']
                    else:
                        # Try with @ handle format using search
                        channels_response = self.youtube.search().list(
                            part='snippet',
                            q=channel_username,
                            type='channel',
                            maxResults=1
                        ).execute()
                        
                        if channels_response.get('items'):
                            channel_id = channels_response['items'][0]['snippet']['channelId']
                        else:
                            print(f"Channel username '{channel_username}' not found")
                            return videos
                except Exception as e:
                    print(f"Error looking up channel username: {_redact_secrets(e)}")
                    return videos
            
            if not channel_id:
                print("Either channel_id, channel_username, or channel_url must be provided")
                return videos
            
            # Fetch videos from channel
            request = self.youtube.search().list(
                part='snippet',
                channelId=channel_id,
                type='video',
                maxResults=min(max_results, 50),  # API limit is 50 per request
                order=order
            )
            
            while request and len(videos) < max_results:
                response = request.execute()
                
                for item in response.get('items', []):
                    snippet = item.get('snippet', {})
                    videos.append({
                        'video_id': item['id']['videoId'],
                        'title': snippet.get('title', 'Unknown'),
                        'channel_title': snippet.get('channelTitle', 'Unknown'),
                        'channel_id': snippet.get('channelId', ''),
                        'description': snippet.get('description', '')[:200],
                        'published_at': snippet.get('publishedAt', ''),
                        'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url', '')
                    })
                
                # Check if there are more pages
                if 'nextPageToken' in response and len(videos) < max_results:
                    request = self.youtube.search().list(
                        part='snippet',
                        channelId=channel_id,
                        type='video',
                        maxResults=min(max_results - len(videos), 50),
                        pageToken=response['nextPageToken'],
                        order=order
                    )
                else:
                    break
            
            # Rate limiting
            time.sleep(0.1)
            
        except HttpError as e:
            if e.resp.status == 403:
                print("API quota exceeded or access denied")
            else:
                print(f"Error fetching channel videos: {_redact_secrets(e)}")
        except Exception as e:
            print(f"Unexpected error fetching channel videos: {_redact_secrets(e)}")
        
        return videos
    
    def fetch_my_videos(self, max_results: int = 50) -> List[Dict]:
        """
        Fetch videos from the authenticated user's channel
        Note: Requires OAuth authentication, falls back to channel search
        
        Args:
            max_results: Maximum number of videos to fetch
        
        Returns:
            List of video dictionaries
        """
        # For now, this requires the user to provide their channel ID
        # In the future, could use OAuth to get user's channel automatically
        print("Note: To fetch your own videos, provide your channel ID or username")
        print("You can find your channel ID in your YouTube channel settings")
        return []
    
    def analyze_video_comments(self, video_id: str, max_comments: int = 100) -> Dict:
        """
        Quick analysis of a single video's comments
        
        Args:
            video_id: YouTube video ID
            max_comments: Maximum comments to analyze
        
        Returns:
            Dictionary with analysis results
        """
        # Fetch comments
        comments = self.fetch_video_comments(video_id, max_comments)
        
        if not comments:
            return {
                'video_id': video_id,
                'status': 'no_comments',
                'message': 'No comments found or video not accessible'
            }
        
        # Analyze sentiment
        comments_df = self.analyze_comments_sentiment(comments)
        
        if comments_df.empty:
            return {
                'video_id': video_id,
                'status': 'analysis_failed',
                'message': 'Failed to analyze comments'
            }
        
        # Get video info
        video_info = self.get_video_info(video_id)
        video_title = video_info['title'] if video_info else video_id
        
        # Calculate statistics
        avg_sentiment = comments_df['Polarity'].mean()
        positive_count = (comments_df['Polarity'] > 0.1).sum()
        negative_count = (comments_df['Polarity'] < -0.1).sum()
        neutral_count = len(comments_df) - positive_count - negative_count
        
        return {
            'video_id': video_id,
            'video_title': video_title,
            'status': 'success',
            'total_comments': len(comments_df),
            'avg_sentiment': avg_sentiment,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_pct': positive_count / len(comments_df) * 100,
            'negative_pct': negative_count / len(comments_df) * 100,
            'neutral_pct': neutral_count / len(comments_df) * 100,
            'comments_df': comments_df  # Include full dataframe for further analysis
        }
