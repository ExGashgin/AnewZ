import streamlit as st
import pandas as pd
import yt_dlp
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import ssl
import time

# 1. INITIALIZATION (The "Fixes")
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# 2. YOUR GENRE BRAIN
GENRE_MAP = {
    "World": ["un", "nato", "global", "international", "world", "foreign"],
    "Politics": ["election", "president", "minister", "parliament", "government"],
    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank"],
    "Sports": ["football", "goal", "match", "league", "win", "player"],
    "Technology": ["ai", "tech", "software", "google", "meta", "cyber"],
    "Region": ["baku", "caucasus", "tbilisi", "karabakh"]
}

def analyze_comment(text):
    text_str = str(text).lower()
    genre = "General"
    for g, keywords in GENRE_MAP.items():
        if any(word in text_str for word in keywords):
            genre = g
            break
    score = sia.polarity_scores(text_str)['compound']
    label = "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
    return genre, score, label

# 3. UI LAYOUT
st.set_page_config(page_title="Social Intelligence", layout="wide")
st.title("📊 Social Media Comment Intelligence")

urls_input = st.text_area("Paste Video URLs (TikTok/YouTube) - One per line:", height=150)

if st.button("🚀 Scrape & Analyze"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    if not urls:
        st.warning("Please enter at least one URL.")
    else:
        results = []
        with st.spinner("Accessing social media... this may take a minute."):
            ydl_opts = {
                'getcomments': True,
                'skip_download': True,
                'quiet': True,
                'extractor_args': {'youtube': {'max_comments': ['50']}, 'tiktok': {'max_comments': ['50']}} 
            }
            
            for url in urls:
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        comments = info.get('comments', [])
                        for c in comments:
                            if c.get('text'):
                                g, s, l = analyze_comment(c.get('text'))
                                results.append({
                                    "Video": info.get('title', 'Video'),
                                    "Comment": c.get('text'),
                                    "Genre": g,
                                    "Sentiment": l,
                                    "Score": s
                                })
                except Exception as e:
                    st.error(f"Error scraping {url}: {e}")

        if results:
            df = pd.DataFrame(results)
            
            # --- DASHBOARD VISUALS ---
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Sentiment Breakdown")
                st.bar_chart(df['Sentiment'].value_counts())
            
            with col2:
                st.subheader("Genre Distribution")
                st.table(df['Genre'].value_counts())

            st.subheader("Detailed Analysis")
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download Results", df.to_csv(index=False), "analysis.csv")
