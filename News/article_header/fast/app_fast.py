import streamlit as st
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Velo-Genre Extractor", page_icon="🏎️", layout="wide")

# 1. EXPANDED GENRE BRAIN (Prioritized from top to bottom)
GENRE_MAP = {
    "World": ["un", "nato", "global", "international", "world", "foreign", "diplomacy", "summit"],
    "Politics": ["election", "president", "minister", "parliament", "government", "protest", "policy"],
    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank", "dollar", "crypto"],
    "Sports": ["football", "goal", "match", "league", "win", "player", "tournament", "fifa"],
    "Technology": ["ai", "tech", "software", "google", "meta", "cyber", "robot", "space"],
    "Health": ["virus", "health", "doctor", "medicine", "covid", "vaccine", "fitness"],
    "Region": ["baku", "caucasus", "tbilisi", "karabakh", "central asia", "yerevan"]
}

def detect_genre(text):
    if not text or text == "Not_specified": return "Not_specified"
    text_lower = text.lower()
    for genre, keywords in GENRE_MAP.items():
        if any(word in text_lower for word in keywords):
            return genre
    return "General"

# 2. SLIM EXTRACTION ENGINE (Metadata Only)
def fast_extract(url):
    # Using a modern User-Agent to prevent basic blocks
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0"}
    try:
        # TIKTOK/YOUTUBE FAST PATH: Use official oEmbed APIs
        if "tiktok.com" in url or "youtube.com" in url or "youtu.be" in url:
            api = f"https://www.tiktok.com/oembed?url={url}" if "tiktok" in url else f"https://www.youtube.com/oembed?url={url}&format=json"
            data = requests.get(api, timeout=3).json()
            content = data.get('title', 'Not_specified')
        else:
            # FACEBOOK/X/NEWS FAST PATH: Grab meta description only
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract only the "Preview text" which contains keywords
            meta = soup.find("meta", property="og:description")
