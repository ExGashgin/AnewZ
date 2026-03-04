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
st.title("📊 Apify Comment Categorizer")
st.write("Upload your CSV file from Apify to automatically categorize sentiments.")

# 2. File Uploader (Replaces the broken pd.read_csv line)
uploaded_file = st.file_uploader("Choose your Apify CSV file", type="csv")

if uploaded_file is not None:
    # Read the uploaded file directly
    df = pd.read_csv(uploaded_file)
    
    # 3. Automatic Column Detection
    # Apify usually uses 'text' or 'content' for comments
    possible_cols = ['text', 'content', 'comment', 'body']
    target_col = next((c for c in possible_cols if c in df.columns), None)

    if target_col:
        with st.spinner('Categorizing comments...'):
            # Apply sentiment analysis
            df['Category'] = df[target_col].apply(get_sentiment)
        
        st.success(f"Successfully categorized using column: **{target_col}**")
        
        # 4. Display Summary & Data
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Sentiment Summary")
            st.bar_chart(df['Category'].value_counts())
            
        with col2:
            st.subheader("Categorized Data")
            st.dataframe(df[[target_col, 'Category']], use_container_width=True)
            
        # 5. Download Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Categorized CSV",
            csv,
            "categorized_comments.csv",
            "text/csv"
        )
    else:
        st.error(f"Could not find a comment column. Columns found: {list(df.columns)}")
