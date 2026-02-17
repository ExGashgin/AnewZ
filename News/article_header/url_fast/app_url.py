import streamlit as st
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="TikTok Genre Extractor", page_icon="📂", layout="wide")

# 1. THE GENRE BRAIN (Keyword Mapping)
# You can add or change these words to match your needs!
GENRE_MAP = {
    "Politics": ["election", "president", "minister", "parliament", "government", "protest"],
    "Economy": ["gas", "oil", "price", "market", "finance", "business", "dollar", "crypto"],
    "Region": ["caucasus", "karabakh", "baku", "tbilisi", "yerevan", "central asia"],
    "Sports": ["football", "goal", "match", "olympics", "fifa", "score", "win"],
    "Entertainment": ["music", "dance", "funny", "challenge", "movie", "star", "celebrity"]
}

def detect_genre(title):
    title_lower = title.lower()
    for genre, keywords in GENRE_MAP.items():
        if any(word in title_lower for word in keywords):
            return genre
    return "General" # Default if no keywords match

# 2. DATA EXTRACTION FUNCTION
def get_tiktok_data(url):
    try:
        # Secret API for fast TikTok titles
        api_url = f"https://www.tiktok.com/oembed?url={url}"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('title', 'N/A')
            
            # Clean title (TikTok often adds "TikTok - ..." to titles)
            clean_title = title.split(" TikTok")[0]
            
            return {
                "Genre": detect_genre(clean_title), # Run the brain
                "Title": clean_title,
                "Author": data.get('author_name', 'N/A'),
                "URL": url
            }
    except:
        pass
    return None

# 3. STREAMLIT UI
st.title("📂 Video Title & Genre Extractor")
urls_text = st.text_area("Paste TikTok URLs (one per line):", height=250)

if st.button("🚀 Process Videos"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    if urls:
        results = []
        progress = st.progress(0)
        
        # Parallel processing for speed
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_tiktok_data, url) for url in urls]
            for i, f in enumerate(futures):
                res = f.result()
                if res: results.append(res)
                progress.progress((i + 1) / len(urls))

        if results:
            df = pd.DataFrame(results)
            st.success(f"Success! Categorized {len(results)} videos.")
            
            # Show the data
            st.dataframe(df, use_container_width=True)
            
            # Download
            st.download_button("📥 Download CSV", df.to_csv(index=False), "categorized_videos.csv")
