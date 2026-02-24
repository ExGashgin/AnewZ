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
async def scrape_youtube(url, max_comments=300):
    chrome_path = get_chrome_path()
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=chrome_path, headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")

        # Scroll to comments section initially
        await page.mouse.wheel(0, 1000)
        await asyncio.sleep(2)

        prev_height = 0
        reached_end = False
        all_comments = []

        while len(all_comments) < max_comments:
            # Scroll to the current bottom of the page
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2) # Wait for new comments to "pop in"

            # Check if the page height has changed
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == prev_height:
                # If height didn't change, we might be at the very bottom
                break
            prev_height = new_height

            # Extract currently visible comments
            comments = await page.locator("#content-text").all_inner_texts()
            authors = await page.locator("#author-text").all_inner_texts()
            
            # Update our list (using a dict to avoid duplicates)
            current_batch = [{"Author": a, "Comment": c} for a, c in zip(authors, comments)]
            all_comments = current_batch # Locator grabs everything currently in the DOM
            
            # Stop if we hit the limit
            if len(all_comments) >= max_comments:
                break
                
        await browser.close()
        return all_comments[:max_comments], None

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
