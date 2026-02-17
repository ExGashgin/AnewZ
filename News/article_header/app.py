import streamlit as st
import pandas as pd
from newspaper import Article, Config
import nltk
import time

# 1. Page Setup
st.set_page_config(page_title="Path-Based Extractor", page_icon="🔗", layout="wide")

@st.cache_resource
def load_nltk():
    try:
        nltk.download('punkt')
        nltk.download('punkt_tab')
    except:
        pass

load_nltk()

st.title("🔗 News Path Extractor")
st.write("Combine a Base Domain with multiple Page Paths to extract data in bulk.")

# 2. INPUT SECTION
col_a, col_b = st.columns([1, 2])

with col_a:
    base_url = st.text_input("Base Domain:", value="https://anewz.tv", help="The website homepage (include https://)")

with col_b:
    paths_text = st.text_area("Paste Page Paths (one per line):", 
                              height=150, 
                              placeholder="/news/article-1\n/region/article-2",
                              help="The part of the URL that comes after the .com or .tv")

# 3. EXTRACTION LOGIC
if st.button("Generate URLs and Extract"):
    # Clean the base URL (remove trailing slash)
    base_url = base_url.strip().rstrip('/')
    
    # Clean the paths and combine them
    path_list = [p.strip() for p in paths_text.split('\n') if p.strip()]
    
    if path_list:
        results = []
        progress_bar = st.progress(0)
        
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36'
        
        for i, path in enumerate(path_list):
            # Ensure path starts with a slash
            clean_path = path if path.startswith('/') else '/' + path
            full_url = f"{base_url}{clean_path}"
            
            try:
                article = Article(full_url, config=config)
                article.download()
                article.parse()
                article.nlp()
                
                results.append({
                    "Path": clean_path,
                    "Title": article.title,
                    "Author": ", ".join(article.authors) if article.authors else "N/A",
                    "Keywords": ", ".join(article.keywords[:5]),
                    "Summary": article.summary[:150] + "...",
                    "Full URL": full_url
                })
            except Exception as e:
                st.error(f"Error on path {clean_path}: {e}")
            
            progress_bar.progress((i + 1) / len(path_list))
            time.sleep(0.3)

        # 4. RESULTS DISPLAY
        if results:
            st.success(f"Successfully processed {len(results)} paths!")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download All as CSV", csv, "path_extraction.csv", "text/csv")
    else:
        st.warning("Please enter at least one path.")
