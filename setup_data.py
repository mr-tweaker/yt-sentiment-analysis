#!/usr/bin/env python3
"""
Helper script to set up data directory and provide instructions
"""
import os
from pathlib import Path

def setup_data_directory():
    """Create data directory and provide setup instructions"""
    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    
    print("=" * 80)
    print("YouTube Sentiment Analysis - Data Setup")
    print("=" * 80)
    
    # Create data directory
    data_dir.mkdir(exist_ok=True)
    print(f"✓ Created data directory: {data_dir}")
    
    # Check if files exist
    comments_file = data_dir / "UScomments.csv"
    videos_file = data_dir / "USvideos.csv"
    
    print("\n📁 Data Directory Status:")
    print(f"   Location: {data_dir}")
    
    if comments_file.exists():
        size = comments_file.stat().st_size / (1024 * 1024)  # MB
        print(f"   ✓ Comments file found: {comments_file.name} ({size:.2f} MB)")
    else:
        print(f"   ✗ Comments file missing: {comments_file.name}")
        print(f"     Expected location: {comments_file}")
    
    if videos_file.exists():
        size = videos_file.stat().st_size / (1024 * 1024)  # MB
        print(f"   ✓ Videos file found: {videos_file.name} ({size:.2f} MB)")
    else:
        print(f"   - Videos file (optional): {videos_file.name}")
    
    print("\n📋 Next Steps:")
    if not comments_file.exists():
        print("   1. Place your comments CSV file in the data directory:")
        print(f"      cp /path/to/your/comments.csv {comments_file}")
        print("\n   2. Or update the path in src/config.py")
        print("\n   3. Or use command line argument:")
        print("      python main.py --comments /path/to/your/comments.csv")
    else:
        print("   ✓ Data files are ready!")
        print("   Run the analysis with: python main.py")
    
    print("\n📝 Expected CSV Format:")
    print("   Comments CSV should have columns: video_id, comment_text, likes, replies")
    print("   Videos CSV (optional) should have: video_id, category_id, channel_title, etc.")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    setup_data_directory()
