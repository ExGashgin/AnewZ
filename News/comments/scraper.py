import streamlit as st
import pandas as pd
import yt_dlp
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import ssl
import os

# --- 1. CLOUD INITIALIZATION ---
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

@st.cache_resource
def load_nltk():
    nltk.download('vader_lexicon')
    return SentimentIntensityAnalyzer()

sia = load_nltk()

# --- 2. GENRE BRAIN ---
GENRE_MAP = {
    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank", "dollar"],
    "Politics": ["election", "president", "minister", "parliament", "government"],
    "World": ["un", "nato", "global", "international", "world", "foreign"]
}

def analyze_comment(text):
    text_str = str(text).lower()
    genre = "General"
    for g, keywords in GENRE_MAP.items():
        if any(word in text_str for word in keywords):
            genre = g
            break
    score = sia.polarity_scores(text_str)['compound']
    label = "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
    return genre, score, label

# --- 3. THE SCRAPER ENGINE ---
def scrape_video_data(url):
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'extractor_args': {
            'youtube': {
                'max_comments': ['30'],
                'player_client': ['web_embedded', 'web']
            },
            'tiktok': {'max_comments': ['30']}
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
    }
    
    # Check for cookies file to bypass 403 Forbidden errors
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = 'cookies.txt'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        comments = info.get('comments', [])
        return [{"Comment": c.get('text'), "Video": info.get('title', 'Video')} for c in comments if c.get('text')]

# --- 4. DASHBOARD ---
st.set_page_config(page_title="News Intel", layout="wide")
st.title("📊 Social Intelligence Dashboard")

urls_input = st.text_area("Paste URLs (TikTok/YouTube):", height=100)

if st.button("🚀 Analyze"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    if urls:
        all_data = []
        for url in urls:
            try:
                # Add a small delay to avoid rate-limiting
                time_delay = 1
                data
