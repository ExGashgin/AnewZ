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

# --- 2. GENRE BRAIN ---
GENRE_MAP = {
    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank"],
    "Politics": ["election", "president", "minister", "parliament", "government"],
    "World": ["un", "nato", "global", "international", "world", "foreign"]
}

def analyze_text(text):
    text_str = str(text).lower()
    genre = "General"
    for g, keywords in GENRE_MAP.items():
        if any(word in text_str for word in keywords):
            genre = g
            break
    score = sia.polarity_scores(text_str)['compound']
    label = "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
    return genre, label, score

# --- 3. SCRAPER ENGINE ---
def scrape_video_data(url):
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        },
        'extractor_args': {
            'youtube': {'max_comments': ['50'], 'player_client': ['web']},
            'tiktok': {'max_comments': ['50']}
        }
    }
    
    # Detect cookies.txt in current or News/comments/ directory
    paths = ["cookies.txt", "News/comments/cookies.txt"]
    for path in paths:
        if os.path.exists(path):
            ydl_opts['cookiefile'] = path
            break

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        comments = info.get('comments', [])
        return [{"Comment": c.get('text'), "Title": info.get('title', 'Video')} for c in comments if c.get('text')]

# --- 4. DASHBOARD UI ---
st.set_page_config(page_title="News Intel", layout="wide")
st.title("📊 Social Intelligence Dashboard")

if not os.path.exists("cookies.txt"):
    st.sidebar.warning("⚠️ cookies.txt not found. Scraping may be limited or blocked.")
else:
    st.sidebar.success("✅ cookies.txt detected.")

urls_input = st.text_area("Paste URLs (TikTok/YouTube):", height=100)

if st.button("🚀 Analyze"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    if urls:
        all_results = []
        for url in urls:
            try:
                data = scrape_video_data(url)
                for item in data:
                    g, l, s = analyze_text(item['Comment'])
                    all_results.append({
                        "Video": item['Title'], 
                        "Comment": item['Comment'], 
                        "Genre": g, 
                        "Sentiment": l, 
                        "Score": s
                    })
            except Exception as e:
                st.error(f"Error on {url}: {e}")
        
        if all_results:
            df = pd.DataFrame(all_results)
            st.subheader("Sentiment Distribution")
            # FIXED SYNTAX: Ensure counts are calculated before plotting
            counts = df['Sentiment'].value_counts()
            st.bar_chart(counts)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No comments retrieved. Ensure cookies.txt is valid and uploaded.")
