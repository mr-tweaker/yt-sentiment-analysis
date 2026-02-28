#!/usr/bin/env python3
"""
Real-time YouTube Sentiment Monitoring Service
Runs continuously to monitor YouTube videos and track sentiment changes
"""
import os
import sys
import time
import signal
from datetime import datetime
from pathlib import Path
import argparse
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.youtube_monitor import YouTubeSentimentMonitor
from src.config import DEFAULT_YOUTUBE_API_KEY


class MonitoringService:
    """Service that runs continuous monitoring"""
    
    def __init__(self, config_file: str = "monitoring_config.json"):
        """
        Initialize monitoring service
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = Path(config_file)
        self.running = True
        self.monitor = None
        self.load_config()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.api_key = config.get('api_key') or os.getenv('YOUTUBE_API_KEY')
                self.video_ids = config.get('video_ids', [])
                self.interval = config.get('interval_minutes', 30)
                self.max_comments = config.get('max_comments_per_video', 100)
                self.check_alerts = config.get('check_alerts', True)
        else:
            # Create default config with preloaded API key
            self.api_key = os.getenv('YOUTUBE_API_KEY') or DEFAULT_YOUTUBE_API_KEY
            self.video_ids = []
            self.interval = 30  # minutes
            self.max_comments = 100
            self.check_alerts = True
            self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        config = {
            'api_key': self.api_key,
            'video_ids': self.video_ids,
            'interval_minutes': self.interval,
            'max_comments_per_video': self.max_comments,
            'check_alerts': self.check_alerts
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {self.config_file}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down monitoring service...")
        self.running = False
    
    def start(self):
        """Start the monitoring service"""
        # Use default API key if not set
        if not self.api_key:
            self.api_key = DEFAULT_YOUTUBE_API_KEY
        
        if not self.api_key:
            print("❌ Error: YouTube API key not found!")
            print("   Set YOUTUBE_API_KEY environment variable or add to config file")
            return
        
        print(f"✅ Using API key: {self.api_key[:10]}...{self.api_key[-4:]}")
        
        if not self.video_ids:
            print("⚠️  Warning: No videos to monitor!")
            print(f"   Add video IDs to {self.config_file}")
            print("   Example: {\"video_ids\": [\"dQw4w9WgXcQ\", \"jNQXAC9IVRw\"]}")
            return
        
        try:
            self.monitor = YouTubeSentimentMonitor(
                api_key=self.api_key,
                video_ids=self.video_ids
            )
        except Exception as e:
            print(f"❌ Error initializing monitor: {e}")
            return
        
        print("=" * 80)
        print("🚀 YouTube Sentiment Monitoring Service Started")
        print("=" * 80)
        print(f"Monitoring {len(self.video_ids)} video(s)")
        print(f"Update interval: {self.interval} minutes")
        print(f"Max comments per video: {self.max_comments}")
        print(f"Press Ctrl+C to stop")
        print("=" * 80)
        
        iteration = 0
        while self.running:
            iteration += 1
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iteration #{iteration}")
            print("-" * 80)
            
                try:
                    results = self.monitor.monitor_all_videos(
                        max_comments=self.max_comments,
                        check_alerts=self.check_alerts
                    )
                    
                    # Summary with video titles
                    successful = sum(1 for r in results if r.get('status') == 'success')
                    print(f"\n✓ Completed: {successful}/{len(results)} videos monitored successfully")
                    
                    # Show video titles in summary
                    print("\n📊 Monitoring Summary:")
                    for result in results:
                        if result.get('status') == 'success':
                            video_title = self.monitor.get_video_title(result['video_id'])
                            print(f"   • {video_title}")
                            print(f"     Sentiment: {result['avg_sentiment']:.3f} | Comments: {result['total_comments']}")
                        elif result.get('status') == 'error':
                            video_title = self.monitor.get_video_title(result['video_id'])
                            print(f"   ✗ {video_title}: {result.get('error', 'Unknown error')}")
                
                # Show alerts if any
                alerts_df = self.monitor.get_recent_alerts(hours=1)
                if len(alerts_df) > 0:
                    print(f"\n🚨 {len(alerts_df)} alert(s) in the last hour:")
                    for _, alert in alerts_df.head(5).iterrows():
                        print(f"   - {alert['message']}")
                
            except Exception as e:
                print(f"❌ Error during monitoring: {e}")
                import traceback
                traceback.print_exc()
            
            if self.running:
                wait_seconds = self.interval * 60
                print(f"\n⏳ Next update in {self.interval} minutes...")
                print("   (Press Ctrl+C to stop)")
                
                # Wait with periodic checks for shutdown signal
                for _ in range(wait_seconds):
                    if not self.running:
                        break
                    time.sleep(1)
        
        print("\n✅ Monitoring service stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='YouTube Sentiment Monitoring Service')
    parser.add_argument('--config', '-c', type=str, default='monitoring_config.json',
                       help='Path to configuration file')
    parser.add_argument('--interval', '-i', type=int, default=None,
                       help='Update interval in minutes (overrides config)')
    parser.add_argument('--videos', '-v', type=str, nargs='+',
                       help='Video IDs to monitor (overrides config)')
    parser.add_argument('--api-key', '-k', type=str, default=None,
                       help='YouTube API key (overrides config and env var)')
    
    args = parser.parse_args()
    
    service = MonitoringService(config_file=args.config)
    
    # Override config with command line arguments
    if args.api_key:
        service.api_key = args.api_key
    if args.interval:
        service.interval = args.interval
    if args.videos:
        service.video_ids = args.videos
    
    service.start()


if __name__ == "__main__":
    main()
