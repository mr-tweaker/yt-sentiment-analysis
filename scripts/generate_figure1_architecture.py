#!/usr/bin/env python3
"""
Generate Figure 1: System Architecture Diagram for YouTube Sentiment Analysis.
Saves to screenshots/Figure1_System_Architecture.png
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

# Output path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'screenshots')
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Figure1_System_Architecture.png')

# Figure setup
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 14)
ax.set_aspect('equal')
ax.axis('off')

# Colors (professional palette)
bg_light = '#f8f9fa'
layer_colors = {
    'presentation': '#4a90d9',   # blue
    'application':  '#50c878',   # green
    'data':         '#e8a838',   # amber
    'infrastructure': '#6c5ce7', # purple
}
text_dark = '#2d3436'
arrow_color = '#636e72'

def draw_rounded_box(ax, x, y, w, h, color, label, items, fontsize_title=11, fontsize_items=8):
    """Draw a rounded rectangle with title and bullet items."""
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                         facecolor=color, edgecolor='white', linewidth=2, alpha=0.85)
    ax.add_patch(box)
    ax.text(x + w/2, y + h - 0.35, label, ha='center', va='top', fontsize=fontsize_title,
            fontweight='bold', color='white')
    for i, item in enumerate(items):
        ax.text(x + 0.15, y + h - 0.7 - i * 0.32, f'• {item}', ha='left', va='top',
                fontsize=fontsize_items, color=text_dark)

def draw_arrow(ax, x1, y1, x2, y2, style='->'):
    """Draw arrow between two points."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=arrow_color, lw=2))

# Layer definitions (x, y, width, height, color, title, items)
layers = [
    (0.5, 10.5, 9, 2.2, layer_colors['presentation'], 'Presentation Layer',
     ['Streamlit web app • Video Browser, Live Monitoring, History, Alerts, Manual Check',
      'Responsive design • Session state management • Real-time updates']),
    (0.5, 7.5, 9, 2.5, layer_colors['application'], 'Application Layer',
     ['data_loader.py • sentiment_analyzer.py • features/ (basic, medium, advanced)',
      'visualizations.py • youtube_monitor.py • Modular Python pipeline']),
    (0.5, 4.2, 9, 2.8, layer_colors['data'], 'Data Layer',
     ['SQLite: video_sentiment_history, comment_snapshots, alerts, video_info_cache',
      'YouTube Data API v3 • CSV batch support • Caching & backup']),
    (0.5, 1.2, 9, 2.5, layer_colors['infrastructure'], 'Infrastructure Layer',
     ['Docker (python:3.11-slim) • Docker Compose • Environment variables',
      'Health checks • Port 8501 • Volume mounts for output']),
]

for x, y, w, h, color, title, items in layers:
    draw_rounded_box(ax, x, y, w, h, color, title, items)

# Vertical flow arrows (between layers)
arrow_x = 9.6
arrow_coords = [(arrow_x, 10.4), (arrow_x, 9.0), (arrow_x, 7.2), (arrow_x, 5.6), (arrow_x, 3.7), (arrow_x, 2.5)]
for i in range(len(arrow_coords) - 1):
    draw_arrow(ax, arrow_x, arrow_coords[i][1], arrow_x, arrow_coords[i+1][1])
ax.text(9.85, 6.5, 'Data\nFlow', fontsize=9, ha='left', va='center', color=arrow_color, style='italic')

# External input: YouTube API
ax.annotate('', xy=(1.8, 5.0), xytext=(0.2, 6.5),
            arrowprops=dict(arrowstyle='->', color='#d63031', lw=1.5, linestyle='--'))
ax.text(0.1, 6.9, 'YouTube\nAPI v3', fontsize=8, ha='center', va='bottom', color='#d63031')

# User
ax.text(5, 13.2, 'User (Browser)', fontsize=10, ha='center', va='center', color=text_dark, fontweight='bold')
draw_arrow(ax, 5, 12.8, 5, 12.3)

# Title
ax.text(5, 13.75, 'YouTube Sentiment Analysis — System Architecture', fontsize=14, ha='center', va='center',
       fontweight='bold', color=text_dark)

plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f'Figure 1 saved to: {OUTPUT_FILE}')
