import streamlit as st
import os
import subprocess
import pandas as pd
import time
import random

# --- 1. CLOUD BOOTSTRAP (Required for TikTok JS Challenges) ---
def ensure_deno():
    """Installs Deno in the Streamlit Cloud environment to solve security puzzles."""
    deno_path = os.path.expanduser("~/.deno/bin")
    if not os.path.exists(os.path.join(deno_path, "deno")):
        with st.spinner("🛠️ Setting up Security Engine (Deno)..."):
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
    st.error("Missing libraries. Ensure 'yt-dlp[default,curl-cffi]' and 'vaderSentiment' are in requirements.txt.")
    st.stop()

# --- 3. SCRAPING LOGIC ---
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(text)
    if score['compound'] >= 0.05: return "Positive"
    if score['compound'] <= -0.05: return "Negative"
    return "Neutral"

def scrape_tiktok(url):
    cookie_file = "tiktok_cookies.txt"
    
    # YOUR WORKING PROXY STRING
    my_proxy = "http://pcrlcxjv:hl1zglfn47du@31.59.20.176:6754/"

    if not os.path.exists(cookie_file):
        return "ERROR: Missing tiktok_cookies.txt in your GitHub repository."

    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'extract_flat': False,
        'cookiefile': cookie_file,
        # Mandatory 2026 TLS Impersonation
        'impersonate': ImpersonateTarget.from_str('chrome'),
        # Integrated Proxy
        'proxy': my_proxy,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.tiktok.com/',
        },
        'extractor_args': {
            'tiktok': {
                'api_hostname': 'api16-normal-c-useast1a.tiktokv.com',
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
st.set_page_config(page_title="TikTok AI Sentiment Scraper", layout="wide")
st.title("🎵 TikTok Cloud Scraper")
st.subheader("2026 Hardened Edition with Webshare Proxy")

if not os.path.exists("tiktok_cookies.txt"):
    st.error("🚨 tiktok_cookies.txt NOT FOUND. Please upload it to your GitHub repo.")

url_input = st.text_area("Paste TikTok URLs (one per line):", height=150)

if st.button("🚀 Start Analysis"):
    urls = [u.strip() for u in url_input.split('\n') if u.strip()]
    
    if not urls:
        st.warning("Please enter at least one URL.")
    else:
        all_comments = []
        progress_bar = st.progress(0)
        
        for idx, url in enumerate(urls):
            st.write(f"🔍 Analyzing: {url}")
            
            result = scrape_tiktok(url)
            
            if result == "EMPTY":
                st.error("TikTok returned no data. Your proxy might be throttled or cookies expired.")
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
                st.success(f"Fetched {len(result)} comments!")

            progress_bar.progress((idx + 1) / len(urls))
            # Human-like delay to prevent proxy burnout
            if idx < len(urls) - 1:
                time.sleep(random.uniform(3, 6))

        if all_comments:
            df = pd.DataFrame(all_comments)
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.write("### Sentiment Summary")
                st.bar_chart(df['Sentiment'].value_counts())
            with c2:
                st.write("### Raw Data")
                st.dataframe(df, use_container_width=True)
            
            st.download_button("📥 Download CSV", df.to_csv(index=False), "tiktok_sentiment.csv")
