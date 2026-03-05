import streamlit as st
import pandas as pd
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

# Scraper Function for Meta (FB/IG)
def get_meta_comments(obj_id, token, platform):
    # Endpoint for comments
    url = f"https://graph.facebook.com/v22.0/{obj_id}/comments"
    
    # Instagram uses 'text', Facebook uses 'message'
    fields = 'text,username,timestamp,like_count' if platform == "Instagram" else 'message,from,created_time,like_count'
    
    try:
        r = requests.get(url, params={'access_token': token, 'fields': fields}, timeout=15).json()
        
        if "error" in r:
            st.error(f"Meta API Error for ID {obj_id}: {r['error'].get('message')}")
            return None
            
        data = r.get('data', [])
        for c in data:
            # Extract content based on platform to run sentiment
            msg = c.get('text') if platform == "Instagram" else c.get('message')
            c['Sentiment_Category'] = get_sentiment(msg)
            
            # Flatten the 'from' dictionary in Facebook to make it CSV friendly
            if platform == "Facebook" and 'from' in c:
                c['Author_Name'] = c['from'].get('name')
                c['Author_ID'] = c['from'].get('id')
        return data
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# --- UI SECTION ---
st.set_page_config(page_title="Meta Sentiment Scraper", layout="wide")
st.title("📊 Meta Sentiment Scraper (FB & IG)")
st.markdown("Scrape comments from Facebook or Instagram while preserving all original CSV columns.")

# Sidebar Settings
platform = st.sidebar.selectbox("Select Platform", ["Facebook", "Instagram"])
token = st.sidebar.text_input(f"Enter {platform} Page Access Token", type="password")

# File Uploader
uploaded_file = st.sidebar.file_uploader("Upload your CSV/Excel list", type=["csv", "xlsx"])

if uploaded_file:
    # Read the original file
    if uploaded_file.name.endswith('.csv'):
        df_original = pd.read_csv(uploaded_file)
    else:
        df_original = pd.read_excel(uploaded_file)
    
    st.write("### Original Data Preview", df_original.head(3))
    
    # User selects column with Post IDs
    id_column = st.selectbox("Select the column containing Post IDs or Media IDs", df_original.columns)

    if st.button(f"Analyze {platform}"):
        if not token:
            st.warning("Please enter a valid Access Token in the sidebar.")
        else:
            all_rows = []
            progress_bar = st.progress(0)
            
            for index, row in df_original.iterrows():
                item_id = str(row[id_column]).strip()
                
                # Fetch comments from Meta
                fetched_data = get_meta_comments(item_id, token, platform)
