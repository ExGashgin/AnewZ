import streamlit as st
import pandas as pd
import yt_dlp
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize the analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text:
        return "Neutral"
    score = analyzer.polarity_scores(text)
    compound = score['compound']
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# --- NEW: FACEBOOK SCRAPER FUNCTION ---
def get_fb_comments(post_id, access_token):
    # Meta Graph API Endpoint for 2026
    url = f"https://graph.facebook.com/v22.0/{post_id}/comments"
    params = {
        'access_token': access_token,
        'limit': 100,  # Get up to 100 comments per request
        'fields': 'from,message,created_time'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            st.error(f"Meta Error: {data['error']['message']}")
            return None
            
        results = []
        for c in data.get('data', []):
            msg = c.get('message')
            results.append({
                "Author": c.get('from', {}).get('name', 'Anonymous'),
                "Text": msg,
                "Category": get_sentiment(msg),
                "URL": f"https://facebook.com/{post_id}"
            })
        return results
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# --- EXISTING: YOUTUBE SCRAPER FUNCTION ---
def get_yt_comments_bulk(url):
    ydl_opts = {'getcomments': True, 'skip_download': True, 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            return [{"Author": c.get('author'), "Text": c.get('text'), 
                     "Category": get_sentiment(c.get('text')), "URL": url} for c in comments]
    except Exception:
        return None

# --- UI SECTION ---
st.title("📊 Multi-Platform Sentiment Scraper")

tab1, tab2 = st.tabs(["YouTube", "Facebook"])

with tab1:
    urls_input = st.text_area("Paste YouTube URLs:", key="yt_input")
    if st.button("Scrape YouTube"):
        urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
        all_data = []
        for url in urls:
            data = get_yt_comments_bulk(url)
            if data: all_data.extend(data)
        
        if all_data:
            df = pd.DataFrame(all_data)
            st.bar_chart(df['Category'].value_counts())
            st.dataframe(df)

with tab2:
    fb_token = st.text_input("Enter Page Access Token:", type="password")
    post_ids_input = st.text_area("Enter Facebook Post IDs (one per line):", 
                                 help="Format: pageid_postid")
    
    if st.button("Scrape Facebook"):
        if not fb_token:
            st.warning("Please provide a valid Page Access Token.")
        else:
            ids = [i.strip() for i in post_ids_input.split('\n') if i.strip()]
            all_fb_data = []
            for pid in ids:
                st.write(f"Fetching FB Post: {pid}")
                data = get_fb_comments(pid, fb_token)
                if data: all_fb_data.extend(data)
            
            if all_fb_data:
                df_fb = pd.DataFrame(all_fb_data)
                st.bar_chart(df_fb['Category'].value_counts())
                st.dataframe(df_fb)
                st.download_button("Download FB Data", df_fb.to_csv(index=False), "fb_comments.csv")
