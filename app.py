import streamlit as st
import pandas as pd
import yt_dlp
import time
import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from apify_client import ApifyClient

# --- SETUP ---
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral 😐"
    score = analyzer.polarity_scores(str(text))['compound']
    if score >= 0.05: return "Good 😊"
    elif score <= -0.05: return "Bad 😡"
    return "Neutral 😐"

# --- SCRAPER ENGINES ---
def scrape_youtube(url):
    ydl_opts = {'getcomments': True, 'skip_download': True, 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        comments = info.get('comments', [])
        return [{"Author": c.get('author'), "Text": c.get('text'), "URL": url} for c in comments]

def scrape_meta(url, api_token, platform):
    client = ApifyClient(api_token)
    # Choose correct 'Actor' based on platform
    actor_id = "apify/facebook-comments-scraper" if platform == "Facebook" else "apify/instagram-comment-scraper"
    
    run_input = { "startUrls": [{ "url": url }], "resultsLimit": 100 }
    run = client.actor(actor_id).call(run_input=run_input)
    
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append({
            "Author": item.get('author', {}).get('name') or item.get('ownerUsername'),
            "Text": item.get('commentText') or item.get('text'),
            "URL": url
        })
    return results

# --- STREAMLIT UI ---
st.set_page_config(page_title="Multi-Platform Scraper", layout="wide")
st.title("📊 Social Media Sentiment Dashboard")

# Sidebar for Configuration
st.sidebar.header("Configuration")
platform = st.sidebar.selectbox("Target Platform", ["YouTube", "Facebook", "Instagram"])
apify_token = ""
if platform in ["Facebook", "Instagram"]:
    apify_token = st.sidebar.text_input("Apify API Token", type="password", help="Get it from apify.com")

urls_input = st.text_area(f"Paste {platform} URLs (one per line):", height=150)

if st.button(f"Scrape {platform}"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    all_data = []
    
    progress_bar = st.progress(0)
    for i, url in enumerate(urls):
        st.write(f"🔍 Analyzing: {url}")
        try:
            if platform == "YouTube":
                data = scrape_youtube(url)
            else:
                if not apify_token:
                    st.error("Please enter an Apify Token for Meta platforms.")
                    st.stop()
                data = scrape_meta(url, apify_token, platform)
            
            if data:
                all_data.extend(data)
            
            # Anti-Ban Delay for YouTube
            if platform == "YouTube":
                time.sleep(random.randint(2, 5))
                
        except Exception as e:
            st.warning(f"Skipped {url}: {str(e)}")
        
        progress_bar.progress((i + 1) / len(urls))

    if all_data:
        df = pd.DataFrame(all_data)
        
        # --- CRITICAL: FIX THE 2,277 VS 267 PROBLEM ---
        # Deduplicate by URL and Text
        initial_count = len(df)
        df = df.drop_duplicates(subset=['Text', 'URL'])
        final_count = len(df)
        
        if initial_count > final_count:
            st.info(f"Cleaned up {initial_count - final_count} duplicate comments.")

        # Apply Sentiment
        df['Category'] = df['Text'].apply(get_sentiment)

        # Dashboard
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Sentiment Summary")
            st.bar_chart(df['Category'].value_counts())
        with col2:
            st.subheader("Data Preview")
            st.dataframe(df, use_container_width=True)

        st.download_button("📥 Download Clean Report", df.to_csv(index=False), "social_sentiment_report.csv")
