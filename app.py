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
    return "Positive" if score['compound'] >= 0.05 else "Negative" if score['compound'] <= -0.05 else "Neutral"

def get_tiktok_comments(url):
    cookie_file = "tiktok_cookies.txt"
    ydl_opts = {
        'getcomments': True, 
        'skip_download': True, 
        'quiet': True,
        'extract_flat': False,
        'no_warnings': True,
    }

    if os.path.exists(cookie_file):
        ydl_opts['cookiefile'] = cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            return [{
                "Author": c.get('author'),
                "Text": c.get('text'),
                "Category": get_sentiment(c.get('text')),
                "URL": url
            } for c in comments]
    except Exception as e:
        st.error(f"Error on {url}: {str(e)}")
        return None

# --- UI SECTION ---
st.title("🎵 TikTok Sentiment Scraper (Human Mode)")
st.info("💡 A random delay (4–9s) is active to prevent TikTok IP blocks.")

urls_input = st.text_area("Paste TikTok URLs (one per line):")

if st.button("Start Scraping"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    all_data = []
    
    for idx, url in enumerate(urls):
        st.write(f"🔄 Processing ({idx+1}/{len(urls)}): {url}")
        data = get_tiktok_comments(url)
        if data:
            all_data.extend(data)
            st.success(f"✅ Found {len(data)} comments.")
        
        # Human-like delay logic
        if idx < len(urls) - 1:
            wait_time = random.uniform(4.0, 9.0)
            st.write(f"⏳ Waiting {wait_time:.1f}s to avoid detection...")
            time.sleep(wait_time)
            
    if all_data:
        df = pd.DataFrame(all_data)
        st.bar_chart(df['Category'].value_counts())
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "tiktok_analysis.csv")
