import streamlit as st
import pandas as pd
import yt_dlp
import os
import time
import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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
            # Extracting info
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
st.info("💡 Note: A random delay is active between videos to prevent TikTok from blocking your IP.")

urls_input = st.text_area("Paste TikTok URLs (one per line):")

if st.button("Start Scraping"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    all_data = []
    
    total_urls = len(urls)
    for idx, url in enumerate(urls):
        st.write(f"🔄 Processing ({idx+1}/{total_urls}): {url}")
        
        data = get_tiktok_comments(url)
        if data:
            all_data.extend(data)
            st.success(f"✅ Found {len(data)} comments.")
        
        # --- DELAY LOGIC ---
        if idx < total_urls - 1: # No need to wait after the very last video
            wait_time = random.uniform(4.0, 9.0) # Random float between 4 and 9 seconds
            st.write(f"⏳ Mimicking human scroll... waiting {wait_time:.1f}s")
            time.sleep(wait_time)
            
    if all_data:
        df = pd.DataFrame(all_data)
        st.subheader("Results Summary")
        st.bar_chart(df['Category'].value_counts())
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "tiktok_analysis.csv")
