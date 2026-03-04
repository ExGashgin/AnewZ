import streamlit as st
import pandas as pd
import yt_dlp
import os
import time
import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from yt_dlp.networking.impersonate import ImpersonateTarget 

# 1. Error Guard: Ensures the app doesn't go white on startup
try:
    analyzer = SentimentIntensityAnalyzer()

    def get_sentiment(text):
        if not text: return "Neutral"
        score = analyzer.polarity_scores(text)
        return "Positive" if score['compound'] >= 0.05 else "Negative" if score['compound'] <= -0.05 else "Neutral"

    def scrape_tiktok(url):
        cookie_path = "tiktok_cookies.txt"
        if not os.path.exists(cookie_path):
            return "ERROR: Missing tiktok_cookies.txt file."

        ydl_opts = {
            'getcomments': True,
            'skip_download': True,
            'quiet': True,
            'cookiefile': cookie_path,
            'impersonate': ImpersonateTarget.from_str('chrome'),
            'extractor_args': {'tiktok': {'api_hostname': 'api22-normal-c-useast2a.tiktokv.com'}},
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            return comments if comments else "EMPTY"

    # --- UI START ---
    st.set_page_config(page_title="TikTok Scraper")
    st.title("🎵 TikTok Sentiment Analysis")

    # Double check dependencies in UI
    if not os.path.exists("tiktok_cookies.txt"):
        st.error("Please put your 'tiktok_cookies.txt' in the folder and refresh.")
    
    url = st.text_input("Enter TikTok URL:")

    if st.button("Analyze"):
        if url:
            with st.spinner("Bypassing TikTok security..."):
                result = scrape_tiktok(url)
                
                if isinstance(result, list):
                    data = []
                    for c in result:
                        data.append({
                            "User": c.get('author'),
                            "Comment": c.get('text'),
                            "Sentiment": get_sentiment(c.get('text'))
                        })
                    df = pd.DataFrame(data)
                    st.success(f"Fetched {len(df)} comments!")
                    st.bar_chart(df['Sentiment'].value_counts())
                    st.dataframe(df)
                else:
                    st.error(f"Failed: {result}")
        else:
            st.warning("Please enter a URL first.")

except Exception as e:
    st.error(f"Crticial App Error: {e}")
    st.write("Check your terminal for more details.")
