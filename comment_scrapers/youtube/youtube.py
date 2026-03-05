import streamlit as st
import pandas as pd
import yt_dlp
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

def get_comments_bulk(url):
    # Added 'max_comments' to prevent hanging on huge videos
    # Added 'ignoreerrors' to keep the script running if one URL fails
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
                    "Comment_Author": c.get('author'),
                    "Comment_Text": comment_text,
                    "Sentiment_Category": get_sentiment(comment_text),
                    "Comment_Date": c.get('timestamp')
                })
            return results
    except Exception as e:
        # Logging the error helps diagnose "no results" issues
        st.error(f"Error scraping {url}: {e}")
        return None

# --- UI SECTION ---
st.set_page_config(page_title="YouTube Bulk Scraper", layout="wide")
st.title("📊 Bulk YouTube Scraper (File Upload)")

# Sidebar for configuration
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file:
    # 1. Load the data
    if uploaded_file.name.endswith('.csv'):
        df_input = pd.read_csv(uploaded_file)
    else:
        df_input = pd.read_excel(uploaded_file)

    st.write("### Data Preview", df_input.head(3))
    
    # 2. Select the URL column
    url_column = st.selectbox("Select the column that contains YouTube URLs", df_input.columns)

    if st.button("Run Bulk Scrape & Analyze"):
        final_data = []
        progress_bar = st.progress(0)
        
        # 3. Iterate through original rows
        for index, row in df_input.iterrows():
            url = str(row[url_column]).strip()
            
            if url and "youtube.com" in url or "youtu.be" in url:
                st.write(f"Scraping: {url}")
                comments = get_comments_bulk(url)
                
                if comments:
                    for c in comments:
                        # MERGE: Combine original CSV row with new comment data
                        new_row = row.to_dict()
                        new_row.update(c) 
                        final_data.append(new_row)
                else:
                    # Keep row even if no comments found
                    no_data_row = row.to_dict()
                    no_data_row["Sentiment_Category"] = "No Comments Found"
                    final_data.append(no_data_row)
            
            progress_bar.progress((index + 1) / len(df_input))

        # 4. Results
        if final_data:
            df_final = pd.DataFrame(final_data)
            
            st.subheader("Analysis Results")
            st.bar_chart(df_final['Sentiment_Category'].value_counts())
            st.dataframe(df_final)
            
            # Download button
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("Download Full Results (CSV)", csv, "youtube_analysis.csv", "text/csv")
else:
    st.info("Please upload a CSV or Excel file to get started.")
