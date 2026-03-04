import streamlit as st
import pandas as pd
import yt_dlp
import os
import time
import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(text)
    if score['compound'] >= 0.05: return "Positive"
    if score['compound'] <= -0.05: return "Negative"
    return "Neutral"

def get_tiktok_comments(url, debug=False):
    cookie_file = "tiktok_cookies.txt"
    
    # Advanced 2026 Options for TikTok
    ydl_opts = {
        'getcomments': True, 
        'skip_download': True, 
        'quiet': not debug,
        'extract_flat': False,
        'no_warnings': False,
        'impersonate': 'chrome', # Crucial: Mimics a real browser TLS/Fingerprint
        'extractor_args': {
            'tiktok': {
                'api_hostname': 'api22-normal-c-useast2a.tiktokv.com',
                'app_name': 'musical_ly'
            }
        },
    }

    if os.path.exists(cookie_file):
        ydl_opts['cookiefile'] = cookie_file
    elif not debug:
        st.warning("⚠️ No 'tiktok_cookies.txt' found. Comments will likely be empty.")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info is the main heavy lifter
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            
            if not comments:
                return "EMPTY"
            
            return [{
                "Author": c.get('author'),
                "Text": c.get('text'),
                "Category": get_sentiment(c.get('text')),
                "Likes": c.get('like_count', 0),
                "URL": url
            } for c in comments]
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- UI SECTION ---
st.set_page_config(page_title="TikTok AI Sentiment", layout="wide")
st.title("🎵 TikTok Bulk Sentiment Analyzer")

with st.sidebar:
    st.header("Settings")
    debug_mode = st.checkbox("Enable Debug Mode", help="Shows the raw logs if things fail.")
    min_delay = st.slider("Min Delay (s)", 2, 10, 4)
    max_delay = st.slider("Max Delay (s)", 11, 30, 15)
    st.divider()
    if os.path.exists("tiktok_cookies.txt"):
        st.success("✅ Cookies detected")
    else
