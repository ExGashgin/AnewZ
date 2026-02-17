import streamlit as st
import pandas as pd
from newspaper import Article, Config
from concurrent.futures import ThreadPoolExecutor
import nltk

st.set_page_config(page_title="Bulk URL Scraper", page_icon="🚀", layout="wide")

@st.cache_resource
def setup_nltk():
    nltk.download('punkt_tab', quiet=True)
setup_nltk()

# --- THE FAST SCRAPE FUNCTION ---
def fast_scrape_url(url, config):
    try:
        # We only download and parse; we SKIP nlp() to save 80% of time
        article = Article(url, config=config)
        article.download()
        article.parse()
        
        return {
            "Title": article.title,
            "Author": ", ".join(article.authors) if article.authors else "N/A",
            "Date": article.publish_date,
            "URL": url
        }
    except:
        return None

# --- UI INTERFACE ---
st.title("🚀 Ultra-Fast Bulk URL Scraper")
st.write("Paste your list of full URLs below for high-speed extraction.")

urls_text = st.text_area("Paste URLs (one per line):", height=250, placeholder="https://bbc.com/news1\nhttps://cnn.com/news2")

# Speed Slider
threads = st.select_slider("Speed Level (Connections)", options=[5, 10, 20, 50, 100], value=50)

if st.button("⚡ Start Bulk Extraction"):
    url_list = [u.strip() for u in urls_text.split('\n') if u.strip()]
    
    if url_list:
        # CONFIGURATION FOR MAXIMUM SPEED
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0'
        config.fetch_images = False      # SPEED BOOST: Don't download pictures
        config.request_timeout = 7       # Move on if a site is slow
        config.memoize_articles = False  # Don't waste memory on caching
        
        results = []
        progress = st.progress(0)
        status = st.empty()

        # RUNNING IN PARALLEL
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(fast_scrape_url, url, config) for url in url_list]
            
            for i, f in enumerate(futures):
                res = f.result()
                if res:
                    results.append(res)
                
                # Update progress every 5 articles to save browser memory
                if i % 5 == 0 or i == len(url_list)-1:
                    progress.progress((i + 1) / len(url_list))
                    status.text(f"Processed {i+1} of {len(url_list)}...")

        # DISPLAY TABLE
        if results:
            df = pd.DataFrame(results)
            st.success(f"Successfully extracted {len(results)} articles!")
            st.dataframe(df, use_container_width=True)
            
            # EXPORT
            st.download_button("📥 Download Results (CSV)", df.to_csv(index=False), "bulk_urls.csv")
    else:
        st.warning("Please paste some URLs first.")
