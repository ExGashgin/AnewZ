import streamlit as st
import pandas as pd
import yt_dlp
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import ssl

# --- 1. CLOUD-READY INITIALIZATION ---
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# --- 2. GENRE BRAIN ---
GENRE_MAP = {
    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank"],
    "Politics": ["election", "president", "minister", "parliament", "government"],
    "World": ["un", "nato", "global", "international", "world", "foreign"]
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

# --- 3. DASHBOARD INTERFACE ---
st.set_page_config(page_title="Social Intelligence", layout="wide")
st.title("📊 Social Media Intelligence Dashboard")

urls_input = st.text_area("Enter Video URLs (TikTok/YouTube) - One per line:", height=100)

if st.button("🚀 Analyze Comments"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    if urls:
        results = []
        with st.spinner("Scraping live data..."):
            # Options to prevent "403 Forbidden" or "Unavailable" errors
            ydl_opts = {
                'getcomments': True,
                'skip_download': True,
                'quiet': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'extractor_args': {'youtube': {'max_comments': ['30']}, 'tiktok': {'max_comments': ['30']}}
            }
            
            for url in urls:
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        comments = info.get('comments', [])
                        for c in comments:
                            if c.get('text'):
                                g, s, l = analyze_comment(c.get('text'))
                                results.append({"Comment": c.get('text'), "Genre": g, "Sentiment": l, "Score": s})
                except Exception as e:
                    st.error(f"Error on {url}: {e}")

        if results:
            df = pd.DataFrame(results)
            st.subheader("Real-Time Sentiment Analysis")
            # Create the chart
            chart_data = df.groupby(['Genre', 'Sentiment']).size().unstack().fillna(0)
            st.bar_chart(chart_data)
            # Show the table
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("Please paste at least one URL.")
