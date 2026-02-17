import streamlit as st
import pandas as pd
import re

# Set page layout
st.set_page_config(page_title="Video Content Intelligence", page_icon="🎬", layout="wide")

# 1. THE GENRE BRAIN
# Define categories and keywords
GENRE_MAP = {
    "World": ["un", "nato", "global", "international", "world", "foreign", "diplomacy"],
    "Politics": ["election", "president", "minister", "parliament", "government", "protest"],
    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank", "dollar"],
    "Sports": ["football", "goal", "match", "league", "win", "player", "tournament"],
    "Technology": ["ai", "tech", "software", "google", "meta", "cyber", "robot"],
    "Region": ["baku", "caucasus", "tbilisi", "karabakh", "central asia"]
}

def detect_genre(text):
    """Categorizes text based on keywords."""
    if not text or pd.isna(text):
        return "Not_specified"
    text_lower = str(text).lower()
    for genre, keywords in GENRE_MAP.items():
        if any(word in text_lower for word in keywords):
            return genre
    return "General"

def extract_hashtags(text):
    """Pulls all #hashtags from a string."""
    if not text or pd.isna(text):
        return "Not_specified"
    tags = re.findall(r"#(\w+)", str(text))
    return ", ".join(tags) if tags else "Not_specified"

# 2. USER INTERFACE
st.title("🎬 Video Title & Genre Categorizer")
st.info("Paste your Video Titles or upload a CSV to automatically detect Genres and Hashtags.")

# Choose input method
input_method = st.radio("Choose Input Method:", ["Paste Titles", "Upload CSV"])

# Initialize results list
results_data = []

# --- METHOD A: PASTE TITLES ---
if input_method == "Paste Titles":
    titles_input = st.text_area("Paste Video Titles (one per line):", height=300)
    
    if st.button("🚀 Process Titles"):
        lines = [line.strip() for line in titles_input.split('\n') if line.strip()]
        if lines:
            for line in lines:
                results_data.append({
                    "Video_Title": line,
                    "Genre": detect_genre(line),
                    "Hashtags": extract_hashtags(line)
                })
            
            # Create DataFrame
            df_final = pd.DataFrame(results_data)
            
            # Display stats
            st.subheader("Results Summary")
            st.table(df_final['Genre'].value_counts())
            
            # Show Data
            st.dataframe(df_final, use_container_width=True)
            
            # Download Button
            csv_data = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv_data, "video_titles.csv", "text/csv")
        else:
            st.warning("Please enter some titles first.")

# --- METHOD B: UPLOAD CSV ---
else:
    uploaded_file = st.file_uploader("Upload your CSV file:", type="csv")
    
    if uploaded_file:
        df_input = pd.read_csv(uploaded_file)
        
        # Look for the best column to use for titles
        possible_cols = ['video title', 'title', 'headline', 'description', 'text']
        col_name = next((c for c in df_input.columns if c.lower() in possible_cols), None)
        
        if col_name:
            st.success(f"Found column: **{col_name}**")
            
            if st.button("🚀 Process File"):
                # Apply the logic to the detected column
                df_input['Genre'] = df_input[col_name].apply(detect_genre)
                df_input['Hashtags'] = df_input[col_name].apply(extract_hashtags)
                
                # Show results
                st.subheader("Genre Distribution")
                st.table(df_input['Genre'].value_counts())
                
                st.dataframe(df_input, use_container_width=True)
                
                # Download Button
                processed_csv = df_input.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Processed CSV", processed_csv, "processed_videos.csv", "text/csv")
        else:
            st.error("Could not find a Title or Description column. Please check your CSV headers.")
