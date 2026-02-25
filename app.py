import streamlit as st
import pandas as pd
import yt_dlp
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from apify_client import ApifyClient

# Initialize Analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(text)['compound']
    if score >= 0.05: return "Positive"
    elif score <= -0.05: return "Negative"
    return "Neutral"

# YouTube Scraper (Existing Logic)
def get_yt_comments(url):
    ydl_opts = {'getcomments': True, 'skip_download': True, 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return [{"Author": c['author'], "Text": c['text'], "URL": url} for c in info.get('comments', [])]
    except: return None

# TikTok Scraper (Using Apify for 2026 Stability)
def get_tt_comments(url, api_token):
    client = ApifyClient(api_token)
    run_input = { "postURLs": [url], "commentsPerPost": 50 }
    run = client.actor("clockworks/tiktok-comments-scraper").call(run_input=run_input)
    
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append({
            "Author": item.get('authorMeta', {}).get('name'),
            "Text": item.get('text'),
            "URL": url
        })
    return results

# --- UI SECTION ---
st.title("📊 Multi-Platform Sentiment Analyzer")
platform = st.selectbox("Select Platform", ["YouTube", "TikTok"])

# Sidebar for API Key (required for TikTok)
api_token = ""
if platform == "TikTok":
    api_token = st.sidebar.text_input("Apify API Token", type="password")
    st.sidebar.info("Get a free token at apify.com")

urls_input = st.text_area(f"Paste {platform} URLs (one per line):")

if st.button("Start Analysis"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    all_data = []
    
    for url in urls:
        st.write(f"⏳ Scraping: {url}")
        data = get_yt_comments(url) if platform == "YouTube" else get_tt_comments(url, api_token)
        if data:
            all_data.extend(data)
            
    if all_data:
        df = pd.DataFrame(all_data)
        df['Category'] = df['Text'].apply(get_sentiment)
        
        # Deduplication to fix the "Kamchatka" issue (2277 vs 267)
        df = df.drop_duplicates(subset=['Text', 'Author'])
        
        st.subheader("Sentiment Results")
        st.bar_chart(df['Category'].value_counts())
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "results.csv")
