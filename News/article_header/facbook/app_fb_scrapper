import streamlit as st
import pandas as pd
from newspaper import Article, Config
from concurrent.futures import ThreadPoolExecutor
import nltk

st.set_page_config(page_title="Ultra-Fast Scraper", page_icon="🚀", layout="wide")

@st.cache_resource
def setup_nltk():
    nltk.download('punkt_tab', quiet=True)

setup_nltk()

# --- OPTIMIZED FAST FUNCTION ---
def ultra_fast_scrape(full_url, config):
    try:
        # We only download and parse; we SKIP nlp() to save 80% of time
        article = Article(full_url, config=config)
        article.download()
        article.parse()
        
        return {
            "Title": article.title,
            "Date": article.publish_date,
            "URL": full_url
        }
    except:
        return None

# --- UI ---
st.title("🚀 Ultra-Fast Bulk Scraper")
base_url = st.text_input("Base Domain:", value="https://anewz.tv").strip().rstrip('/')
paths_text = st.text_area("Paste 1,000+ Paths:", height=200)

# ADVANCED SPEED SETTINGS
t_col1, t_col2 = st.columns(2)
with t_col1:
    threads = st.select_slider("Speed (Threads)", options=[10, 20, 50, 100], value=50)
with t_col2:
    skip_nlp = st.checkbox("Skip NLP (Summary/Keywords) for 5x Speed", value=True)

if st.button("⚡ Start Ultra-Fast Extraction"):
    paths = [p.strip() for p in paths_text.split('\n') if p.strip()]
    if paths:
        # CONFIGURATION FOR SPEED
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0'
        config.fetch_images = False  # DO NOT download images (Huge speed boost!)
        config.memoize_articles = False
        config.request_timeout = 5   # Don't wait more than 5 seconds per link
        
        urls = [f"{base_url}{'/' if not p.startswith('/') else ''}{p}" for p in paths]
        results = []
        
        status = st.empty()
        progress = st.progress(0)

        with ThreadPoolExecutor(max_workers=threads) as executor:
            # Launch all requests at once
            futures = [executor.submit(ultra_fast_scrape, url, config) for url in urls]
            
            for i, f in enumerate(futures):
                res = f.result()
                if res: results.append(res)
                if i % 10 == 0: # Update UI every 10 articles to save browser memory
                    progress.progress((i + 1) / len(urls))
                    status.text(f"🚀 Speed: {i+1}/{len(urls)} processed...")

        st.success(f"Finished! Processed {len(urls)} links.")
        st.dataframe(pd.DataFrame(results))
