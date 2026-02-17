import streamlit as st
import pandas as pd
import requests
import re # We use Regular Expressions to find hashtags
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Social Media Intelligence", page_icon="📈", layout="wide")

# 1. GENRE BRAIN
GENRE_MAP = {
    "World": ["un", "nato", "global", "international", "world", "foreign", "peace", "treaty", "diplomacy", "summit"],
    "Politics": ["election", "president", "minister", "parliament", "government", "protest", "policy"],
    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank", "dollar", "crypto"],
    "Sports": ["football", "goal", "match", "league", "win", "player", "tournament", "fifa"],
    "Technology": ["ai", "tech", "software", "google", "meta", "cyber", "robot", "space"],
    "Health": ["virus", "health", "doctor", "medicine", "covid", "vaccine", "fitness"],
    "Region": ["baku", "caucasus", "tbilisi", "karabakh", "central asia", "yerevan"]
}

def detect_genre(text):
    if not text or text == "Not_specified":
        return "Not_specified"
    
    text_lower = text.lower()
    for genre, keywords in GENRE_MAP.items():
        # This checks if any keyword from the list is in the post title
        if any(word in text_lower for word in keywords):
            return genre
    return "General"

# 2. HASHTAG EXTRACTOR FUNCTION
def get_hashtags(text):
    if not text or text == "Not_specified":
        return "Not_specified"
    # This regex looks for # followed by letters/numbers
    tags = re.findall(r"#(\w+)", text)
    return ", ".join(tags) if tags else "Not_specified"

# 3. UNIVERSAL EXTRACTION ENGINE
def extract_metadata(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0"}
    content = "Not_specified"
    source = "Unknown"
    
    # Identify Platform
    for s in ["facebook", "instagram", "twitter", "x.com", "youtube", "youtu.be", "tiktok"]:
        if s in url.lower(): source = s.capitalize()

    try:
        # TikTok Special Handling (oEmbed)
        if "tiktok.com" in url:
            resp = requests.get(f"https://www.tiktok.com/oembed?url={url}", timeout=5)
            if resp.status_code == 200:
                content = resp.json().get('title', 'Not_specified')
        else:
            # Universal Meta Tag Handling
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                og_desc = soup.find("meta", property="og:description")
                og_title = soup.find("meta", property="og:title")
                
                if og_desc: content = og_desc["content"]
                elif og_title: content = og_title["content"]
                elif soup.title: content = soup.title.string
    except:
        pass

    # Ensure "Not_specified" consistency
    if not content or "Login" in content or len(content) < 5:
        content = "Not_specified"

    return {
        "Source": source,
        "Genre": detect_genre(content),
        "Hashtags": get_hashtags(content), # NEW COLUMN
        "Title": content,
        "URL": url
    }

# 4. STREAMLIT UI
st.title("📈 Social Media Intelligence Dashboard")
st.write("Extracting Titles, Genres, and Hashtags from any social link.")

urls_text = st.text_area("Paste URLs (one per line):", height=200)

if st.button("🚀 Process Intelligence Report"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    if urls:
        results = []
        progress = st.progress(0)
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(extract_metadata, url) for url in urls]
            for i, f in enumerate(futures):
                res = f.result()
                if res: results.append(res)
                progress.progress((i + 1) / len(urls))

        df = pd.DataFrame(results)
        
        # Summary View
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Genre Summary")
            st.table(df['Genre'].value_counts())
        with col2:
            st.subheader("Platform Source")
            st.bar_chart(df['Source'].value_counts())

        # Main Data Table
        st.subheader("Extracted Intelligence")
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Export CSV", df.to_csv(index=False), "social_intelligence.csv")
