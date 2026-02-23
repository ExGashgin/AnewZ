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
        # FORCE player to use web_embedded to bypass some blocks
        'extractor_args': {
            'youtube': {
                'max_comments': ['30'],
                'player_client': ['web_embedded', 'web']
            },
            'tiktok': {'max_comments': ['30']}
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
    }
    
    # Check if user uploaded a cookies file to GitHub
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = 'cookies.txt'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        comments = info.get('comments', [])
        return [{"Comment": c.get('text'), "Video": info.get('title')} for c in comments if c.get('text')]

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
                data = scrape_video_data(url)
                for item in data:
                    g, s, l = analyze_comment(item['Comment'])
                    all_data.append({"Video": item['Video'], "Comment": item['Comment'], "Genre": g, "Sentiment": l, "Score": s})
            except Exception as e:
                st.error(f"Error on {url}: {e}")
        
        if all_data:
            df = pd.DataFrame(all_data)
            st.bar_chart(
