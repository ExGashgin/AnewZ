import streamlit as st
import pandas as pd
import yt_dlp
import os
import time
import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# Critical import for 2026 impersonation
from yt_dlp.networking.impersonate import ImpersonateTarget 

analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(text)
    return "Positive" if score['compound'] >= 0.05 else "Negative" if score['compound'] <= -0.05 else "Neutral"

def get_tiktok_data(url):
    cookie_file = "tiktok_cookies.txt"
    
    ydl_opts = {
        'getcomments': True, 
        'skip_download': True, 
        'quiet': True,
        'extract_flat': False,
        # 2026 Fix: Use the official target object to mimic Chrome
        'impersonate': ImpersonateTarget.from_str('chrome'),
        'extractor_args': {
            'tiktok': {
                'api_hostname': 'api22-normal-c-useast2a.tiktokv.com',
                'app_name': 'musical_ly'
            }
        },
    }

    if os.path.exists(cookie_file):
        ydl_opts['cookiefile'] = cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            
            if not comments:
                return "EMPTY"
                
            return [{
                "Author": c.get('author'),
                "Text": c.get('text'),
                "Category": get_sentiment(c.get('text')),
                "URL": url
            } for c in comments]
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- UI ---
st.set_page_config(page_title="TikTok AI Scraper", page_icon="🎵")
st.title("🎵 TikTok Sentiment Scraper (2026 Edition)")

if not os.path.exists("tiktok_cookies.txt"):
    st.error("🚨 Missing 'tiktok_cookies.txt'! TikTok will block anonymous requests.")

urls_input = st.text_area("Paste TikTok URLs (one per line):", height=150)

if st.button("Analyze Comments"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    all_results = []
    
    for idx, url in enumerate(urls):
        st.write(f"🔍 Checking: {url}")
        data = get_tiktok_data(url)
        
        if data == "EMPTY":
            st.warning("No comments found. Refresh your cookies or check if comments are disabled.")
        elif isinstance(data, str) and data.startswith("ERROR"):
            st.error(data)
        else:
            all_results.extend(data)
            st.success(f"Fetched {len(data)} comments.")
        
        # Human-like delay
        if idx < len(urls) - 1:
            time.sleep(random.uniform(5, 10))

    if all_results:
        df = pd.DataFrame(all_results)
        st.subheader("Summary")
        st.bar_chart(df['Category'].value_counts())
        st.dataframe(df)
        st.download_button("Download Data", df.to_csv(index=False), "tiktok_results.csv")
