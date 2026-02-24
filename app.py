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
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=chrome_path, headless=True)
        # Use a mobile-like user agent to get a lighter, faster-loading page
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()
        
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
        # 1. Scroll down gradually to trigger the comment section
        for _ in range(3):
            await page.mouse.wheel(0, 800)
            await asyncio.sleep(1)
        
        # 2. Wait for the specific comment container to appear
        try:
            # YouTube comments are inside a ytd-item-section-renderer
            await page.wait_for_selector("#content-text", timeout=15000)
        except:
            return None, "Timed out waiting for comments. Try a different video URL."

        # 3. Pull all comments currently loaded
        comment_elements = await page.locator("#content-text").all_inner_texts()
        
        await browser.close()
        return [{"Comment": c} for c in comment_elements], None

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
