import streamlit as st
import pandas as pd
import requests
from newspaper import Article, Config
from concurrent.futures import ThreadPoolExecutor

# --- SUPER SLIM SCRAPER ---
def ultra_fast_extract(url, config):
    try:
        # TIKTOK / YOUTUBE FAST PATH
        if any(x in url for x in ['tiktok.com', 'youtube.com', 'youtu.be']):
            # Use oEmbed for instant results on video platforms
            api_url = f"https://www.tiktok.com/oembed?url={url}" if 'tiktok' in url else f"https://www.youtube.com/oembed?url={url}&format=json"
            data = requests.get(api_url, timeout=3).json()
            title = data.get('title', 'Not_specified')
            return {"Genre": "Video", "Title": title, "URL": url}

        # NEWS ARTICLE FAST PATH
        article = Article(url, config=config)
        article.download()
        article.parse()
        # We completely skip NLP and images here
        return {
            "Genre": "General", 
            "Title": article.title if article.title else "Not_specified", 
            "URL": url
        }
    except:
        return {"Genre": "Not_specified", "Title": "Not_specified", "URL": url}

# --- UI ---
st.title("⚡ Extreme Speed Scraper")
urls_text = st.text_area("Paste 10,000+ URLs:", height=200)

if st.button("🚀 Start High-Velocity Extraction"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    if urls:
        # OPTIMIZED CONFIG
        conf = Config()
        conf.fetch_images = False
        conf.request_timeout = 4  # Don't get stuck on slow sites
        conf.browser_user_agent = 'Mozilla/5.0'
        
        results = []
        progress = st.progress(0)
        
        # Use ThreadPool with a controlled worker count
        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(ultra_fast_extract, url, conf) for url in urls]
            for i, f in enumerate(futures):
                results.append(f.result())
                if i % 20 == 0: # Update UI less often to save speed
                    progress.progress((i + 1) / len(urls))
        
        st.dataframe(pd.DataFrame(results))
