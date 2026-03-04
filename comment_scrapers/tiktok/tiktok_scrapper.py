import streamlit as st
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 1. Initialize Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    """Categorizes text into Positive, Negative, or Neutral."""
    if not text or pd.isna(text):
        return "Neutral"
    
    score = analyzer.polarity_scores(str(text))
    compound = score['compound']
    
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# --- UI SECTION ---
st.set_page_config(page_title="Apify Data Processor", layout="wide")
st.title("📊 Complete Data Categorizer")
st.write("Upload your Apify CSV. This will add a 'Category' column while keeping all your original data.")

uploaded_file = st.file_uploader("Choose your Apify CSV file", type="csv")

if uploaded_file is not None:
    # Read the full dataframe
    df = pd.read_csv(uploaded_file)
    
    # Identify the comment column
    possible_cols = ['text', 'content', 'comment', 'body', 'description']
    target_col = next((c for c in possible_cols if c in df.columns), None)

    if target_col:
        with st.spinner('Processing all columns...'):
            # Create the new column without dropping others
            df['Category'] = df[target_col].apply(get_sentiment)
        
        st.success(f"Analysis complete! Added 'Category' based on the '{target_col}' column.")
        
        # --- Visualization ---
        col1, col2 = st.columns([1, 3])
        with col1:
            st.subheader("Sentiment Distribution")
            st.bar_chart(df['Category'].value_counts())
            
        with col2:
            st.subheader("Full Dataset Preview")
            # Display the ENTIRE dataframe (all columns)
            st.dataframe(df, use_container_width=True)
            
        # --- Download All Data ---
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Categorized CSV",
            data=csv,
            file_name="apify_full_categorized.csv",
            mime="text/csv"
        )
    else:
        st.error(f"Could not find a text column. Your CSV columns are: {list(df.columns)}")
