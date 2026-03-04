import streamlit as st
import os
import subprocess
import pandas as pd
import time
import random

# --- CLOUD BOOTSTRAP ---
def ensure_deno():
    deno_path = os.path.expanduser("~/.deno/bin")
    if not os.path.exists(os.path.join(deno_path, "deno")):
        subprocess.run("curl -fsSL https://deno.land/x/install/install.sh | sh", shell=True)
    if deno_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + deno_path

ensure_deno()

import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def scrape_tiktok(url, proxy_url=None):
    cookie_file = "tiktok_cookies.txt"
    
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'extract_flat': False,
        'cookiefile': cookie_file,
        'impersonate': ImpersonateTarget.from_str('chrome'),
        'extractor_args': {'tiktok': {'api_hostname': 'api22-normal-c-useast2a.tiktokv.com'}},
    }

    # Add proxy if provided to bypass Cloud IP blocks
    if proxy_url:
        ydl_opts['proxy'] = http://pcrlcxjv:hl1zglfn47du@31.59.20.176:6754/

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            return comments if comments else "EMPTY"
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- UI SECTION ---
st.title("🎵 TikTok Cloud Scraper (Anti-Block Edition)")

# Sidebar for Proxy Settings
with st.sidebar:
    st.header("Cloud Bypass")
    proxy_input = st.text_input("Residential Proxy (Optional)", 
                                placeholder="http://user:pass@host:port",
                                help="Recommended if getting 'EMPTY' errors on Streamlit Cloud.")

url_input = st.text_area("TikTok URLs:")

if st.button("🚀 Analyze"):
    urls = [u.strip() for u in url_input.split('\n') if u.strip()]
    if urls:
        for url in urls:
            st.write(f"🔍 Scraping: {url}")
            # Use the proxy from the sidebar
            result = scrape_tiktok(url, proxy_url=proxy_input if proxy_input else None)
            
            if result == "EMPTY":
                st.error("TikTok returned no data. Your Cloud IP is likely blocked. Please provide a proxy in the sidebar.")
            elif isinstance(result, list):
                st.success(f"Found {len(result)} comments!")
                # (Sentiment logic remains the same)
