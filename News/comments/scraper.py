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

# --- 2. THE SEARCH ENGINE ---
def find_the_file(filename):
    # This checks the current folder, the News folder, and the comments folder
    search_locations = [
        filename,
        os.path.join("News", "comments", filename),
        os.path.join("comments", filename),
        os.path.abspath(filename)
    ]
    for loc in search_locations:
        if os.path.exists(loc):
            return loc
    return None

# --- 3. THE SCRAPER ---
def scrape_video_data(url):
    cookie_path = find_the_file("cookies.txt")
    
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
    
    if cookie_path:
        ydl_opts['cookiefile'] = cookie_path
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        comments = info.get('comments', [])
        return [{"Comment": c.get('text'), "Title": info.get('title', 'Video')} for c in comments if c.get('text')]

# --- 4. THE UI ---
st.set_page_config(page_title="News Intel", layout="wide")
st.title("📊 Social Intelligence Dashboard")

# Visual Debugger for you
found_path = find_the_file("cookies.txt")
if found_path:
    st.sidebar.success(f"✅ Found cookies at: {found_path}")
else:
    st.sidebar.error("❌ cookies.txt NOT found. Please move it to the main folder.")

urls_input = st.text_area("Paste URLs:", height=100)

if st.button("🚀 Analyze"):
    if not found_path:
        st.error("I cannot start without the cookies.txt file.")
    else:
        results = []
        urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
        for url in urls:
            try:
                data = scrape_video_data(url)
                for item in data:
                    score = sia.polarity_scores(str(item['Comment']))['compound']
                    results.append({
                        "Video": item['Title'], 
                        "Comment": item['Comment'], 
                        "Sentiment": "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
                    })
            except Exception as e:
                st.error(f"Error: {e}")
        
        if results:
            df = pd.DataFrame(results)
            st.bar_chart(df['Sentiment'].value_counts())
            st.dataframe(df, use_container_width=True)
