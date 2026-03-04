import streamlit as st
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 1. Initialize Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    """Categorizes text into Positive, Negative, or Neutral using VADER."""
    if not text or pd.isna(text):
        return "Neutral"
    
    score = analyzer.polarity_scores(str(text))
    compound = score['compound']
    
    # Standard VADER thresholds
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# --- UI SECTION ---
st.set_page_config(page_title="Apify Data Processor", layout="wide")
st.title("📊 Apify Comment Cleaner & Categorizer")
st.write("Upload your CSV. This script will clean dates and add sentiment categories while keeping all data.")

# 2. File Uploader
uploaded_file = st.file_uploader("Upload your Apify CSV file", type="csv")

if uploaded_file is not None:
    # Read the full dataset
    df = pd.read_csv(uploaded_file)
    
    # --- ACTION 1: DATE CLEANING ---
    # Detect date column (Common Apify names: createTime, createdAt, timestamp)
    date_cols = ['createTime', 'createdAt', 'timestamp', 'date']
    target_date_col = next((c for c in date_cols if c in df.columns), None)
    
    if target_date_col:
        try:
            # Convert ISO 8601 string (2026-02-01T...) to only Date (2026-02-01)
            df[target_date_col] = pd.to_datetime(df[target_date_col]).dt.strftime('%Y-%m-%d')
            st.info(f"📅 Dates in '{target_date_col}' simplified to YYYY-MM-DD.")
        except Exception as e:
            st.warning(f"⚠️ Could not clean dates: {e}")

    # --- ACTION 2: SENTIMENT CATEGORIZATION ---
    # Detect text column (Common Apify names: text, content, comment)
    text_cols = ['text', 'content', 'comment', 'body']
    target_text_col = next((c for c in text_cols if c in df.columns), None)

    if target_text_col:
        with st.spinner('Categorizing comments...'):
            # Adds 'Category' column without removing any existing ones
            df['Category'] = df[target_text_col].apply(get_sentiment)
        st.success(f"✅ Sentiment analysis complete based on '{target_text_col}'.")
    else:
        st.error("❌ No text column found for sentiment analysis.")

    # --- UI DISPLAY & DOWNLOAD ---
    if target_text_col:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.subheader("Summary")
            st.bar_chart(df['Category'].value_counts())
            
        with col2:
            st.subheader("Full Data View")
            # Shows all columns from the original file + the new 'Category'
            st.dataframe(df, use_container_width=True)
            
        # Download Link for the full dataset
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Cleaned CSV",
            data=csv,
            file_name="cleaned_categorized_comments.csv",
            mime="text/csv"
        )
