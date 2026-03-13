import streamlit as st
import pandas as pd
import time
import random
from ntscraper import Nitter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(str(text))
    return "Positive" if score['compound'] >= 0.05 else "Negative" if score['compound'] <= -0.05 else "Neutral"

def get_x_robust(url, count=10):
    # Added even more fresh instances for 2026
    instances = [
        'https://nitter.net', 'https://nitter.cz', 'https://nitter.it',
        'https://nitter.privacy.com.de', 'https://nitter.seller.hu'
    ]
    
    # Try Search Mode first - it is often more stable than 'User' mode
    scraper = Nitter(instances=instances)
    try:
        # Extract the unique Tweet ID from the URL
        tweet_id = url.split('/')[-1].split('?')[0]
        
        # We search for the Tweet ID specifically
        tweets = scraper.get_tweets(tweet_id, mode='term', number=count)
        
        if not tweets or not tweets.get('tweets'):
            return None

        return [{
            "Date": t.get('date'),
            "Text": t.get('text'),
            "Sentiment": get_sentiment(t.get('text')),
            "Source_URL": url
        } for t in tweets['tweets']]
    except:
        return None

# --- STREAMLIT UI ---
st.set_page_config(page_title="X Marketing Final", layout="wide")
st.title("🐦 X Marketing Sentiment Final")

uploaded_file = st.sidebar.file_uploader("Upload X Links", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    url_col = st.selectbox("Select URL Column", df.columns)
    
    if st.button("🚀 Final Attempt: Scrape via Search"):
        results = []
        urls = df[url_col].dropna().unique().tolist()
        progress = st.progress(0)
        
        for i, url in enumerate(urls):
            st.write(f"🔍 Searching data for link {i+1}...")
            data = get_x_robust(url)
            if data:
                results.extend(data)
                st.success(f"✅ Found {len(data)} items for {url[:30]}...")
            else:
                st.error(f"❌ X is still blocking: {url[:30]}...")
            
            # Longer cooldown to prevent total IP ban
            time.sleep(random.uniform(5, 8)) 
            progress.progress((i + 1) / len(urls))

        if results:
            final_df = pd.DataFrame(results)
            st.dataframe(final_df)
            st.download_button("📥 Download Final Results", final_df.to_csv(index=False), "final_x_data.csv")
