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
        'no_warnings': True,
        # MIMIC A MODERN BROWSER EXACTLY
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        },
        'extractor_args': {
            'youtube': {'max_comments': ['50'], 'player_client': ['web']},
            'tiktok': {'max_comments': ['50']}
        }
    }
    
    # Path logic to use the cookies you successfully uploaded
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = "cookies.txt"
    elif os.path.exists("News/comments/cookies.txt"):
        ydl_opts['cookiefile'] = "News/comments/cookies.txt"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        comments = info.get('comments', [])
        return [{"Comment": c.get('text'), "Title": info.get('title', 'Video')} for c in comments if c.get('text')]

# --- 3. THE UI ---
st.set_page_config(page_title="News Intelligence", layout="wide")
st.title("📊 Social Intelligence Dashboard")

urls_input = st.text_area("Paste URLs (One per line):", height=150)

if st.button("🚀 Analyze Comments"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    if urls:
        all_results = []
        for url in urls:
            with st.spinner(f"Scraping {url}..."):
                try:
                    data = scrape_video_data(url)
                    for item in data:
                        score = sia.polarity_scores(str(item['Comment']))['compound']
                        all_results.append({
                            "Video": item['Title'], 
                            "Comment": item['Comment'], 
                            "Sentiment": "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
                        })
                except Exception as e:
                    st.error(f"Platform Error on {url}: {str(e)}")
        
        if all_results:
            df = pd.DataFrame(all_results)
            st.success(f"Successfully scraped {len(df)} comments!")
            st.bar_chart(df['Sentiment'].value_counts())
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No comments found. 1. Re-export your cookies.txt 2. Try a different video.")
