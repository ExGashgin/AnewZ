import streamlit as st
import pandas as pd
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 1. Setup Logic
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(str(text))['compound']
    if score >= 0.05: return "Positive"
    elif score <= -0.05: return "Negative"
    return "Neutral"

# 2. UI - Always run this first to avoid blank screens
st.set_page_config(page_title="TikTok Scraper", layout="centered")
st.title("🎵 TikTok Comment Analyzer")

# 3. Sidebar
st.sidebar.header("Setup")
api_key = st.sidebar.text_input("API Key", type="password")
urls_input = st.text_area("Paste TikTok URLs:")

# 4. Scraper Logic with Error Catching
if st.button("Start Analysis"):
    if not api_key:
        st.error("Please enter an API Key first.")
    else:
        try:
            # Simple API request example
            st.info("Searching for comments...")
            # Your API logic here...
            st.success("Analysis complete!")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
