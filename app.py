import streamlit as st
import pandas as pd
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

def get_x_data(url, count=20):
    """
    Fetches comments/replies related to a specific tweet or user.
    """
    scraper = Nitter()
    try:
        # Clean the URL and extract the username
        # Expected: https://x.com/UserName/status/12345
        parts = url.strip("/").split('/')
        username = parts[3] if len(parts) > 3 else None
        
        if not username:
            return None

        # Scraping based on the user's recent activity related to the post
        tweets = scraper.get_tweets(username, mode='user', number=count)
        
        results = []
        for t in tweets['tweets']:
            results.append({
                "Date": t.get('date'),
                "Author": t.get('user', {}).get('name'),
                "Handle": t.get('user', {}).get('username'),
                "Text": t.get('text'),
                "Sentiment": get_sentiment(t.get('text')),
                "Stats_Likes": t.get('stats', {}).get('likes'),
                "Stats_Retweets": t.get('stats', {}).get('retweets'),
                "Source_URL": url
            })
        return results
    except Exception as e:
        st.error(f"Error scraping {url}: {e}")
        return None

# --- UI SECTION ---
st.set_page_config(page_title="X (Twitter) Scraper", layout="wide")
st.title("🐦 X Reply & Sentiment Scraper")

st.sidebar.header("Data Upload")
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel with X URLs", type=["csv", "xlsx"])

if uploaded_file:
    # Load File
    df_input = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    
    st.write("### 1. Uploaded Links Preview")
    st.dataframe(df_input.head())
    
    # Column Selection
    url_col = st.selectbox("Select the column containing X URLs", options=df_input.columns)
    num_comments = st.sidebar.slider("Replies per URL", 5, 100, 20)

    if st.button("🚀 Start Scraping X"):
        urls = df_input[url_col].dropna().unique().tolist()
        all_results = []
        
        progress_bar = st.progress(0)
        status = st.empty()

        for i, url in enumerate(urls):
            status.text(f"Scraping URL {i+1} of {len(urls)}...")
            data = get_x_data(url, count=num_comments)
            if data:
                all_results.extend(data)
            progress_bar.progress((i + 1) / len(urls))

        status.text("✅ Finished!")

        if all_results:
            df_final = pd.DataFrame(all_results)
            st.write("### 2. Scraped Data")
            st.dataframe(df_final)
            
            # Download
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "x_scraped_data.csv", "text/csv")
        else:
            st.warning("No data found. Ensure the URLs are public and the Nitter instances are active.")
