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

# --- 2. API SCRAPERS ---

def get_yt_comments(url):
    ydl_opts = {'getcomments': True, 'skip_download': True, 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return [{"Author": c.get('author'), "Text": c.get('text'), 
                     "Category": get_sentiment(c.get('text')), "Source": url} 
                    for c in info.get('comments', [])]
    except Exception as e:
        st.warning(f"YouTube Error for {url}: {str(e)}")
        return None

def get_fb_comments(post_id, token):
    url = f"https://graph.facebook.com/v22.0/{post_id}/comments"
    params = {'access_token': token, 'fields': 'message,from'}
    response = requests.get(url, params=params).json()
    
    if "error" in response:
        st.error(f"FB Error: {response['error'].get('message')}")
        return None
        
    return [{"Author": c.get('from', {}).get('name'), "Text": c.get('message'),
             "Category": get_sentiment(c.get('message')), "Source": post_id} 
            for c in response.get('data', [])]

def get_ig_comments(media_id, token):
    # Instagram uses the same comments endpoint but fields differ slightly ('text' vs 'message')
    url = f"https://graph.facebook.com/v22.0/{media_id}/comments"
    params = {'access_token': token, 'fields': 'text,username'}
    response = requests.get(url, params=params).json()
    
    if "error" in response:
        st.error(f"IG Error for {media_id}: {response['error'].get('message')}")
        return None
        
    return [{"Author": c.get('username'), "Text": c.get('text'),
             "Category": get_sentiment(c.get('text')), "Source": media_id} 
            for c in response.get('data', [])]

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Multi-Platform Sentiment Scraper", layout="wide")
st.title("📊 Social Media Sentiment Scraper")
st.markdown("Download comments and analyze sentiment from **YouTube**, **Facebook**, or **Instagram**.")

# Sidebar Settings
st.sidebar.header("Configuration")
platform = st.sidebar.selectbox("Target Platform", ["YouTube", "Facebook", "Instagram"])
token = ""
if platform in ["Facebook", "Instagram"]:
    token = st.sidebar.text_input(f"Enter {platform} Page Access Token", type="password")
    st.sidebar.info("💡 Ensure your token has 'instagram_basic' and 'pages_read_engagement' permissions.")

uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel of IDs/URLs", type=["csv", "xlsx"])

# Main Input Area
input_label = "URLs" if platform == "YouTube" else "Post/Media IDs"
raw_input = st.text_area(f"Paste {platform} {input_label} (one per line):", height=150)

# Process Input
items = []
if uploaded_file:
    df_in = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    items = df_in.iloc[:, 0].dropna().tolist()
elif raw_input:
    items = [i.strip() for i in raw_input.split('\n') if i.strip()]

# --- 4. EXECUTION ---
if st.button(f"Analyze {platform}"):
    if not items:
        st.error("Please provide IDs or URLs to analyze.")
    elif platform in ["Facebook", "Instagram"] and not token:
        st.error("Access Token is required for Meta platforms.")
    else:
        all_data = []
        progress_bar = st.progress(0)
        
        for idx, item in enumerate(items):
            if platform == "YouTube":
                data = get_yt_comments(item)
            elif platform == "Facebook":
                data = get_fb_comments(item, token)
            elif platform == "Instagram":
                data = get_ig_comments(item, token)
            
            if data:
                all_data.extend(data)
            progress_bar.progress((idx + 1) / len(items))
        
        if all_data:
            df = pd.DataFrame(all_data)
            
            # Dashboard
            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader("Sentiment Distribution")
                st.bar_chart(df['Category'].value_counts())
            
            with col2:
                st.subheader("Raw Data")
                st.dataframe(df, use_container_width=True)
            
            # Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Results (CSV)", csv, f"{platform.lower()}_sentiment.csv", "text/csv")
        else:
            st.error("No comments found. Check your IDs or Token permissions.")
