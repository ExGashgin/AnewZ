import streamlit as st
import pandas as pd
from newspaper import Article, Config, ArticleException
import nltk
import time

# 1. Page Setup
st.set_page_config(page_title="Bulk News Extractor", page_icon="📰", layout="wide")

@st.cache_resource
def load_nltk():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
        nltk.download('punkt_tab')

load_nltk()

st.title("📰 Bulk News Data Scraper")
st.write("Paste multiple URLs below (one per line) to extract data for all of them at once.")

# 2. THE MULTI-LINE BOX
# We use text_area instead of text_input
urls_text = st.text_area("Paste News URLs here (one per line):", height=200, placeholder="https://anewz.tv/link1\nhttps://reuters.com/link2")

# 3. EXTRACTION LOGIC
if st.button("Extract All Articles"):
    # Split the text by new lines and remove empty lines or extra spaces
    url_list = [url.strip() for url in urls_text.split('\n') if url.strip()]
    
    if url_list:
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Setup Configuration
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36'
        config.request_timeout = 10

        # Loop through each URL
        for i, url in enumerate(url_list):
            try:
                status_text.text(f"Processing ({i+1}/{len(url_list)}): {url[:50]}...")
                
                article = Article(url, config=config)
                article.download()
                article.parse()
                article.nlp()
                
                results.append({
                    "Title": article.title,
                    "Author": ", ".join(article.authors) if article.authors else "N/A",
                    "Date": article.publish_date,
                    "Keywords": ", ".join(article.keywords[:5]),
                    "Summary": article.summary[:150] + "...", # Short snippet for the table
                    "URL": url
                })
            except Exception as e:
                st.error(f"Error skipping {url}: {e}")
            
            # Update progress bar
            progress_bar.progress((i + 1) / len(url_list))
            time.sleep(0.5) # Slight delay to be "polite" to servers

        # 4. DISPLAY RESULTS IN A TABLE
        if results:
            st.success(f"Successfully extracted {len(results)} articles!")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)

            # 5. DOWNLOAD BUTTON
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name='bulk_news_data.csv',
                mime='text/csv',
            )
        status_text.text("Extraction Complete!")
    else:
        st.warning("Please paste at least one URL.")
