import os
import subprocess
import streamlit as st
import asyncio
from playwright.async_api import async_playwright
import pandas as pd

@st.cache_resource
# 1. Define a writable path for the browser
# Streamlit's /tmp directory is usually writable
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/tmp/playwright-browsers"

@st.cache_resource
def install_playwright_locally():
    try:
        # Install only Chromium to keep it lightweight
        subprocess.run(["python", "-m", "playwright", "install", "chromium"], check=True)
        # Note: We skip 'install-deps' here because Streamlit installs 
        # those via your packages.txt file automatically.
    except subprocess.CalledProcessError as e:
        st.error(f"Playwright installation failed. Error: {e}")

# Run the installer
install_playwright_locally()


2. Update your packages.txt (Root Folder)
Streamlit Cloud uses a Debian-based Linux. It needs these specific libraries to run a "headless" browser. Make sure your packages.txt has these exact names:

Plaintext
libnss3
libatk-bridge2.0-0
libgtk-3-0
libgbm1
libasound2
libxshmfence1
libglu1-mesa
3. Update the Scraper Launch
Because you moved the browser to /tmp/, you need to ensure Playwright knows where to look when you launch the browser:

Python
from playwright.async_api import async_playwright

async def run_scraper(url):
    async with async_playwright() as p:
        # Playwright will automatically look in the PLAYWRIGHT_BROWSERS_PATH 
        # environment variable we set at the top of the script.
        browser = await p.chromium.launch(headless=True)
        # ... rest of your code
Why this fixes the "Exit Status 1"
Permissions: By default, Playwright tries to install to ~/.cache/ms-playwright. On some Streamlit server instances, this path is restricted. Moving it to /tmp/ usually solves the permission block.

Dependencies: The error often stems from missing Linux "dependencies" (like libnss3). By adding them to packages.txt, Streamlit installs them before your Python code even runs, ensuring playwright install finds a healthy environment.

Would you like me to check your requirements.txt as well to make sure there are no version conflicts between Playwright and Streamlit?

Playwright Python Installation Guide

This video provides a foundational walkthrough of the Playwright installation process for Python, which is helpful for understanding the underlying commands your script is executing.

Playwright Python Installation | Step-by-Step Guide for Beginners - YouTube
Suresh SDET Automation · 311 views

# --- MUST BE AT THE TOP OF YOUR SCRIPT ---
def install_playwright_browsers():
    try:
        # Try to launch playwright to see if browsers are there
        from playwright.async_api import async_playwright
    except ImportError:
        # Install the playwright python package if somehow missing
        subprocess.run(["pip", "install", "playwright"])
    
    # Run the browser installation
    # We only install chromium to save time and space on the server
    subprocess.run(["python", "-m", "playwright", "install", "chromium"])
    subprocess.run(["python", "-m", "playwright", "install-deps"])

# Run the installer
if 'browsers_installed' not in st.session_state:
    with st.spinner("Setting up browser engines... this only happens once."):
        install_playwright_browsers()
        st.session_state['browsers_installed'] = True


# Function to scrape YouTube (The easiest one)
async def scrape_youtube(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        # Scroll to trigger comment loading
        await page.evaluate("window.scrollTo(0, 1000)")
        await page.wait_for_selector("ytd-comment-thread-renderer", timeout=10000)
        
        comments = await page.locator("#content-text").all_inner_texts()
        authors = await page.locator("#author-text").all_inner_texts()
        
        await browser.close()
        return [{"Author": a, "Comment": c} for a, c in zip(authors, comments)]

# UI Setup
st.title("🚀 Universal Social Scraper 2026")
platform = st.selectbox("Select Platform", ["YouTube", "Instagram", "TikTok", "Facebook"])
url = st.text_input("Paste the Post URL here:")

if st.button("Start Scraping"):
    if not url:
        st.error("Please enter a URL!")
    else:
        with st.spinner(f"Scraping {platform}..."):
            try:
                if platform == "YouTube":
                    data = asyncio.run(scrape_youtube(url))
                else:
                    st.warning(f"{platform} requires advanced proxies. Showing YouTube demo logic.")
                    data = [] # Placeholder for other platform logic
                
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                    st.download_button("Download CSV", df.to_csv(index=False), "comments.csv")
                else:
                    st.error("No data found. The page might be protected.")
            except Exception as e:
                st.error(f"Error: {e}")
