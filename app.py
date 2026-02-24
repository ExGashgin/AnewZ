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
        # Using a desktop User-Agent to ensure we get the standard layout
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # --- POP-UP KILLER ---
            # Wait a moment for any consent dialogs to appear
            await asyncio.sleep(2)
            # This looks for 'Accept all', 'I agree', or 'Reject all' buttons
            consent_buttons = ["Accept all", "I agree", "Allow all", "Reject all"]
            for text in consent_buttons:
                button = page.get_by_role("button", name=text, exact=False).first
                if await button.is_visible():
                    await button.click()
                    await asyncio.sleep(1) # Wait for pop-up to disappear
                    break

            # --- TRIGGER COMMENTS ---
            # YouTube won't load comments until you scroll down
            await page.evaluate("window.scrollTo(0, 800)")
            await asyncio.sleep(2)
            
            # Wait for the comment section to load (ID is usually #comments)
            await page.wait_for_selector("#content-text", timeout=15000)
            
            # Pull the data
            comment_elements = await page.locator("#content-text").all_inner_texts()
            authors = await page.locator("#author-text").all_inner_texts()
            
            await browser.close()
            
            results = [{"Author": a.strip(), "Comment": c.strip()} for a, c in zip(authors, comment_elements)]
            return results, None

        except Exception as e:
            # Take a screenshot if it fails so we can see what the bot sees
            await page.screenshot(path="error_screen.png")
            await browser.close()
            return None, f"Scrape failed. Bot was stuck at a screen. Details: {str(e)}"

# In your UI section, add this so you can see the error screenshot
if 'error_screen.png' in os.listdir():
    st.image("error_screen.png", caption="What the bot saw when it failed")

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
