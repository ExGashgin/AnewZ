import streamlit as st
import pandas as pd
import yt_dlp
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import ssl
import time

# --- 1. CLOUD INITIALIZATION (Prevents LookupErrors) ---
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

@st.cache_resource
def load_nltk():
    nltk.download('vader_lexicon')
    return SentimentIntensityAnalyzer()

sia = load_nltk()

# --- 2. THE GENRE BRAIN ---
GENRE_MAP = {
    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank", "dollar"],
    "Politics": ["election", "president", "minister", "parliament", "government", "protest"],
    "World": ["un", "nato", "global", "international", "world", "foreign", "diplomacy"],
    "Technology": ["ai", "tech", "software", "google", "meta", "cyber", "robot"],
    "Region": ["baku", "caucasus", "tbilisi", "karabakh", "central asia"]
}

def analyze_comment(text):
    text_str = str(text).lower()
    # Detect Genre
    genre = "General"
    for g, keywords in GENRE_MAP.items():
        if any(word in text_str for word in keywords):
            genre = g
            break
    
    # Detect Sentiment
    score = sia.polarity_scores(text_str)['compound']
    label = "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
    
    return genre, score, label

# --- 3. THE SCRAPER ENGINE ---
def scrape_video_data(url):
    # These options help bypass "Video Unavailable" errors on Cloud IPs
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        },
        'extractor_args': {
            'youtube': {'max_comments': ['50'], 'player_client': ['web']},
            'tiktok': {'max_comments': ['50']}
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_title = info.get('title', 'Unknown Video')
        comments = info.get('comments', [])
        
        parsed_comments = []
        for c in comments:
            if c.get('text'):
                genre, score, label = analyze_comment(c.get('text'))
                parsed_comments.append({
                    "Video Title": video_title,
                    "Comment": c.get('text'),
                    "Genre": genre,
                    "Sentiment": label,
                    "Score": score
                })
        return parsed_comments

# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="News Intelligence", layout="wide")

st.title("📝 Social Media Intelligence Dashboard")
st.markdown("Analyze audience sentiment and topics from **TikTok** and **YouTube** URLs.")

# Sidebar for controls
with st.sidebar:
    st.header("Settings")
    st.info("Currently set to scrape up to 50 comments per video to maintain speed.")

# Input Area
urls_input = st.text_area("Paste Video URLs (one per line):", placeholder="https://www.tiktok.com/@user/video/...", height=150)

if st.button("🚀 Run Intelligence Analysis"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    
    if not urls:
        st.error("Please enter at least one valid URL.")
    else:
        all_results = []
        progress_bar = st.progress(0)
        
        for idx, url in enumerate(urls):
            with st.status(f"Analyzing {url}...", expanded=True) as status:
                try:
                    data = scrape_video_data(url)
                    all_results.extend(data)
                    status.update(label=f"✅ {url} analyzed!", state="complete")
                except Exception as e:
                    st.error(f"Failed to scrape {url}: {str(e)}")
            
            progress_bar.progress((idx + 1) / len(urls))

        if all_results:
            df = pd.DataFrame(all_results)
            
            # --- VISUALIZATIONS ---
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Sentiment Distribution")
                sentiment_counts = df['Sentiment'].value_counts()
                st.bar_chart(sentiment_counts)
                
            with col2:
                st.subheader("Top Genres Detected")
                genre_counts = df['Genre'].value_counts()
                st.table(genre_counts)

            st.subheader("Detailed Data")
            st.dataframe(df, use_container_width=True)
            
            # Download Button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Analysis as CSV", data=csv, file_name="social_analysis.csv", mime="text/csv")
        else:
            st.warning("No comments were retrieved. This often happens if the video is private or the platform is blocking the request.")
