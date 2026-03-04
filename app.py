import streamlit as st
import pandas as pd
import yt_dlp
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize the analyzer
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
    }

    # Automatically use cookies if the file exists
    if os.path.exists(cookie_file):
        ydl_opts['cookiefile'] = cookie_file
    else:
        st.warning("No 'tiktok_cookies.txt' found. Scrape might fail or be limited.")

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
        st.error(f"Error: {str(e)}")
        return None

# --- UI SECTION ---
st.title("🎵 TikTok Sentiment Scraper")
urls_input = st.text_area("Paste TikTok URLs (one per line):")

if st.button("Scrape TikTok"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    all_data = []
    
    for url in urls:
        st.write(f"🔍 Accessing: {url}")
        data = get_tiktok_comments(url)
        if data: all_data.extend(data)
            
    if all_data:
        df = pd.DataFrame(all_data)
        st.bar_chart(df['Category'].value_counts())
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "tiktok_analysis.csv")
