import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Universal Social Categorizer", page_icon="🌐", layout="wide")

# 1. YOUR GENRE BRAIN (Customize these keywords!)
GENRE_MAP = {
    "Politics": ["election", "president", "minister", "parliament", "government", "protest", "policy"],
    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank", "dollar"],
    "Sports": ["football", "goal", "match", "league", "win", "player", "tournament", "fifa"],
    "Region": ["baku", "caucasus", "tbilisi", "karabakh", "central asia", "yerevan"]
}

def detect_genre(text):
    if not text or text == "Not_specified":
        return "Not_specified"
    
    text_lower = text.lower()
    for genre, keywords in GENRE_MAP.items():
        if any(word in text_lower for word in keywords):
            return genre
    return "General"

# 2. UNIVERSAL EXTRACTION ENGINE
def extract_metadata(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        # Step 1: Handle TikTok via its fast oEmbed API
        if "tiktok.com" in url:
            api_url = f"https://www.tiktok.com/oembed?url={url}"
            resp = requests.get(api_url, timeout=5)
            if resp.status_code == 200:
                title = resp.json().get('title', 'Not_specified')
                return {"Genre": detect_genre(title), "Title": title, "URL": url, "Source": "TikTok"}

        # Step 2: Handle everything else via Meta Tags
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for Open Graph Tags (Standard for FB, IG, YT)
            og_title = soup.find("meta", property="og:title")
            og_desc = soup.find("meta", property="og:description")
            
            # Priority: Description (usually has more text) > Title
            content = ""
            if og_desc: content = og_desc["content"]
            elif og_title: content = og_title["content"]
            elif soup.title: content = soup.title.string

            # Final Cleanup
            if not content or len(content) < 5 or "Login" in content or "Robot" in content:
                content = "Not_specified"
        else:
            content = "Not_specified"
    except:
        content = "Not_specified"

    # Identify Platform for the table
    source = "Unknown"
    for s in ["facebook", "instagram", "twitter", "x.com", "youtube", "youtu.be"]:
        if s in url.lower(): source = s.capitalize()

    return {
        "Genre": detect_genre(content),
        "Title": content,
        "URL": url,
        "Source": source
    }

# 3. STREAMLIT UI
st.title("🌐 Universal Social Media Categorizer")
st.info("Works with Facebook, Instagram, X, TikTok, and YouTube URLs.")

urls_text = st.text_area("Paste URLs (one per line):", height=200)

if st.button("🚀 Process All URLs"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    if urls:
        results = []
        progress = st.progress(0)
        
        # Keep workers moderate to prevent IP blocking across platforms
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(extract_metadata, url) for url in urls]
            for i, f in enumerate(futures):
                res = f.result()
                if res: results.append(res)
                progress.progress((i + 1) / len(urls))

        df = pd.DataFrame(results)
        
        # Table Summary
        st.subheader("Summary Statistics")
        counts = df['Genre'].value_counts().reset_index()
        counts.columns = ['Genre', 'Count']
        st.table(counts)

        # Full Results
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Download CSV", df.to_csv(index=False), "universal_social_data.csv")
