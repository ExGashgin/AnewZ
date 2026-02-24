import streamlit as st
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import shutil


# Check where Chromium is
def check_environment():
    paths = ["/usr/bin/chromium", "/usr/bin/chromium-browser", shutil.which("chromium")]
    found = [p for p in paths if p and os.path.exists(p)]
    return found[0] if found else None

chrome_path = check_environment()

if not chrome_path:
    st.error("❌ Chromium is STILL missing.")
    st.info("Check your deployment logs (bottom right of the Streamlit screen). Look for any errors during the 'Apt dependencies' stage.")
else:
    st.success(f"✅ Chromium found at: {chrome_path}")
    
    # Simple test run
    if st.button("Run Test Scrape"):
        async def test():
            async with async_playwright() as p:
                browser = await p.chromium.launch(executable_path=chrome_path, headless=True)
                page = await browser.new_page()
                await page.goto("https://www.google.com")
                title = await page.title()
                await browser.close()
                return title
        
        res = asyncio.run(test())
        st.write(f"Browser successfully opened! Page title: {res}")


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
