import streamlit as st
import pandas as pd
import yt_dlp
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- 1. SETUP & SENTIMENT LOGIC ---
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(str(text))['compound']
    if score >= 0.05: return "Positive"
    elif score <= -0.05: return "Negative"
    return "Neutral"

# --- 2. SCRAPER FUNCTIONS ---

def get_yt_comments(url):
    ydl_opts = {'getcomments': True, 'skip_download': True, 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            return [{
                "Author": c.get('author'), 
                "Text": c.get('text'), 
                "Category": get_sentiment(c.get('text')), 
                "Source_URL": url
            } for c in comments]
    except Exception as e:
        st.warning(f"Could not fetch YouTube comments for {url}: {e}")
        return None

def get_meta_comments(item_id, token, platform_label="Meta"):
    """Handles both Facebook Post IDs and Instagram Media IDs via Graph API"""
    # Endpoint is the same for both: /{object-id}/comments
    url = f"https://graph.facebook.com/v22.0/{item_id}/comments"
    # Instagram uses 'text', Facebook uses 'message'
    fields = "text,username" if platform_label == "Instagram" else "message,from"
    params = {'access_token': token, 'fields': fields}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error" in data:
            st.error(f"⚠️ {platform_label} Error ({item_id}): {data['error'].get('message')}")
            return None
            
        results = []
        for c in data.get('data', []):
            # Extract text and author based on platform-specific keys
            text = c.get('text') if platform_label == "Instagram" else c.get('message')
            author = c.get('username') if platform_label == "Instagram" else c.get('from', {}).get('name')
            
            results.append({
                "Author": author,
                "Text": text,
                "Category": get_sentiment(text),
                "Source_ID": item_id
            })
        return results
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# --- 3. UI SECTION ---
st.set_page_config(page_title="Social Sentiment Scraper", layout="wide")
st.title("📊 Multi-
