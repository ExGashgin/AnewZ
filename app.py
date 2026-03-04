import streamlit as st
import os
import subprocess
import pandas as pd
import time
import random

# --- 1. CLOUD BOOTSTRAP (Bypass 403 Errors) ---
def ensure_deno():
    """Installs Deno in the Streamlit Cloud environment for JS challenge solving."""
    deno_path = os.path.expanduser("~/.deno/bin")
    if not os.path.exists(os.path.join(deno_path, "deno")):
        with st.spinner("🛠️ Setting up Cloud Security Engine (Deno)..."):
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

# --- 3. LOGIC ---
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(text)
    if score['compound'] >= 0.05: return "Positive"
    if score['compound'] <= -0.05: return "Negative"
    return "Neutral"

def scrape_tiktok(url, proxy_url=None):
    cookie_file = "tiktok_cookies.txt"
    
    if not os.path.exists(cookie_file):
        return "ERROR: Missing tiktok_cookies.txt"

    # 2026 Hardened Options
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'extract_flat': False,
        'cookiefile': cookie_file,
        'impersonate': ImpersonateTarget.from_str('chrome'), # Mimics Chrome TLS fingerprint
        'proxy': proxy_url if proxy_url else None, # Bypasses Cloud IP bans
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.tiktok.com/',
        },
        'extractor_args': {
            'tiktok': {
                'api_hostname': 'api16-normal-c-useast1a.tiktokv.com', # Alternate API node
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
st.set_page_config(page_title="TikTok AI Scraper 2026", layout="wide")
st.title("🎵 TikTok Cloud Scraper")

with st.sidebar:
    st.header("Settings")
    # Wrap input in quotes internally to avoid SyntaxError
    proxy_input = st.text_input("Residential Proxy", placeholder="http://user:pass@host:port")
    st.info("💡 If you get 'EMPTY', your Proxy is likely blocked or not Residential.")
    
    if os.path.exists("tiktok_cookies.txt"):
        st.success("✅ Cookies Detected")
    else:
        st.error("❌ Cookies Missing")

url_input = st.text_area("Paste TikTok URLs (one per line):", height=150)

if st.button("🚀 Start Deep Analysis"):
    urls = [u.strip() for u in url_input.split('\n') if u.strip()]
    
    if not urls:
        st.warning("Please enter at least one URL.")
    else:
        all_comments = []
        progress_bar = st.progress(0)
        
        for idx, url in enumerate(urls):
            st.write(f"🔍 Processing: {url}")
            
            # Pass the proxy string directly to the function
            result = scrape_tiktok(url, proxy_url=proxy_input if proxy_input else None)
            
            if result == "EMPTY":
                st.error(f"TikTok returned no data for this video. Try a different proxy.")
            elif isinstance(result, str) and "ERROR" in result:
                st.error(result)
            else:
                for c in result:
                    all_comments.append({
                        "Author": c.get('author'),
                        "Text": c.get('text'),
                        "Sentiment": get_sentiment(c.get('text')),
                        "Video": url
                    })
                st.success(f"Successfully pulled {len(result)} comments!")

            progress_bar.progress((idx + 1) / len(urls))
            if idx < len(urls) - 1:
                time.sleep(random.uniform(3, 7)) # Human behavior simulation

        if all_comments:
            df = pd.DataFrame(all_comments)
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Sentiment Summary")
                st.bar_chart(df['Sentiment'].value_counts())
            with col2:
                st.subheader("Raw Data")
                st.dataframe(df, use_container_width=True)
            
            st.download_button("📥 Download Results (CSV)", df.to_csv(index=False), "tiktok_analysis.csv")
