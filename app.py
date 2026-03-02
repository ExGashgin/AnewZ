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

def get_yt_dlp_comments(url, platform_label):
    """Handles both YouTube and TikTok via yt-dlp"""
    ydl_opts = {
        'getcomments': True, 
        'skip_download': True, 
        'quiet': True,
        'extract_flat': True,
        'check_formats': False
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            if not comments:
                return None
            return [{
                "Author": c.get('author') or c.get('author_id'), 
                "Text": c.get('text'), 
                "Category": get_sentiment(c.get('text')), 
                "Source_URL": url
            } for c in comments]
    except Exception as e:
        st.warning(f"Could not fetch {platform_label} comments for {url}: {e}")
        return None

def get_meta_comments(item_id, token, platform_label="Meta"):
    """Handles both Facebook Post IDs and Instagram Media IDs via Graph API"""
    url = f"https://graph.facebook.com/v22.0/{item_id}/comments"
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
st.title("📊 Multi-Platform Sentiment Scraper")
st.markdown("Analyze comments from **YouTube**, **TikTok**, **Facebook**, or **Instagram**.")

# Sidebar Configuration
st.sidebar.header("Settings")
platform = st.sidebar.selectbox("Select Platform", ["YouTube", "TikTok", "Facebook", "Instagram"])
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel list", type=["csv", "xlsx"])

# Platform-specific token inputs
token = ""
if platform in ["Facebook", "Instagram"]:
    token = st.sidebar.text_input(f"Enter {platform} Access Token", type="password")

# --- 4. EXECUTION LOGIC ---

input_list = []
if uploaded_file:
    df_input = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    input_list = df_input.iloc[:, 0].dropna().tolist()
else:
    label = f"{platform} URLs" if platform in ["YouTube", "TikTok"] else f"{platform} Object IDs"
    text_input = st.text_area(f"Paste {label} (one per line):")
    input_list = [i.strip() for i in text_input.split('\n') if i.strip()]

if st.button(f"Analyze {platform}"):
    if not input_list:
        st.warning("Please provide IDs or upload a file.")
    elif platform in ["Facebook", "Instagram"] and not token:
        st.error("Access Token is required for Meta platforms.")
    else:
        all_data = []
        progress_bar = st.progress(0)
        
        for i, item in enumerate(input_list):
            if platform in ["YouTube", "TikTok"]:
                data = get_yt_dlp_comments(item, platform)
            else:
                data = get_meta_comments(item, token, platform)
            
            if data:
                all_data.extend(data)
            progress_bar.progress((i + 1) / len(input_list))

        if all_data:
            df = pd.DataFrame(all_data)
            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader("Sentiment Distribution")
                st.bar_chart(df['Category'].value_counts())
            with col2:
                st.subheader("Raw Data
