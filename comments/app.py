import os
import subprocess
import streamlit as st
import asyncio
import pandas as pd

# 1. SET ENVIRONMENT VARIABLE FIRST (Must be before importing playwright)
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/tmp/playwright-browsers"

from playwright.async_api import async_playwright

# 2. INSTALLATION LOGIC
@st.cache_resource
def install_playwright_locally():
    try:
        # We check if chromium exists to avoid re-installing on every rerun
        if not os.path.exists("/tmp/playwright-browsers"):
            subprocess.run(["python", "-m", "playwright", "install", "chromium"], check=True)
    except Exception as e:
        st.error(f"Playwright installation failed: {e}")

# Run installer
install_playwright_locally()

# 3. SCRAPING LOGIC
async def scrape_youtube(url):
    async with async_playwright() as p:
        # Launch using the path we set above
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Add a realistic User-Agent to avoid immediate bot detection
        await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
        
        await page.goto(url, wait_until="networkidle")
        
        # YouTube specific: Scroll to trigger comments
        await page.mouse.wheel(0, 2000)
        await asyncio.sleep(3) # Wait for load
        
        comments = await page.locator("#content-text").all_inner_texts()
        await browser.close()
        return [{"Comment": c} for c in comments]

# 4. STREAMLIT UI
st.title("Social Media Comment Scraper")

url = st.text_input("Enter YouTube URL:")

if st.button("Scrape"):
    if url:
        with st.spinner("Fetching comments..."):
            results = asyncio.run(scrape_youtube(url))
            if results:
                df = pd.DataFrame(results)
                st.dataframe(df)
                st.download_button("Download CSV", df.to_csv(index=False), "data.csv")
            else:
                st.warning("No comments found. Try scrolling the page manually in your browser to see if they are public.")
