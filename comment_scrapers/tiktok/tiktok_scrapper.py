import streamlit as st
import os
import subprocess
import pandas as pd
import time
import random

# --- 1. CLOUD BOOTSTRAP ---
def ensure_deno():
    """Installs Deno to solve TikTok's mandatory JS puzzles in 2026."""
    deno_path = os.path.expanduser("~/.deno/bin")
    if not os.path.exists(os.path.join(deno_path, "deno")):
        with st.spinner("🛠️ Syncing Security Engine (Deno)..."):
            subprocess.run("curl -fsSL https://deno.land/x/install/install.sh | sh", shell=True)
    if deno_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + deno_path

ensure_deno()

# --- 2. IMPORTS ---
try:
    import yt_dlp
    from yt_dlp.networking.impersonate import ImpersonateTarget
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    st.error("Missing requirements. Ensure 'yt-dlp[default,curl-cffi]' and 'vaderSentiment' are in requirements.txt.")
    st.stop()

# --- 3. ANALYSIS LOGIC ---
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    """Categorizes text using VADER."""
    if not text:
        return "Neutral"
    score = analyzer.polarity_scores(text)
    compound = score['compound']
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# --- 4. SCRAPER LOGIC ---
def scrape_tiktok(url):
    api_nodes = [
        'api16-normal-c-useast1a.tiktokv.com',
        'api22-normal-c-useast2a.tiktokv.com',
        'api-h2.tiktokv.com'
    ]

    # File path must match your GitHub structure
    cookie_file = "comment_scrapers/tiktok/tiktok_cookies.txt"
    my_proxy = "http://pcrlcxjv:hl1zglfn47du@31.59.20.176:6754/"

    if not os.path.exists(cookie_file):
        return f"ERROR: {cookie_file} not found."

    # Combined and fixed ydl_opts
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'cookiefile': cookie_file,
        'proxy': my_proxy,
        'impersonate': ImpersonateTarget.from_str('chrome'), # 2026 TLS spoofing
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.tiktok.com/',
        },
        'extractor_args': {
            'tiktok': {
                'api_hostname': random.choice(api_nodes), 
                'app_name': 'musical_ly',
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            
            if not comments:
                return "EMPTY"
            
            # Format results for the dataframe
            results = []
            for c in comments:
                text = c.get('text', '')
                results.append({
                    "Author": c.get('author'),
                    "Text": text,
                    "Sentiment": get_sentiment(text),
                    "URL": url
                })
            return results
    except Exception as e:
        return f"CRITICAL ERROR: {str(e)}"

# --- 5. STREAMLIT UI ---
st.set_page_config(page_title="TikTok AI Scraper", layout="wide")
st.title("📊 Bulk TikTok Scraper & Sentiment Analysis")

with st.sidebar:
    st.header("System Check")
    if st.button("🕵️ Run Diagnostic"):
        try:
            ip = subprocess.check_output(f'curl --proxy "http://pcrlcxjv:hl1zglfn47du@31.59.20.176:6754/" -s https://ifconfig.me', shell=True).decode()
            st.success(f"Proxy Active: {ip}")
        except:
            st.error("Proxy connection failed.")

url_input = st.text_area("Paste TikTok URLs (one per line):", height=150)

if st.button("🚀 Scrape & Analyze"):
    urls = [u.strip() for u in url_input.split('\n') if u.strip()]
    all_results = []
    
    if urls:
        for url in urls:
            with st.status(f"Processing: {url}", expanded=False):
                data = scrape_tiktok(url)
                
                if isinstance(data, list):
                    all_results.extend(data)
                    st.write(f"✅ Found {len(data)} comments.")
                elif data == "EMPTY":
                    st.warning("⚠️ TikTok returned no data. Check your cookies.")
                else:
                    st.error(data)
                
                time.sleep(random.uniform(3, 6)) # Polite delay

    if all_results:
        df = pd.DataFrame(all_results)
        st.divider()
        
        # Dashboard
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Sentiment Summary")
            st.bar_chart(df['Sentiment'].value_counts())
        
        with col2:
            st.subheader("Raw Data")
            st.dataframe(df, use_container_width=True)
            
        st.download_button("📥 Download CSV", df.to_csv(index=False), "tiktok_analysis.csv")
