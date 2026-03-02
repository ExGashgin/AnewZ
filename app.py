import streamlit as st
import pandas as pd
import yt_dlp
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time

# --- 1. SETUP ---
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(str(text))['compound']
    if score >= 0.05: return "Positive"
    elif score <= -0.05: return "Negative"
    return "Neutral"

# --- 2. TIKTOK SCRAPER FUNCTION ---
def get_tiktok_comments(url):
    if not str(url).strip().startswith("http"):
        st.error(f"❌ '{url[:30]}...' is not a link.")
        return None

    ydl_opts = {
        'getcomments': True, 
        'skip_download': True, 
        'quiet': True,
        'extract_flat': True,
        # Force yt-dlp to look like a specific browser version
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'referer': 'https://www.tiktok.com/',
        # Use a configuration that helps bypass JS challenges
        'extractor_args': {'tiktok': {'impersonate': 'chrome'}}, 
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We use extract_info but specifically target comment metadata
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            
            if not comments:
                return "Empty" 
                
            return [{
                "Author": c.get('author'), 
                "Text": c.get('text'), 
                "Category": get_sentiment(c.get('text')), 
                "Video_URL": url
            } for c in comments]
    except Exception as e:
        # If blocked, we show a helpful error instead of just "No Data"
        st.warning(f"⚠️ TikTok Blocked the Scraper. This is common on cloud hosts.")
        return None

# --- 3. UI SECTION ---
st.set_page_config(page_title="TikTok Sentiment Analyzer", layout="wide")
st.title("🎵 TikTok Comment Scraper & Sentiment")

st.sidebar.header("Data Input")
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel of TikTok URLs", type=["csv", "xlsx"])
urls_input = st.text_area("OR Paste TikTok URLs (one per line):", placeholder="https://www.tiktok.com/@user/video/...")

if st.button("Start Scraping TikTok"):
    urls = []
    # Determine source of URLs
    if uploaded_file:
        df_input = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        urls = df_input.iloc[:, 0].dropna().tolist()
    else:
        urls = [u.strip() for u in urls_input.split('\n') if u.strip()]

    if not urls:
        st.warning("Please provide at least one TikTok URL.")
    else:
        all_data = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, url in enumerate(urls):
            status_text.text(f"Processing video {i+1} of {len(urls)}...")
            data = get_tiktok_comments(url)
            
            if isinstance(data, list):
                all_data.extend(data)
            elif data == "Empty":
                st.info(f"ℹ️ No comments found on video: {url}")
            
            # Update progress
            progress_bar.progress((i + 1) / len(urls))
            # Short pause to reduce risk of IP blocking
            time.sleep(1) 

        # --- 4. RESULTS DISPLAY ---
        if all_data:
            df = pd.DataFrame(all_data)
            
            st.divider()
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Sentiment Breakdown")
                st.bar_chart(df['Category'].value_counts())
                
            with col2:
                st.subheader("Comment Data")
                st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download TikTok Results", csv, "tiktok_analysis.csv", "text/csv")
        else:
            st.error("No data could be retrieved. This is likely due to TikTok's anti-scraping protections or invalid URLs.")
