import streamlit as st
import asyncio
from playwright.async_api import async_playwright
import pandas as pd

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
