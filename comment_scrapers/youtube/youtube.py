import streamlit as st
import pandas as pd
import yt_dlp
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize the analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text:
        return "Neutral"
    score = analyzer.polarity_scores(str(text))
    compound = score['compound']
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def format_timestamp(ts):
    """Converts Unix timestamp to readable date string"""
    if ts:
        try:
            return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return "Unknown"
    return "N/A"

def get_comments_bulk(url):
    ydl_opts = {
        'getcomments': True, 
        'skip_download': True, 
        'quiet': True, 
        'max_comments': 50,
        'no_warnings': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            
            results = []
            for c in comments:
                comment_text = c.get('text')
                results.append({
                    "Video_URL": url,
                    "Comment_ID": c.get('id'),
                    "Comment_Author": c.get('author'),
                    "Comment_Text": comment_text,
                    "Sentiment": get_sentiment(comment_text),
                    "Comment_Date": format_timestamp(c.get('timestamp'))
                })
            return results
    except Exception as e:
        return None

# --- UI SECTION ---
st.set_page_config(page_title="YouTube Bulk Scraper", layout="wide")
st.title("📊 Bulk YouTube Scraper & Sentiment Analyzer")

st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file:
    # Handle File Loading
    if uploaded_file.name.endswith('.csv'):
        df_input = pd.read_csv(uploaded_file)
    else:
        df_input = pd.read_excel(uploaded_file)

    st.write("### 1. Preview Uploaded Data")
    st.dataframe(df_input.head())

    # --- Column Selection ---
    cols = df_input.columns.tolist()
    url_col = st.selectbox("Select the column that contains YouTube URLs", options=cols)

    # --- Start Button ---
    if st.button("🚀 Start Bulk Scraping"):
        urls = df_input[url_col].dropna().unique().tolist()
        
        if not urls:
            st.warning("No URLs found in the selected column.")
        else:
            all_comments = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, url in enumerate(urls):
                status_text.text(f"Processing video {i+1} of {len(urls)}: {url}")
                data = get_comments_bulk(url)
                if data:
                    all_comments.extend(data)
                
                # Update progress
                progress_bar.progress((i + 1) / len(urls))

            status_text.text("✅ Scraping Complete!")

            # --- Display & Download Results ---
            if all_comments:
                df_final = pd.DataFrame(all_comments)
                st.write("### 2. Scraped Results")
                st.dataframe(df_final)

                # Export to CSV
                csv_data = df_final.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv_data,
                    file_name=f"youtube_sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.error("No comments could be retrieved. Check your URLs and try again.")
else:
    st.info("Please upload a file in the sidebar to get started.")
