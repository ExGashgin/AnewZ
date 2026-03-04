import streamlit as st
import os
import subprocess
import sys
import pandas as pd
import time
import random

# --- 2026 CLOUD BOOTSTRAP (RUNS FIRST) ---
def ensure_deno():
    """Installs Deno in the Streamlit Cloud environment if not present."""
    deno_path = os.path.expanduser("~/.deno/bin")
    if not os.path.exists(os.path.join(deno_path, "deno")):
        with st.status("🛠️ Setting up Cloud Security Bypass (Deno)...", expanded=True):
            st.write("Installing Deno runtime...")
            subprocess.run("curl -fsSL https://deno.land/x/install/install.sh | sh", shell=True)
            st.write("Configuring Path...")
    
    if deno_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + deno_path

# Execute Bootstrap
ensure_deno()

# --- NOW IMPORT SCRAPING LIBS ---
try:
    import yt_dlp
    from yt_dlp.networking.impersonate import ImpersonateTarget
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    st.error("Missing libraries. Please check your requirements.txt")
    st.stop()

# Initialize Sentiment
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not text: return "Neutral"
    score = analyzer.polarity_scores(text)
    if score['compound'] >= 0.05: return "Positive"
    if score['compound'] <= -0.05: return "Negative"
    return "Neutral"

def scrape_tiktok(url):
    cookie_file = "tiktok_cookies.txt"
    
    if not os.path.exists(cookie_file):
        return "ERROR: tiktok_cookies.txt not found in GitHub repo."

    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'extract_flat': False,
        'cookiefile': cookie_file,
        # Mandatory 2026 TLS Impersonation
        'impersonate': ImpersonateTarget.from_str('chrome'),
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        },
        'extractor_args': {
            'tiktok': {
                'api_hostname': 'api22-normal-c-useast2a.tiktokv.com',
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            return comments if comments else "EMPTY"
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- UI SECTION ---
st.set_page_config(page_title="TikTok AI Sentiment", page_icon="🎵")
st.title("🎵 TikTok Cloud Scraper")
st.caption("2026 Edition: Automated Deno Setup + TLS Impersonation")

# Sidebar for Status
with st.sidebar:
    st.header("Environment Status")
    if os.path.exists("tiktok_cookies.txt"):
        st.success("✅ Cookies Found")
    else:
        st.error("❌ Cookies Missing")
    
    # Check if Deno is actually working
    try:
        deno_version = subprocess.check_output(["deno", "--version"]).decode()
        st.info("✅ Deno Engine Ready")
    except:
        st.warning("⚠️ Deno Engine Not Found Yet")

urls_input = st.text_area("Paste TikTok URLs (one per line):")

if st.button("🚀 Analyze TikToks"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    all_data = []
    
    if not urls:
        st.warning("Please enter a URL.")
    else:
        for idx, url in enumerate(urls):
            st.write(f"🔍 Accessing Video {idx+1}...")
            result = scrape_tiktok(url)
            
            if isinstance(result, list):
                for c in result:
                    all_data.append({
                        "User": c.get('author'),
                        "Comment": c.get('text'),
                        "Sentiment": get_sentiment(c.get('text')),
                        "Source": url
                    })
                st.success(f"Pulled {len(result)} comments.")
            else:
                st.error(f"Error: {result}")
            
            # Anti-Ban Delay
            if idx < len(urls) - 1:
                time.sleep(random.uniform(4, 8))

        if all_data:
            df = pd.DataFrame(all_data)
            st.divider()
            st.subheader("Sentiment Analysis Results")
            st.bar_chart(df['Sentiment'].value_counts())
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download Results", df.to_csv(index=False), "tiktok_analysis.csv")
