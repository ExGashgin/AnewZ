import streamlit as st
import pandas as pd
import re

# Set page layout
st.set_page_config(page_title="Path Intelligence Dashboard", page_icon="🔗", layout="wide")

# 1. THE GENRE BRAIN
GENRE_MAP = {
    "World": ["un", "nato", "global", "international", "world", "foreign", "diplomacy"],
    "Politics": ["election", "president", "minister", "parliament", "government", "protest"],
    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank", "dollar"],
    "Sports": ["football", "goal", "match", "league", "win", "player", "tournament"],
    "Technology": ["ai", "tech", "software", "google", "meta", "cyber", "robot"],
    "Region": ["baku", "caucasus", "tbilisi", "karabakh", "central asia"]
}

def clean_path(path_text):
    """Removes slashes, hyphens, and extensions to make paths readable."""
    if not path_text or pd.isna(path_text):
        return ""
    # Replace common URL separators with spaces
    clean = re.sub(r'[/_\-.]', ' ', str(path_text))
    return clean

def detect_genre(text):
    """Categorizes text based on keywords."""
    if not text:
        return "Not_specified"
    
    # We clean the path before checking keywords
    readable_text = clean_path(text).lower()
    
    for genre, keywords in GENRE_MAP.items():
        if any(word in readable_text for word in keywords):
            return genre
    return "General"

# 2. USER INTERFACE
st.title("🔗 URL Path & Genre Categorizer")
st.info("Paste your URL Paths or upload a CSV to automatically detect Genres based on the URL structure.")

# Choose input method
input_method = st.radio("Choose Input Method:", ["Paste Paths", "Upload CSV"])

results_data = []

# --- METHOD A: PASTE PATHS ---
if input_method == "Paste Paths":
    paths_input = st.text_area("Paste Paths (one per line, e.g., /news/economy-update):", height=300)
    
    if st.button("🚀 Process Paths"):
        lines = [line.strip() for line in paths_input.split('\n') if line.strip()]
        if lines:
            for line in lines:
                results_data.append({
                    "Original_Path": line,
                    "Cleaned_Words": clean_path(line), # Shows you what the AI 'read'
                    "Genre": detect_genre(line)
                })
            
            df_final = pd.DataFrame(results_data)
            st.subheader("Results Summary")
            st.table(df_final['Genre'].value_counts())
            st.dataframe(df_final, use_container_width=True)
            
            csv_data = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv_data, "path_genres.csv", "text/csv")

# --- METHOD B: UPLOAD CSV ---
else:
    uploaded_file = st.file_uploader("Upload your CSV file:", type="csv")
    
    if uploaded_file:
        df_input = pd.read_csv(uploaded_file)
        
        # Look for 'path', 'url', 'slug', or 'permalink'
        possible_cols = ['path', 'url', 'slug', 'permalink', 'link', 'video title']
        col_name = next((c for c in df_input.columns if c.lower() in possible_cols), None)
        
        if col_name:
            st.success(f"Detected Path column: **{col_name}**")
            
            if st.button("🚀 Process File"):
                df_input['Genre'] = df_input[col_name].apply(detect_genre)
                
                st.subheader("Genre Distribution")
                st.table(df_input['Genre'].value_counts())
                st.dataframe(df_input, use_container_width=True)
                
                processed_csv = df_input.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Processed CSV", processed_csv, "processed_paths.csv", "text/csv")
        else:
            st.error("Could not find a Path, URL, or Slug column. Please check your CSV headers.")
