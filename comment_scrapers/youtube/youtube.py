import streamlit as st
import pandas as pd
import yt_dlp
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize the analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text:
        return "Neutral"
    score = analyzer.polarity_scores(str(text))
    compound = score['compound']
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def format_timestamp(ts):
    """Converts Unix timestamp to readable date string"""
    if ts:
        try:
            return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return "Unknown"
    return "N/A"

def get_comments_bulk(url):
    ydl_opts = {
        'getcomments': True, 
        'skip_download': True, 
        'quiet': True, 
        'max_comments': 50,
        'no_warnings': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            
            results = []
            for c in comments:
                comment_text = c.get('text')
                results.append({
                    "Comment_ID": c.get('id'),
                    "Comment_Author": c.get('author'),
                    "Comment_Text": comment_text,
                    "Sentiment_Category": get_sentiment(comment_text),
                    "Comment_Date": format_timestamp(c.get('timestamp')) # <--- CONVERTED DATE
                })
            return results
    except Exception as e:
        st.error(f"Error scraping {url}: {e}")
        return None

# --- UI SECTION ---
st.set_page_config(page_title="YouTube Bulk Scraper", layout="wide")
st.title("📊 Bulk YouTube Scraper (File Upload)")

st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df_input = pd.read_csv(uploaded_file
