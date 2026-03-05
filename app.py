import streamlit as st
import pandas as pd
import yt_dlp
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize Analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(str(text))['compound']
    if score >= 0.05: return "Positive"
    elif score <= -0.05: return "Negative"
    return "Neutral"

def get_yt_comments(url):
    # 'getcomments': True pulls all metadata available
    ydl_opts = {
        'getcomments': True, 
        'skip_download': True, 
        'quiet': True, 
        'max_comments': 50,
        'extract_flat': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            
            # Add sentiment to each comment object
            for c in comments:
                c['Sentiment_Category'] = get_sentiment(c.get('text'))
            return comments
    except Exception as e:
        st.warning(f"Could not fetch comments for {url}: {e}")
        return None

# --- UI Setup ---
st.set_page_config(page_title="YouTube Multi-Column Scraper", layout="wide")
st.title("🎥 YouTube Comment Scraper")
st.markdown("Upload a CSV with YouTube URLs to scrape all comments while keeping your original data.")

# Sidebar for file upload
uploaded_file = st.sidebar.file_uploader("Step 1: Upload CSV/Excel", type=["csv", "xlsx"])

if uploaded_file:
    # Read original data
    if uploaded_file.name.endswith('.csv'):
        df_original = pd.read_csv(uploaded_file)
    else:
        df_original = pd.read_excel(uploaded_file)
    
    st.write("### 1. Preview Original Data", df_original.head(3))
    
    # Step 2: Select the URL column
    url_col = st.selectbox("Step 2: Select the column containing YouTube URLs", df_original.columns)

    if st.button("Step 3: Run Full Scrape"):
        all_results = []
        progress_bar = st.progress(0)
        
        # Iterate through your CSV rows
        for index, row in df_original.iterrows():
            video_url = str(row[url_col]).strip()
            
            # Fetch comments
            comments_data = get_yt_comments(video_url)
            
            if comments_data:
                for comment in comments_data:
                    # MERGE: Combine the original CSV row with the new comment data
                    full_row = row.to_dict()
                    full_row.update(comment) # This keeps ALL YouTube metadata columns
                    all_results.append(full_row)
            else:
                # Keep the row even if no comments found
                empty_row = row.to_dict()
                empty_row['Sentiment_Category'] = "No comments found or error"
                all_results.append(empty_row)
            
            progress_bar.progress((index + 1) / len(df_original))
        
        # Display and Download
        if all_results:
            df_final = pd.DataFrame(all_results)
            
            # Reorder to put Sentiment first for visibility
            if 'Sentiment_Category' in df_final.columns:
                cols = ['Sentiment_Category'] + [c for c in df_final.columns if c != 'Sentiment_Category']
                df_final = df_final[cols]

            st.success(f"Done! Scraped {len(df_final)} total rows.")
            st.dataframe(df_final)
            
            csv_data = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Full Result CSV", csv_data, "youtube_full_analysis.csv", "text/csv")
else:
    st.info("Please upload your CSV file in the sidebar to start.")
