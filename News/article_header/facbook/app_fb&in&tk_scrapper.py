import streamlit as st
import pandas as pd
import re
import io

st.set_page_config(page_title="Text Intelligence Dashboard", page_icon="📝", layout="wide")

# 1. REFINED GENRE BRAIN (Specific & Smart)
GENRE_MAP = {

    "World": ["un", "nato", "global", "international", "world", "foreign", "diplomacy"],

    "Politics": ["election", "president", "minister", "parliament", "government", "protest"],

    "Conflict & Security": ["strike", "military", "targeted", "attack", "war", "conflict", "security", "base", "retaliatory", "clash"],

    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank", "dollar"],

    "Culture": ["cuisine", "art", "music", "festival", "tradition", "heritage", "food", "museum", "history", "cultural"],

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
st.title("📝 Post Text Categorizer")

input_method = st.radio("Choose Input Method:", ["Paste Text", "Upload CSV"])

results = []

if input_method == "Paste Text":
    texts_input = st.text_area("Paste Post Texts (one per line):", height=300)
    if st.button("🚀 Process Text"):
        lines = [line.strip() for line in texts_input.split('\n') if line.strip()]
        for line in lines:
            results.append({
                "Genre": detect_genre(line),
                "Hashtags": extract_hashtags(line),
                "Post_Text": line
            })

else:
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        try:
            # Try UTF-8-SIG first (handles Excel-generated CSVs with BOM)
            df_input = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        except:
            uploaded_file.seek(0)
            df_input = pd.read_csv(uploaded_file, encoding='latin1')
        
        # FIND THE TEXT COLUMN (Improved List)
        possible_names = ['description', 'text', 'post_text', 'content', 'caption', 'body', 'message']
        col_name = next((c for c in df_input.columns if c.lower() in possible_names), None)
        
        if col_name:
            # Create the results
            df_input['Genre'] = df_input[col_name].apply(detect_genre)
            df_input['Hashtags'] = df_input[col_name].apply(extract_hashtags)
            
            st.success(f"Found text in column: '{col_name}'")
            st.dataframe(df_input)
            
            csv = df_input.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Download Results", csv, "processed_data.csv", "text/csv")
        else:
            st.error(f"Could not find a text column. Your columns are: {list(df_input.columns)}")
            st.info("Tip: Rename your text column to 'Description' or 'Text' in Excel and re-upload.")

# 3. DISPLAY RESULTS (For Paste Method)
if results:
    df = pd.DataFrame(results)
    st.subheader("Genre Distribution")
    st.bar_chart(df['Genre'].value_counts())
    
    st.subheader("Processed Intelligence")
    st.dataframe(df, use_container_width=True)
    
    csv_paste = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Download Results (CSV)", csv_paste, "text_genres.csv", "text/csv")
