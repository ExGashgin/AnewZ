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

# --- UI SECTION ---
st.set_page_config(page_title="Social Scraper", layout="wide")
st.title("📊 Bulk Sentiment Scraper (File Upload)")

platform = st.sidebar.selectbox("Select Platform", ["YouTube", "Facebook"])

# File Uploader in the sidebar or main page
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel list", type=["csv", "xlsx"])

if platform == "YouTube":
    # Fallback to text area if no file is uploaded
    urls_input = st.text_area("OR Paste YouTube URLs (one per line):")
    
    if st.button("Analyze YouTube"):
        urls = []
        if uploaded_file:
            # Read from uploaded file (assumes URLs are in the first column)
            df_input = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            urls = df_input.iloc[:, 0].dropna().tolist()
        else:
            urls = [u.strip() for u in urls_input.split('\n') if u.strip()]

        if urls:
            all_data = []
            progress_bar = st.progress(0)
            for i, url in enumerate(urls):
                data = get_yt_comments(url)
                if data: all_data.extend(data)
                progress_bar.progress((i + 1) / len(urls))
            
            if all_data:
                df = pd.DataFrame(all_data)
                st.bar_chart(df['Category'].value_counts())
                st.dataframe(df)
                st.download_button("Download Results", df.to_csv(index=False), "yt_results.csv")

else: # Facebook
    token = st.sidebar.text_input("Enter Page Access Token", type="password")
    pids_input = st.text_area("OR Enter FB Post IDs (one per line):")
    
    if st.button("Analyze Facebook"):
        pids = []
        if uploaded_file:
            df_input = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            pids = df_input.iloc[:, 0].dropna().tolist()
        else:
            pids = [p.strip() for p in pids_input.split('\n') if p.strip()]

        if pids:
            all_data = []
            for pid in pids:
                data = get_fb_comments(pid, token)
                if data: all_data.extend(data)
            
            if all_data:
                df = pd.DataFrame(all_data)
                st.bar_chart(df['Category'].value_counts())
                st.dataframe(df)
                st.download_button("Download Results", df.to_csv(index=False), "fb_results.csv")
