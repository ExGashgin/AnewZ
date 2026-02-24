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
async def scrape_youtube(url, target_count=300):
    chrome_path = get_chrome_path()
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=chrome_path, headless=True)
        page = await browser.new_page()
        
        await page.goto(url, wait_until="networkidle")
        
        # 1. Initial scroll to find the comment section
        await page.evaluate("window.scrollTo(0, 800)")
        await asyncio.sleep(2)
        
        all_comments = []
        last_height = await page.evaluate("document.documentElement.scrollHeight")
        
        while len(all_comments) < target_count:
            # 2. Scroll to the current bottom
            await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
            
            # 3. Wait for the new batch of comments to load
            await asyncio.sleep(2) 
            
            # 4. Extract what is currently on screen
            # We use a set or dict here to ensure we don't save the same comment twice
            comments = await page.locator("#content-text").all_inner_texts()
            authors = await page.locator("#author-text").all_inner_texts()
            
            current_batch = [{"Author": a, "Comment": c} for a, c in zip(authors, comments)]
            all_comments = current_batch # Locator always returns the full list in the DOM
            
            # 5. Check if we've actually reached the very bottom
            new_height = await page.evaluate("document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
            if len(all_comments) >= target_count:
                break

        await browser.close()
        return all_comments[:target_count], None

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
