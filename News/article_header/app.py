import streamlit as st
import pandas as pd
from newspaper import Article, Config, ArticleException
import nltk

# 1. Page Setup
st.set_page_config(page_title="Anewz News Extractor", page_icon="📰", layout="wide")

# Ensure NLTK data is available for NLP (Keywords/Summary)
@st.cache_resource
def load_nltk():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
        nltk.download('punkt_tab')

load_nltk()

# 2. Sidebar - App Info
with st.sidebar:
    st.title("Settings")
    st.info("This tool extracts titles, authors, keywords, and summaries from news URLs.")
    st.markdown("---")
    st.caption("Powered by Newspaper3k & Streamlit")

# 3. Main Interface
st.title("📰 News Data Scraper")
st.write("Enter a news article link below to extract professional metadata.")

url_input = st.text_input("News URL:", placeholder="https://anewz.tv/...")

# 4. Extraction Logic
if st.button("Extract Article Details"):
    if url_input:
        try:
            # Setup User-Agent to prevent 403 Forbidden blocks
            config = Config()
            config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36'
            config.request_timeout = 15

            # Progress Tracking
            with st.status("Fetching Article Data...", expanded=True) as status:
                article = Article(url_input, config=config)
                
                st.write("Downloading content...")
                article.download()
                
                st.write("Parsing HTML...")
                article.parse()
                
                st.write("Running NLP (Keywords & Summary)...")
                article.nlp()
                
                status.update(label="Extraction Successful!", state="complete", expanded=False)

            # 5. Displaying Results
            col1, col2 = st.columns([2, 1])

            with col1:
                st.header(article.title)
                st.write(f"**Authors:** {', '.join(article.authors) if article.authors else 'Not found'}")
                st.write(f"**Publish Date:** {article.publish_date if article.publish_date else 'N/A'}")
                
                st.subheader("Summary")
                st.write(article.summary)

            with col2:
                if article.top_image:
                    st.image(article.top_image, caption="Article Header Image")
                
                st.subheader("Top Keywords")
                st.info(", ".join(article.keywords[:10]))

            # 6. Data Export (CSV)
            st.markdown("---")
            data = {
                "Title": [article.title],
                "Authors": [", ".join(article.authors)],
                "Date": [str(article.publish_date)],
                "Summary": [article.summary],
                "URL": [url_input]
            }
            df = pd.DataFrame(data)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name='news_data.csv',
                mime='text/csv',
            )

        except ArticleException:
            st.error("The website blocked the scraper or the URL is invalid. Try a different link.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("Please paste a URL first!")
