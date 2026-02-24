import streamlit as st
import os
import shutil
import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import random
import time

# --- 1. CONFIGURATION & BROWSER SETUP ---
st.set_page_config(page_title="Bulk Social Scraper", page_icon="🚀", layout="wide")

def get_chrome_path():
    """Finds the Chromium executable installed via packages.txt"""
    paths = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        shutil.which("chromium"),
        shutil.which("chromium-browser")
    ]
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None

# --- 2. SCRAPING ENGINE (Single URL) ---
async def scrape_youtube_bulk(url_list, scrolls=10):
    chrome_path = get_chrome_path()
    master_data = []
    
    async with async_playwright() as p:
        # Launch browser once to save time
        browser = await p.chromium.launch(executable_path=chrome_path, headless=True)
        
        for url in url_list:
            try:
                # Create a fresh context for EVERY url to clear cookies/cache
                context = await browser.new_context(
                    user_agent=random.choice([
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                    ])
                )
                page = await context.new_page()
                
                # Navigate and scrape (using your existing logic)
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # ... [Your Scrolling & Scraping Logic Here] ...
                
                await context.close() # Close context, but keep browser open
                
                # THE FIX: Add a random wait to avoid IP blocking
                wait_time = random.randint(3, 7)
                time.sleep(wait_time) 
                
            except Exception as e:
                st.error(f"Failed on {url}: {e}")
                
        await browser.close()
    return master_data

# --- 3. STREAMLIT UI ---
st.title("🚀 Bulk YouTube Comment Scraper")
st.markdown("Paste multiple URLs below to scrape comments in bulk. Designed for 2026 platform standards.")

# Input Area
urls_input = st.text_area("Enter YouTube URLs (one per line):", height=200, placeholder="https://www.youtube.com/watch?v=...\nhttps://www.youtube.com/watch?v=...")

# Options
col1, col2 = st.columns(2)
with col1:
    scroll_depth = st.slider("Scroll Depth (More scrolls = more comments)", 1, 50, 10)
with col2:
    st.info("💡 Note: Processing 100 URLs may take 10-15 minutes. Keep this tab open.")

# Process Button
if st.button("Start Bulk Scrape"):
    # Clean the input list
    url_list = [u.strip() for u in urls_input.split('\n') if u.strip()]
    
    if not url_list:
        st.error("Please provide at least one valid URL.")
    else:
        master_data = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Loop through each URL
        for index, url in enumerate(url_list):
            status_text.text(f"Processing ({index + 1}/{len(url_list)}): {url}")
            
            # Run the scraper
            data, error = asyncio.run(scrape_youtube(url, max_scrolls=scroll_depth))
            
            if data:
                master_data.extend(data)
            else:
                st.warning(f"Could not get data for: {url}. Error: {error}")
            
            # Update progress
            progress_bar.progress((index + 1) / len(url_list))
        
        # --- 4. FINAL RESULTS ---
        status_text.text("✅ All tasks complete!")
        if master_data:
            df = pd.DataFrame(master_data)
            st.subheader("Results Preview")
            st.dataframe(df.head(100))
            
            # Download Button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Bulk CSV",
                data=csv,
                file_name="bulk_youtube_comments.csv",
                mime="text/csv",
            )
        else:
            st.error("No comments were collected from any of the URLs provided.")

# Sidebar Diagnostics
with st.sidebar:
    st.header("System Status")
    p = get_chrome_path()
    if p:
        st.success("Browser: Detected")
    else:
        st.error("Browser: Missing")
        st.write("Ensure `packages.txt` exists and Reboot.")
