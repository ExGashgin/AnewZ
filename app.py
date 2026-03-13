import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ntscraper import Nitter

# Initialize Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(str(text))
    if score['compound'] >= 0.05: return "Positive"
    elif score['compound'] <= -0.05: return "Negative"
    return "Neutral"

def get_x_data_with_retry(url, count=20):
    """
    Attempts to scrape X data using randomized instances and retries.
    """
    # A list of potentially active Nitter instances
    instances = [
        'https://nitter.net', 'https://nitter.cz', 
        'https://nitter.privacydev.net', 'https://nitter.no-logs.com',
        'https://nitter.projectsegfau.lt', 'https://nitter.rawbit.ninja'
    ]
    
    # Try up to 3 different instances for each URL
    for attempt in range(3):
        selected_instance = random.choice(instances)
        scraper = Nitter(instances=[selected_instance])
        
        try:
            # 1. Randomized delay (Anti-bot measure)
            time.sleep(random.uniform(2, 4))
            
            # 2. Extract Username from URL
            parts = url.strip("/").split('/')
            if "status" in parts:
                username = parts[parts.index("status") - 1]
            else:
                username = parts[-1]
            
            # 3. Scrape
            tweets = scraper.get_tweets(username, mode='user', number=count)
            
            if tweets and tweets.get('tweets'):
                results = []
                for t in tweets['tweets']:
                    results.append({
                        "Date": t.get('date'),
                        "Author": t.get('user', {}).get('name'),
                        "Handle": t.get('user', {}).get('username'),
                        "Text": t.get('text'),
                        "Sentiment": get_sentiment(t.get('text')),
                        "Source_URL": url
                    })
                return results
        except Exception:
            # If this instance fails, wait 2 seconds and try the next one
            time.sleep(2)
            continue
            
    return None

# --- UI SECTION ---
st.set_page_config(page_title="X Marketing Scraper", layout="wide")
st.title("🐦 X (Twitter) Bulk Scraper - Strategy: Retry & Rotate")

st.sidebar.header("Data Upload")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file:
    # --- FIXED SYNTAX ERROR HERE ---
    if uploaded_file.name.endswith('.csv'):
        df_input = pd.read_csv(uploaded_file)
    else:
        df_input = pd.read_excel(uploaded_file)
    
    st.write("### 1. Data Preview", df_input.head())
    
    url_col = st.selectbox("Select the column with X URLs", options=df_input.columns)
    num_replies = st.sidebar.slider("Max items per URL", 5, 50, 15)

    if st.button("🚀 Start Robust Scraping"):
        urls = df_input[url_col].dropna().unique().tolist()
        all_results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, url in enumerate(urls):
            status_text.warning(f"Processing {i+1}/{len(urls)}: {url}")
            
            data = get_x_data_with_retry(url, count=num_replies)
            
            if data:
                all_results.extend(data)
            else:
                st.error(f"Skipped: {url} (All instances failed/Rate limited)")
            
            # Update Progress
            progress_bar.progress((i + 1) / len(urls))

        status_text.success("✅ Process Finished!")

        if all_results:
            df_final = pd.DataFrame(all_results)
            st.write("### 2. Scraped Results")
            st.dataframe(df_final)
            
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Scraped Data", csv, "x_marketing_results.csv", "text/csv")
else:
    st.info("Upload a file to begin.")
