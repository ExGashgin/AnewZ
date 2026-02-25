import streamlit as st
import pandas as pd
import yt_dlp
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 1. Setup
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(text)['compound']
    if score >= 0.05: return "Positive"
    elif score <= -0.05: return "Negative"
    return "Neutral"

# 2. Scrapers
def get_yt_comments(url):
    ydl_opts = {'getcomments': True, 'skip_download': True, 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return [{"Author": c.get('author'), "Text": c.get('text'), 
                     "Category": get_sentiment(c.get('text')), "URL": url} 
                    for c in info.get('comments', [])]
    except: return None

def get_fb_comments(post_id, token):
    # Meta Graph API Endpoint
    url = f"https://graph.facebook.com/v22.0/{post_id}/comments"
    params = {'access_token': token, 'fields': 'message,from'}
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if "error" in data:
        # This will show you exactly what's wrong (e.g., Error 100 or 200)
        st.error(f"⚠️ Meta Error: {data['error'].get('message')}")
        st.write(f"Error Type: {data['error'].get('type')}")
        return None
        
    return [{"Author": c.get('from', {}).get('name'), "Text": c.get('message'),
             "Category": get_sentiment(c.get('message')), "URL": post_id} 
            for c in data.get('data', [])]

# 3. Streamlit UI
st.set_page_config(page_title="Social Scraper", layout="wide")
st.title("📊 Multi-Platform Sentiment Analysis")

platform = st.sidebar.selectbox("Select Platform", ["YouTube", "Facebook"])

if platform == "YouTube":
    urls = st.text_area("Enter YouTube URLs (one per line):")
    if st.button("Analyze YouTube"):
        all_data = []
        for url in urls.split('\n'):
            if url.strip():
                data = get_yt_comments(url.strip())
                if data: all_data.extend(data)
        if all_data:
            df = pd.DataFrame(all_data)
            st.write(f"Analyzed {len(df)} comments")
            st.bar_chart(df['Category'].value_counts())
            st.dataframe(df)

else:
    token = st.sidebar.text_input("Enter Page Access Token", type="password")
    pids = st.text_area("Enter Facebook Post IDs (PageID_PostID):")
    if st.button("Analyze Facebook"):
        all_data = []
        for pid in pids.split('\n'):
            if pid.strip():
                data = get_fb_comments(pid.strip(), token)
                if data: all_data.extend(data)
        if all_data:
            df = pd.DataFrame(all_data)
            st.bar_chart(df['Category'].value_counts())
            st.dataframe(df)
