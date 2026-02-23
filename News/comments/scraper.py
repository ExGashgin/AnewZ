import streamlit as st
import pandas as pd
import yt_dlp
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import ssl
import os

# --- 1. INITIALIZATION ---
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

@st.cache_resource
def load_tools():
    nltk.download('vader_lexicon')
    return SentimentIntensityAnalyzer()

sia = load_tools()

# --- 2. ADVANCED COOKIE SEARCH ---
def find_cookies():
    # List of every possible place the file could be
    search_paths = [
        "cookies.txt",
        "News/comments/cookies.txt",
        "comments/cookies.txt",
        os.path.join(os.getcwd(), "cookies.txt"),
        os.path.join(os.getcwd(), "News/comments/cookies.txt")
    ]
    for path in search_paths:
        if os.path.exists(path):
            return path
    return None

# --- 3. THE SCRAPER ENGINE ---
def scrape_video_data(url):
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        },
        'extractor_args': {
            'youtube': {'max_comments': ['30'], 'player_client': ['web']},
            'tiktok': {'max_comments': ['30']}
        }
    }
    
    path = find_cookies()
    if path:
        ydl_opts['cookiefile'] = path
        st.sidebar.success(f"✅ Active: {path}")
    else:
        st.sidebar.error("❌ cookies.txt NOT found in any folder.")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        comments = info.get('comments', [])
        return [{"Comment": c.get('text'), "Title": info.get('title', 'Video')} for c in comments if c.get('text')]

# --- 4. DASHBOARD UI ---
st.set_page_config(page_title="News Intel", layout="wide")
st.title("📊 Social Intelligence Dashboard")

# Debugger to help you see where the app is looking
if st.sidebar.checkbox("Show System Folders"):
    st.sidebar.write("Current Folder:", os.getcwd())
    st.sidebar.write("Files here:", os.listdir("."))

urls_input = st.text_area("Paste URLs (TikTok/YouTube):", height=100)

if st.button("🚀 Analyze"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    if urls:
        all_results = []
        for url in urls:
            try:
                data = scrape_video_data(url)
                for item in data:
                    score = sia.polarity_scores(str(item['Comment']))['compound']
                    label = "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
                    all_results.append({
                        "Video": item['Title'], 
                        "Comment": item['Comment'], 
                        "Sentiment": label
                    })
            except Exception as e:
                st.error(f"Error: {e}")
        
        if all_results:
            df = pd.DataFrame(all_results)
            st.bar_chart(df['Sentiment'].value_counts())
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No comments found. Try a different video or fresh cookies.")
