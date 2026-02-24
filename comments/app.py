import streamlit as st
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import shutil

# This function finds where Streamlit installed Chromium
def get_chromium_path():
    return shutil.which("chromium") or shutil.which("chromium-browser")

async def scrape_youtube(url):
    path = get_chromium_path()
    if not path:
        st.error("Chromium not found. Check packages.txt")
        return []

    async with async_playwright() as p:
        # We use 'executable_path' to point to the system-installed Chrome
        browser = await p.chromium.launch(
            executable_path=path,
            headless=True
        )
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        
        # Scroll logic
        await page.mouse.wheel(0, 2000)
        await asyncio.sleep(2)
        
        comments = await page.locator("#content-text").all_inner_texts()
        await browser.close()
        return [{"Comment": c} for c in comments]

st.title("Social Media Scraper 2026")
url = st.text_input("YouTube URL:")

if st.button("Scrape"):
    with st.spinner("Using system browser..."):
        results = asyncio.run(scrape_youtube(url))
        if results:
            st.success(f"Found {len(results)} comments!")
            st.dataframe(pd.DataFrame(results))
        else:
            st.error("No comments found. Ensure the video is public.")
