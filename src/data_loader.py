"""
Data loading and preprocessing module
"""
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from .config import COMMENTS_CSV, VIDEOS_CSV, ADDITIONAL_DATA_DIR, SAMPLE_SIZE


def load_comments(file_path=None, sample_size=None):
    """
    Load comments from CSV file
    
    Args:
        file_path: Path to comments CSV file. If None, uses config path.
        sample_size: Number of comments to sample. If None, uses all.
    
    Returns:
        DataFrame with comments
    
    Raises:
        FileNotFoundError: If the file doesn't exist with helpful message
    """
    if file_path is None:
        file_path = COMMENTS_CSV
    
    if not Path(file_path).exists():
        error_msg = f"""
Comments file not found: {file_path}

Please do one of the following:
1. Place your CSV file at: {file_path}
2. Or update the path in src/config.py
3. Or pass the file_path argument: load_comments(file_path='path/to/your/file.csv')
4. Or set environment variable: export COMMENTS_CSV='path/to/your/file.csv'

Expected CSV columns: video_id, comment_text, likes, replies
"""
        raise FileNotFoundError(error_msg)
    
    print(f"Loading comments from {file_path}...")
    
    # Try different encodings to handle special characters
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    comments = None
    
    for encoding in encodings:
        try:
            # Load with error handling for bad lines
            try:
                comments = pd.read_csv(file_path, encoding=encoding, on_bad_lines='skip', low_memory=False)
            except TypeError:
                # Fallback for older pandas versions
                comments = pd.read_csv(file_path, encoding=encoding, error_bad_lines=False, low_memory=False)
            print(f"  Successfully loaded with {encoding} encoding")
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if comments is None:
        raise ValueError(f"Could not read file with any of the tried encodings: {encodings}")
    
    print(f"Loaded {len(comments)} comments")
    
    # Drop missing values
    initial_count = len(comments)
    comments = comments.dropna(subset=['comment_text'])
    dropped = initial_count - len(comments)
    if dropped > 0:
        print(f"Dropped {dropped} comments with missing text")
    
    # Sample if specified
    if sample_size is None:
        sample_size = SAMPLE_SIZE
    
    if sample_size and len(comments) > sample_size:
        comments = comments.head(sample_size).copy()
        print(f"Sampled {sample_size} comments for analysis")
    
    return comments


def load_video_metadata(file_path=None, additional_data_dir=None):
    """
    Load video metadata from CSV files
    
    Args:
        file_path: Path to main videos CSV file
        additional_data_dir: Directory with additional CSV files
    
    Returns:
        DataFrame with video metadata
    """
    full_df = pd.DataFrame()
    
    # Load main video file if provided
    if file_path and Path(file_path).exists():
        print(f"Loading video metadata from {file_path}...")
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        for encoding in encodings:
            try:
                try:
                    full_df = pd.read_csv(file_path, encoding=encoding, on_bad_lines='skip', low_memory=False)
                except TypeError:
                    full_df = pd.read_csv(file_path, encoding=encoding, error_bad_lines=False, low_memory=False)
                print(f"  Loaded {len(full_df)} videos from main file (encoding: {encoding})")
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
    
    # Load additional data files
    if additional_data_dir is None:
        additional_data_dir = ADDITIONAL_DATA_DIR
    
    if Path(additional_data_dir).exists():
        print(f"Loading additional data from {additional_data_dir}...")
        csv_files = list(Path(additional_data_dir).glob("*.csv"))
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='iso-8859-1', 
                               on_bad_lines='skip', low_memory=False)
                full_df = pd.concat([full_df, df], ignore_index=True)
                print(f"  Loaded {len(df)} records from {csv_file.name}")
            except Exception as e:
                print(f"  Error loading {csv_file.name}: {e}")
    
    if len(full_df) > 0:
        # Remove duplicates
        initial_count = len(full_df)
        full_df = full_df.drop_duplicates()
        print(f"Removed {initial_count - len(full_df)} duplicate records")
        
        # Load category mapping if available
        json_file = Path(additional_data_dir) / "US_category_id.json"
        if json_file.exists():
            import json
            with open(json_file, 'r') as f:
                json_data = json.load(f)
            
            cat_dict = {}
            for item in json_data.get('items', []):
                cat_dict[int(item['id'])] = item['snippet']['title']
            
            if 'category_id' in full_df.columns:
                full_df['category_name'] = full_df['category_id'].map(cat_dict)
                print(f"Mapped {len(cat_dict)} categories")
    
    return full_df


def prepare_data(comments_df, video_df=None):
    """
    Prepare and merge comment and video data
    
    Args:
        comments_df: DataFrame with comments
        video_df: DataFrame with video metadata (optional)
    
    Returns:
        Prepared DataFrame
    """
    df = comments_df.copy()
    
    # Merge with video metadata if available
    if video_df is not None and 'video_id' in df.columns and 'video_id' in video_df.columns:
        print("Merging comments with video metadata...")
        df = df.merge(
            video_df[['video_id', 'category_name', 'channel_title']].drop_duplicates(),
            on='video_id',
            how='left'
        )
        print(f"Merged data: {len(df)} comments")
    
    return df
