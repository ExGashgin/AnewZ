import streamlit as st
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="TikTok Bulk Extractor", page_icon="🎵", layout="wide")

def get_tiktok_data(url):
    """Uses TikTok oEmbed API to get clean metadata without scraping HTML"""
    try:
        # The oEmbed endpoint is the secret to fast, clean titles
        api_url = f"https://www.tiktok.com/oembed?url={url}"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # Title is usually the caption. We clean it for the 'Genre'
            title = data.get('title', 'N/A')
            author = data.get('author_name', 'N/A')
            
            # Simple Genre Logic: Extract first hashtag or word
            genre = "Video"
            if "#" in title:
                genre = title.split("#")[1].split()[0].capitalize()
            
            return {
                "Genre": genre,
                "Title": title,
                "Author": author,
                "URL": url
            }
    except Exception:
        pass
    return None

st.title("🎵 TikTok High-Speed Metadata Extractor")
urls_text = st.text_area("Paste TikTok URLs (one per line):", height=200)

if st.button("🚀 Extract Video Titles"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    if urls:
        results = []
        progress = st.progress(0)
        
        # Use 20 threads (TikTok's oEmbed is rate-limited, don't go too fast)
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(get_tiktok_data, url) for url in urls]
            for i, f in enumerate(futures):
                res = f.result()
                if res: results.append(res)
                progress.progress((i + 1) / len(urls))

        if results:
            df = pd.DataFrame(results)
            st.success(f"Extracted {len(results)} video titles!")
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download CSV", df.to_csv(index=False), "tiktok_data.csv")
