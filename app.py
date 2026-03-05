import streamlit as st
import pandas as pd
import yt_dlp
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- 1. SETUP ---
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(str(text))['compound']
    if score >= 0.05: return "Positive"
    elif score <= -0.05: return "Negative"
    return "Neutral"

# --- 2. API SCRAPERS ---

def get_yt_comments(url):
    # Added 'max_comments' to prevent infinite loading on huge videos
    ydl_opts = {'getcomments': True, 'skip_download': True, 'quiet': True, 'max_comments': 50}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            return [{"Author": c.get('author'), "Text": c.get('text'), 
                     "Category": get_sentiment(c.get('text')), "Source": "YouTube"} 
                    for c in comments]
    except Exception as e:
        return None

def get_meta_comments(obj_id, token, platform="Facebook"):
    # Using a 10-second timeout to prevent the app from hanging
    url = f"https://graph.facebook.com/v22.0/{obj_id}/comments"
    fields = 'text,username' if platform == "Instagram" else 'message,from'
    params = {'access_token': token, 'fields': fields}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "error" in data:
            st.warning(f"{platform} ID {obj_id}: {data['error'].get('message')}")
            return None
            
        results = []
        for c in data.get('data', []):
            text = c.get('text') if platform == "Instagram" else c.get('message')
            author = c.get('username') if platform == "Instagram" else c.get('from', {}).get('name')
            results.append({
                "Author": author,
                "Text": text,
                "Category": get_sentiment(text),
                "Source": platform
            })
        return results
    except Exception:
        return None

# --- 3. UI ---
st.set_page_config(page_title="Social Scraper", layout="wide")
st.title("📊 Social Sentiment Scraper")

platform = st.sidebar.selectbox("Platform", ["YouTube", "Facebook", "Instagram"])
token = st.sidebar.text_input("Access Token (Meta Only)", type="password") if platform != "YouTube" else ""

# File or Text Input
uploaded_file = st.sidebar.file_uploader("Upload List", type=["csv", "xlsx"])
raw_input = st.text_area(f"Paste {platform} IDs/URLs (One per line):")

if st.button("Start Analysis"):
    # Determine IDs to process
    items = []
    if uploaded_file:
        df_in = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        items = df_in.iloc[:, 0].dropna().tolist()
    else:
        items = [i.strip() for i in raw_input.split('\n') if i.strip()]

    if not items:
        st.error("No input found.")
    else:
        all_data = []
        prog = st.progress(0)
        
        for idx, item in enumerate(items):
            if platform == "YouTube":
                data = get_yt_comments(item)
            else:
                data = get_meta_comments(item, token, platform)
            
            if data: all_data.extend(data)
            prog.progress((idx + 1) / len(items))
        
        if all_data:
            df = pd.DataFrame(all_data)
            st.success(f"Analysis Complete! Found {len(df)} comments.")
            st.dataframe(df)
            st.download_button("Download CSV", df.to_csv(index=False), "results.csv")
        else:
            st.error("No comments retrieved. Verify your IDs and Token permissions.")
