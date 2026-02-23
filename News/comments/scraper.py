import streamlit as st
import pandas as pd
import yt_dlp
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import ssl

# --- INITIALIZATION ---
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# --- GENRE BRAIN ---
GENRE_MAP = {
    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank", "dollar"],
    "Politics": ["election", "president", "minister", "parliament", "government"],
    "World": ["un", "nato", "global", "international", "world", "foreign"],
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

# --- UI LAYOUT ---
st.set_page_config(page_title="Social Intelligence", layout="wide")
st.title("📊 Social Media Comment Intelligence")

urls_input = st.text_area("Paste Video URLs (One per line):", height=100)

if st.button("🚀 Scrape & Analyze"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    if urls:
        results = []
        with st.spinner("Accessing social media..."):
            # yt-dlp options specifically for cloud servers
            ydl_opts = {
                'getcomments': True,
                'skip_download': True,
                'quiet': True,
                'extractor_args': {'youtube': {'max_comments': ['50']}, 'tiktok': {'max_comments': ['50']}},
                'player_client': ['web_safari'] # Mimics real browser to avoid 403 blocks
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
            st.subheader("Sentiment vs Genre Breakdown")
            chart_data = df.groupby(['Genre', 'Sentiment']).size().unstack().fillna(0)
            st.bar_chart(chart_data)
            st.dataframe(df, use_container_width=True)
