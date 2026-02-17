import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Video Content Intelligence", page_icon="🎬", layout="wide")

# 1. GENRE BRAIN (Same logic, now applied to Titles)
GENRE_MAP = {
    "World": ["un", "nato", "global", "international", "world", "foreign", "diplomacy"],
    "Politics": ["election", "president", "minister", "parliament", "government", "protest"],
    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank", "dollar"],
    "Sports": ["football", "goal", "match", "league", "win", "player", "tournament"],
    "Technology": ["ai", "tech", "software", "google", "meta", "cyber", "robot"],
    "Region": ["baku", "caucasus", "tbilisi", "karabakh", "central asia"]
}

def detect_genre(text):
    if not text or pd.isna(text):
        return "Not_specified"
    text_lower = str(text).lower()
    for genre, keywords in GENRE_MAP.items():
        if any(word in text_lower for word in keywords):
            return genre
    return "General"

def extract_hashtags(text):
    if not text or pd.isna(text):
        return "Not_specified"
    tags = re.findall(r"#(\w+)", str(text))
    return ", ".join(tags) if tags else "Not_specified"

# 2. UI INTERFACE
st.title("🎬 Video Title & Content Categorizer")
st.info("Paste your Video Titles below or upload a CSV file to categorize your content.")

input_method = st.radio("Choose Input Method:", ["Paste Titles", "Upload CSV"])

results = []

if input_method == "Paste Titles":
    titles_input = st.text_area("Paste Video Titles (one per line):", height=300)
    if st.button("🚀 Process Titles"):
        lines = [line.strip() for line in titles_input.split('\n') if line.strip()]
        for line in lines:
            results.append({
                "Genre": detect_genre(line),
                "Hashtags": extract_hashtags(line),
                "Video_Title": line
            })

else:
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        df_input = pd.read_csv(uploaded_file)
        
        # UPDATED: Looking for Video Title specifically
        # It will check for 'video title', 'title', 'headline', or 'description'
        col_name = next((c for c in df_input.columns if c.lower() in 
                         ['video title', 'title', 'headline', 'description', 'text']), None)
        
        if col_name:
            st.success(f"Detected column: **{col_name}**")
            if st.button("🚀 Process File"):
                df_input['Genre'] = df_
