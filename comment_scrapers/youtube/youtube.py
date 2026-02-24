import streamlit as st
import pandas as pd
import yt_dlp
import time

def get_comments_bulk(url):
    """Uses yt-dlp to grab comments without needing a browser."""
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            return [{"Author": c.get('author'), "Text": c.get('text'), "URL": url} for c in comments]
    except Exception as e:
        return None

st.title("🚀 Bulk URL Scraper")
urls_input = st.text_area("Paste URLs (one per line):")

if st.button("Scrape All"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    all_data = []
    
    progress_bar = st.progress(0)
    for i, url in enumerate(urls):
        st.write(f"Scraping: {url}")
        data = get_comments_bulk(url)
        if data:
            all_data.extend(data)
        progress_bar.progress((i + 1) / len(urls))
        # Wait 1 second between URLs to avoid being blocked
        time.sleep(1)

    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f"Finished! Total comments: {len(df)}")
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "bulk_data.csv")
