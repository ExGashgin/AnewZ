import streamlit as st
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 1. Initialize VADER analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    """Categorizes text into Positive, Negative, or Neutral based on compound score."""
    if not text or pd.isna(text):
        return "Neutral"
    
    # Calculate sentiment compound score (-1 to +1)
    score = analyzer.polarity_scores(str(text))['compound']
    
    # Standard classification thresholds
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Data Cleaner", layout="wide")
st.title("📂 Apify Data: Date Cleaner & Sentiment Analyzer")
st.markdown("This app cleans **dates**, categorizes **sentiment**, and keeps **all original columns**.")

uploaded_file = st.file_uploader("Drop your Apify CSV here", type="csv")

if uploaded_file is not None:
    # Read the full dataset
    df = pd.read_csv(uploaded_file)
    
    # --- STEP 1: SMART DATE CLEANING ---
    # Common Apify headers: 'createTime', 'createdAt', 'timestamp'
    date_cols = ['createTime', 'createdAt', 'timestamp', 'date', 'updatedAt']
    target_date = next((c for c in date_cols if c in df.columns), None)
    
    if target_date:
        # Convert "2026-02-01T16:08:43.000Z" -> "2026-02-01"
        df[target_date] = pd.to_datetime(df[target_date]).dt.strftime('%Y-%m-%d')
        st.success(f"📅 Dates in column **'{target_date}'** simplified to YYYY-MM-DD.")

    # --- STEP 2: SENTIMENT CATEGORIZATION ---
    # Common text headers: 'text', 'content', 'comment'
    text_cols = ['text', 'content', 'comment', 'body', 'description']
    target_text = next((c for c in text_cols if c in df.columns), None)

    if target_text:
        with st.spinner('Analyzing sentiments...'):
            # Add Category column at the end
            df['Category'] = df[target_text].apply(get_sentiment)
        st.success(f"✅ Categorized sentiment based on column **'{target_text}'**.")
    else:
        st.error("❌ Could not find a text/comment column for analysis.")

    # --- STEP 3: PREVIEW & EXPORT ---
    st.divider()
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Distribution")
        st.bar_chart(df['Category'].value_counts())
        
    with col2:
        st.subheader("Data Preview (Full)")
        st.dataframe(df, use_container_width=True)
        
    # Download processed file with original name prefix
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Cleaned & Categorized CSV",
        data=csv_data,
        file_name="processed_apify_data.csv",
        mime="text/csv"
    )
