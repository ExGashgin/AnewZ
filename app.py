import streamlit as st
import pandas as pd
import yt_dlp
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize the analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    """Categorizes text into Good, Bad, or Neutral using VADER."""
    if not text:
        return "Neutral"
    
    # Calculate sentiment scores
    score = analyzer.polarity_scores(text)
    compound = score['compound']
    
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def get_comments_bulk(url):
    ydl_opts = {'getcomments': True, 'skip_download': True, 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            
            results = []
            for c in comments:
                comment_text = c.get('text')
                results.append({
                    "Author": c.get('author'),
                    "Text": comment_text,
                    "Category": get_sentiment(comment_text), # New Column
                    "URL": url
                })
            return results
    except Exception:
        return None

# --- UI SECTION ---
st.title("📊 Bulk Scraper with Sentiment Analysis")

urls_input = st.text_area("Paste YouTube URLs:")

if st.button("Scrape & Categorize"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    all_data = []
    
    for url in urls:
        st.write(f"Processing: {url}")
        data = get_comments_bulk(url)
        if data:
            all_data.extend(data)
            
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Display a summary table
        st.subheader("Sentiment Summary")
        summary = df['Category'].value_counts()
        st.bar_chart(summary)
        
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "categorized_comments.csv")
