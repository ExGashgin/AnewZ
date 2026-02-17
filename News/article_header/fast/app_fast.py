import streamlit as st
import pandas as pd
from newspaper import Article, Config
from concurrent.futures import ThreadPoolExecutor # This is the "Speed" engine
import nltk
import time

st.set_page_config(page_title="High-Speed Scraper", page_icon="⚡", layout="wide")

# Standard setup
@st.cache_resource
def load_nltk():
    nltk.download('punkt_tab', quiet=True)
load_nltk()

# --- THE FAST EXTRACTION FUNCTION ---
def fast_scrape(full_url, config):
    try:
        article = Article(full_url, config=config)
        article.download()
        article.parse()
        article.nlp()
        
        # Genre detection logic
        path_parts = [p for p in full_url.split('/') if p]
        genre = path_parts[2].capitalize() if len(path_parts) > 2 else "News"
        
        return {
            "Genre": genre,
            "Title": article.title,
            "Date": article.publish_date,
            "Summary": article.summary[:150] + "...",
            "URL": full_url
        }
    except:
        return None

# --- UI ---
st.title("⚡ High-Speed Bulk Scraper")
base_url = st.text_input("Base Domain:", value="https://anewz.tv").strip().rstrip('/')
paths_text = st.text_area("Paste 1,000+ Paths here:", height=200)

# Speed Setting
num_threads = st.slider("How many simultaneous connections? (Speed)", 5, 50, 20)

if st.button("🚀 Start High-Speed Extraction"):
    paths = [p.strip() for p in paths_text.split('\n') if p.strip()]
    if paths:
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0'
        config.request_timeout = 10
        
        urls = [f"{base_url}{'/' if not p.startswith('/') else ''}{p}" for p in paths]
        
        results = []
        progress_bar = st.progress(0)
        status = st.empty()

        # START MULTITHREADING
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Map the function to all URLs across many threads
            futures = [executor.submit(fast_scrape, url, config) for url in urls]
            
            for i, future in enumerate(futures):
                res = future.result()
                if res:
                    results.append(res)
                # Update UI every few articles
                progress_bar.progress((i + 1) / len(urls))
                status.text(f"Processed {i+1} of {len(urls)}...")

        if results:
            df = pd.DataFrame(results)
            st.success(f"Finished! Extracted {len(results)} articles.")
            st.dataframe(df)
            st.download_button("📥 Download Excel/CSV", df.to_csv(index=False), "bulk_data.csv")
