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

# --- 2. THE SCRAPER ENGINE ---
def scrape_video_data(url):
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        },
        'extractor_args': {
            'youtube': {'max_comments': ['30'], 'player_client': ['web']},
            'tiktok': {'max_comments': ['30']}
        }
    }
    
    # Updated path to match your GitHub structure
    cookie_path = "News/comments/cookies.txt"
    if os.path.exists(cookie_path):
        ydl_opts['cookiefile'] = cookie_path
        st.sidebar.success(f"✅ Found cookies at: {cookie_path}")
    else:
        st.sidebar.error("🚨 cookies.txt NOT found in News/comments/")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        comments = info.get('comments', [])
        return [{"Comment": c.get('text'), "Title": info.get('title', 'Video')} for c in comments if c.get('text')]

# --- 3. DASHBOARD UI ---
st.set_page_config(page_title="News Intelligence", layout="wide")
st.title("📊 Social Intelligence Dashboard")

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
                st.error(f"Error on {url}: {e}")
        
        if all_results:
            df = pd.DataFrame(all_results)
            st.subheader("Sentiment Summary")
            # Bar chart fix
            counts = df['Sentiment'].value_counts()
            st.bar_chart(counts)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No comments found. Try refreshing your cookies.txt file.")
