import streamlit as st
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text or pd.isna(text): return "Neutral"
    score = analyzer.polarity_scores(str(text))
    return "Positive" if score['compound'] >= 0.05 else "Negative" if score['compound'] <= -0.05 else "Neutral"

st.set_page_config(page_title="Apify Cleaner", layout="wide")
st.title("📊 Data Categorizer & Date Cleaner")

uploaded_file = st.file_uploader("Upload Apify CSV", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # --- 1. CLEAN DATE FORMAT ---
    date_cols = ['createTime', 'createdAt', 'timestamp', 'date']
    target_date_col = next((c for c in date_cols if c in df.columns), None)
    
    if target_date_col:
        try:
            # Convert ISO to simple Date
            df[target_date_col] = pd.to_datetime(df[target_date_col]).dt.strftime('%Y-%m-%d')
            st.info(f"📅 Cleaned dates in column: **{target_date_col}**")
        except:
            st.warning("⚠️ Found a date column but format was unexpected.")

    # --- 2. CATEGORIZE SENTIMENT ---
    text_cols = ['text', 'content', 'comment', 'body']
    target_text_col = next((c for c in text_cols if c in df.columns), None)

    if target_text_col:
        with st.spinner('Processing...'):
            df['Category'] = df[target_text_col].apply(get_sentiment)
        
        # UI Display
        st.subheader("Final Result (All Columns Preserved)")
        st.dataframe(df, use_container_width=True)
        
        # Download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Cleaned CSV", csv, "cleaned_data.csv", "text/csv")
    else:
        st.error("Could not find a text column for sentiment analysis.")
