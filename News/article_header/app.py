import streamlit as st
import pandas as pd
from newspaper import Article, Config
import nltk
import time

# 1. Page Setup
st.set_page_config(page_title="News Genre Extractor", page_icon="📂", layout="wide")

@st.cache_resource
def load_nltk():
    try:
        nltk.download('punkt')
        nltk.download('punkt_tab')
    except:
        pass

load_nltk()

st.title("📂 News Path & Genre Extractor")
st.write("Extract metadata and automatically detect the news genre from the URL path.")

# 2. INPUT SECTION
col_a, col_b = st.columns([1, 2])

with col_a:
    base_url = st.text_input("Base Domain:", value="https://anewz.tv")

with col_b:
    paths_text = st.text_area("Paste Page Paths:", 
                              height=150, 
                              placeholder="/region/south-caucasus/article-123\n/economy/global/article-456")

# 3. EXTRACTION LOGIC
if st.button("Extract Data & Detect Genre"):
    base_url = base_url.strip().rstrip('/')
    path_list = [p.strip() for p in paths_text.split('\n') if p.strip()]
    
    if path_list:
        results = []
        progress_bar = st.progress(0)
        
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36'
        
        for i, path in enumerate(path_list):
            clean_path = path if path.startswith('/') else '/' + path
            full_url = f"{base_url}{clean_path}"
            
            # --- GENRE DETECTION LOGIC ---
            # We split the path by '/' and take the first real word
            # Example: /region/south-caucasus/ -> [' ', 'region', 'south-caucasus']
            path_parts = [part for part in clean_path.split('/') if part]
            detected_genre = path_parts[0].capitalize() if path_parts else "General"
            
            try:
                article = Article(full_url, config=config)
                article.download()
                article.parse()
                article.nlp()
                
                results.append({
                    "Genre": detected_genre, # The new column
                    "Title": article.title,
                    "Author": ", ".join(article.authors) if article.authors else "N/A",
                    "Date": article.publish_date,
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
            st.success(f"Successfully processed {len(results)} articles!")
            df = pd.DataFrame(results)
            
            # Show a summary count of genres
            st.subheader("Articles by Genre")
            st.bar_chart(df['Genre'].value_counts())
            
            # Show the main table
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download All as CSV", csv, "news_with_genres.csv", "text/csv")
    else:
        st.warning("Please enter at least one path.")
