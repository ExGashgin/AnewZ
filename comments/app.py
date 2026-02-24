import streamlit as st
import os
import shutil
import asyncio
import pandas as pd
from playwright.async_api import async_playwright

st.set_page_config(page_title="Social Scraper 2026", page_icon="🕵️")

# --- 1. SMART BROWSER FINDER ---
def get_chrome_path():
    # Common paths for Chromium on Streamlit's Linux servers
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

# --- 2. SCRAPING ENGINE ---
async def scrape_youtube(url):
    chrome_path = get_chrome_path()
    if not chrome_path:
        return None, "Chromium not found. Please check packages.txt and Reboot App."

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(executable_path=chrome_path, headless=True)
            page = await browser.new_page()
            
            # Navigate
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # YouTube: Scroll to load comments
            await page.evaluate("window.scrollTo(0, 1000)")
            await asyncio.sleep(3)
            
            # Grab comments
            comments = await page.locator("#content-text").all_inner_texts()
            await browser.close()
            
            if not comments:
                return None, "No comments found. Is this a private video?"
                
            return [{"Comment": text} for text in comments], None
    except Exception as e:
        return None, str(e)

# --- 3. USER INTERFACE ---
st.title("🚀 Social Media Scraper")
st.markdown("Try with a public YouTube video first to verify.")

target_url = st.text_input("Enter URL:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Extract Comments"):
    if not target_url:
        st.warning("Please enter a URL first!")
    else:
        with st.spinner("🤖 Browser is working..."):
            data, error = asyncio.run(scrape_youtube(target_url))
            
            if error:
                st.error(f"Error: {error}")
                if "Chromium not found" in error:
                    st.info("💡 Tip: Go to 'Manage App' -> 'Reboot App' to force installation.")
            else:
                st.success(f"Found {len(data)} comments!")
                df = pd.DataFrame(data)
                st.dataframe(df)
                st.download_button("📥 Download CSV", df.to_csv(index=False), "comments.csv")

# --- 4. DIAGNOSTICS (Hidden in Sidebar) ---
with st.sidebar:
    st.header("System Health")
    path = get_chrome_path()
    if path:
        st.write(f"✅ Browser ready at: `{path}`")
    else:
        st.write("❌ Browser missing")
