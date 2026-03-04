import streamlit as st
import os
import subprocess
import pandas as pd
import time
import random

# --- 1. CLOUD BOOTSTRAP (Required for 2026 JS Challenges) ---
def ensure_deno():
    """Installs Deno to solve TikTok's mandatory JS puzzles."""
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
    st.error("Missing requirements. Ensure 'yt-dlp[default,curl-cffi]' is in requirements.txt.")
    st.stop()

# --- 3. SCRAPER LOGIC ---
analyzer = SentimentIntensityAnalyzer()

def scrape_tiktok(url):
    # Updated path to match your GitHub structure
    cookie_file = "comment_scrapers/tiktok/tiktok_cookies.txt"
    
    # Check if the folder exists for debugging
    if not os.path.exists(cookie_file):
        return f"ERROR: File not found at {cookie_file}. Check folder structure."

    # Your working Webshare proxy
    my_proxy = "http://pcrlcxjv:hl1zglfn47du@31.59.20.176:6754/"

    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'cookiefile': cookie_file, # Uses the new path
        'proxy': my_proxy,
        'impersonate': yt_dlp.networking.impersonate.ImpersonateTarget.from_str('chrome'),
        'extractor_args': {
            'tiktok': {
                'api_hostname': 'api-h2.tiktokv.com',
            }
        },
    }
    
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'cookiefile': cookie_file,
        'impersonate': ImpersonateTarget.from_str('chrome'), # 2026 TLS spoofing
        'proxy': my_proxy,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.tiktok.com/',
        },
        'extractor_args': {
            'tiktok': {
                'api_hostname': random.choice(api_nodes), # Randomize node to avoid rate limits
                'app_name': 'musical_ly',
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            return comments if comments else "EMPTY"
    except Exception as e:
        return f"CRITICAL ERROR: {str(e)}"

# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="TikTok AI Scraper", layout="wide")
st.title("🎵 TikTok Cloud Scraper (2026 Bypass)")

# Check connection status in sidebar
with st.sidebar:
    st.header("Connection Status")
    if st.button("🕵️ Run Diagnostic"):
        try:
            # Test if proxy is live and working
            ip = subprocess.check_output(f'curl --proxy "http://pcrlcxjv:hl1zglfn47du@31.59.20.176:6754/" -s https://ifconfig.me', shell=True).decode()
            st.write(f"✅ Proxy Live: {ip}")
            # Test if Deno is available
            st.write("✅ Deno Engine: Ready")
        except:
            st.error("❌ Proxy/Deno Failed")

url_input = st.text_area("Paste TikTok URLs:", height=100)

if st.button("🚀 Analyze"):
    urls = [u.strip() for u in url_input.split('\n') if u.strip()]
    if urls:
        for url in urls:
            st.write(f"🔍 Checking: {url}")
            result = scrape_tiktok(url)
            
            if result == "EMPTY":
                st.error("TikTok served an empty response. This means your cookies and proxy IP are out of sync.")
                st.info("👉 Action: Re-export cookies while using your proxy in your browser.")
            elif isinstance(result, list):
                df = pd.DataFrame(result)
                st.success(f"Found {len(df)} comments!")
                st.dataframe(df[['author', 'text']])
            else:
                st.error(result)
            
            # Anti-ban sleep
            time.sleep(random.uniform(5, 10))
