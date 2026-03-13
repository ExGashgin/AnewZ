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
    # Manually defined list of active Nitter instances
    # If one fails, ntscraper will try another from this list
    working_instances = [
        'https://nitter.net', 
        'https://nitter.cz', 
        'https://nitter.privacydev.net',
        'https://nitter.no-logs.com'
    ]
    
    # Initialize scraper with the manual list
    scraper = Nitter(instances=working_instances)
    
    try:
        parts = url.strip("/").split('/')
        # Ensure we are getting the username correctly from the URL
        if "status" in parts:
            username = parts[parts.index("status") - 1]
        else:
            username = parts[-1]

        # Use the scraper
        tweets = scraper.get_tweets(username, mode='user', number=count)
        
        if not tweets or not tweets.get('tweets'):
            return None

        results = []
        for t in tweets['tweets']:
            results.append({
                "Date": t.get('date'),
                "Author": t.get('user', {}).get('name'),
                "Text": t.get('text'),
                "Sentiment": get_sentiment(t.get('text')),
                "Source_URL": url
            })
        return results
    except Exception as e:
        # This will now catch the specific error and tell you if it's an instance issue
        st.warning(f"Note: Could not reach X for {url}. X might be blocking the connection.")
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
