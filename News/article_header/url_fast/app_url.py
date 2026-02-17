import streamlit as st
import pandas as pd
from newspaper import Article, Config
import nltk
import re

# Standard setup
@st.cache_resource
def setup_nltk():
    nltk.download('punkt_tab', quiet=True)
setup_nltk()

def get_smart_metadata(url, config):
    try:
        article = Article(url, config=config)
        article.download()
        article.parse()
        
        # 1. FIXED TITLE LOGIC: 
        # If the title is too short or generic, we try to grab it from keywords
        title = article.title
        if "TikTok" in title or len(title) < 5:
            # Fallback: Use the first few words of the actual text
            title = " ".join(article.text.split()[:10]) + "..." if article.text else title

        # 2. ENHANCED GENRE LOGIC:
        # We look at the URL first, then keywords as a backup
        path_parts = [p for p in url.split('/') if p]
        genre = "General"
        
        if len(path_parts) > 3: # Checking URL path first
            genre = path_parts[2].capitalize()
        elif article.keywords: # If URL fails, use the top AI keyword
            genre = article.keywords[0].capitalize()

        return {
            "Genre": genre,
            "Title": title,
            "URL": url
        }
    except:
        return None

# --- UI ---
st.title("📰 Smart News & Video Extractor")
urls_text = st.text_area("Paste URLs here (one per line):", height=200)

if st.button("Extract Smart Data"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    if urls:
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0'
        
        results = []
        for url in urls:
            res = get_smart_metadata(url, config)
            if res: results.append(res)
        
        st.dataframe(pd.DataFrame(results), use_container_width=True)
