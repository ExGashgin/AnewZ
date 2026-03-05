import streamlit as st
import pandas as pd
import yt_dlp
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Setup
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(str(text))['compound']
    if score >= 0.05: return "Positive"
    elif score <= -0.05: return "Negative"
    return "Neutral"

# --- Scrapers ---

def get_yt_comments(url):
    # 'getcomments': True pulls all metadata available for YT comments
    ydl_opts = {'getcomments': True, 'skip_download': True, 'quiet': True, 'max_comments': 50}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            for c in comments:
                c['Sentiment_Category'] = get_sentiment(c.get('text'))
            return comments
    except: return None

def get_meta_comments(obj_id, token, platform):
    # We add more fields here to ensure we get "all" columns from Meta
    fields = "text,username,timestamp,like_count" if platform == "Instagram" else "message,from,created_time,like_count"
    url = f"https://graph.facebook.com/v22.0/{obj_id}/comments"
    
    try:
        r = requests.get(url, params={'access_token': token, 'fields': fields}, timeout=15).json()
        if "error" in r: 
            st.error(f"Error: {r['error'].get('message')}")
            return None
        
        data = r.get('data', [])
        for c in data:
            # Analyze sentiment based on 'text' (IG) or 'message' (FB)
            content = c.get('text') if platform == "Instagram" else c.get('message')
            c['Sentiment_Category'] = get_sentiment(content)
        return data
    except: return None

# --- UI ---
st.set_page_config(page_title="Bulk Scraper", layout="wide")
st.title("📊 Social Scraper (Full Data Export)")

platform = st.sidebar.selectbox("Platform", ["YouTube", "Facebook", "Instagram"])
token = st.sidebar.text_input("Access Token", type="password") if platform != "YouTube" else ""
raw_input = st.text_area("Paste IDs/URLs (one per line):")

if st.button("Run Full Analysis"):
    items = [i.strip() for i in raw_input.split('\n') if i.strip()]
    all_results = []
    
    for item in items:
        res = get_yt_comments(item) if platform == "YouTube" else get_meta_comments(item, token, platform)
        if res: all_results.extend(res)
    
    if all_results:
        df = pd.DataFrame(all_results)
        
        # Move Sentiment to the first column so it's easy to see
        cols = ['Sentiment_Category'] + [c for c in df.columns if c != 'Sentiment_Category']
        df = df[cols]
        
        st.write(f"✅ Success! Captured {len(df)} rows with {len(df.columns)} columns.")
        st.dataframe(df)
        st.download_button("Download Full CSV", df.to_csv(index=False), "full_export.csv")
    else:
        st.error("No data found. Check logs or token.")
