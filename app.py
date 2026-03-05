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

# Scraper Functions
def get_yt_comments(url):
    ydl_opts = {'getcomments': True, 'skip_download': True, 'quiet': True, 'max_comments': 40}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Return all metadata from YouTube
            comments = info.get('comments', [])
            for c in comments:
                c['Sentiment_Category'] = get_sentiment(c.get('text'))
            return comments
    except: return None

def get_meta_comments(obj_id, token, platform):
    url = f"https://graph.facebook.com/v22.0/{obj_id}/comments"
    # Added more fields to Meta request to be safe
    fields = 'text,username,timestamp,like_count' if platform == "Instagram" else 'message,from,created_time,like_count'
    try:
        r = requests.get(url, params={'access_token': token, 'fields': fields}, timeout=10).json()
        if "error" in r: return None
        data = r.get('data', [])
        for c in data:
            msg = c.get('text') if platform == "Instagram" else c.get('message')
            c['Sentiment_Category'] = get_sentiment(msg)
        return data
    except: return None

# UI
st.set_page_config(page_title="Social Scraper", layout="wide")
st.title("📊 Social Sentiment Scraper (Keep Original Columns)")

platform = st.sidebar.selectbox("Platform", ["YouTube", "Facebook", "Instagram"])
token = st.sidebar.text_input("Token", type="password") if platform != "YouTube" else ""

# File Uploader
uploaded_file = st.sidebar.file_uploader("Upload your CSV", type=["csv", "xlsx"])

if uploaded_file:
    # Read the original CSV/Excel
    if uploaded_file.name.endswith('.csv'):
        df_original = pd.read_csv(uploaded_file)
    else:
        df_original = pd.read_excel(uploaded_file)
    
    st.write("### Original Data Preview", df_original.head(3))
    
    # User selects which column contains the ID or URL
    id_column = st.selectbox("Select the column containing IDs or URLs", df_original.columns)

    if st.button("Run Analysis"):
        all_rows = []
        progress_bar = st.progress(0)
        
        for index, row in df_original.iterrows():
            item = str(row[id_column]).strip()
            
            # Fetch comments based on platform
            if platform == "YouTube": 
                fetched_data = get_yt_comments(item)
            else: 
                fetched_data = get_meta_comments(item, token, platform)
            
            if fetched_data:
                for comment in fetched_data:
                    # Create a copy of the original row data
                    combined_row = row.to_dict()
                    # Update it with the new comment data and sentiment
                    combined_row.update(comment)
                    all_rows.append(combined_row)
            else:
                # If no comments found, still keep the original row but leave sentiment empty
                combined_row = row.to_dict()
                combined_row['Sentiment_Category'] = "No Comments Found"
                all_rows.append(combined_row)
            
            progress_bar.progress((index + 1) / len(df_original))
        
        if all_rows:
            df_final = pd.DataFrame(all_rows)
            
            # Reorder: Put original columns first, then new ones
            st.success(f"Analysis complete! Found {len(df_final)} total comment rows.")
            st.dataframe(df_final)
            
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Combined Results", csv, "combined_sentiment_data.csv", "text/csv")
else:
    st.info("Please upload a CSV file to begin.")
