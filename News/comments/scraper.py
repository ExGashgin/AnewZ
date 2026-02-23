import nltk
nltk.download('vader_lexicon')
import yt_dlp
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import time

# --- 1. REUSE YOUR GENRE BRAIN ---
GENRE_MAP = {
    "World": ["un", "nato", "global", "international", "world", "foreign", "diplomacy"],
    "Politics": ["election", "president", "minister", "parliament", "government", "protest"],
    "Economy": ["oil", "gas", "price", "business", "market", "finance", "bank", "dollar"],
    "Sports": ["football", "goal", "match", "league", "win", "player", "tournament"],
    "Technology": ["ai", "tech", "software", "google", "meta", "cyber", "robot"],
    "Region": ["baku", "caucasus", "tbilisi", "karabakh", "central asia"]
}

sia = SentimentIntensityAnalyzer()

def analyze_comment(text):
    text_str = str(text).lower()
    # Detect Genre
    genre = "General"
    for g, keywords in GENRE_MAP.items():
        if any(word in text_str for word in keywords):
            genre = g
            break
    
    # Detect Sentiment
    score = sia.polarity_scores(text_str)['compound']
    label = "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
    
    return genre, score, label

# --- 2. MULTI-URL SCRAPER ENGINE ---
def scrape_and_categorize(urls):
    all_results = []
    
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'extractor_args': {'youtube': {'max_comments': ['all']}, 'tiktok': {'max_comments': ['all']}}
    }

    for url in urls:
        print(f"📡 Scraping: {url}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                comments = info.get('comments', [])
                video_title = info.get('title', 'Unknown Video')

                for c in comments:
                    comment_text = c.get('text')
                    if comment_text:
                        genre, score, label = analyze_comment(comment_text)
                        all_results.append({
                            "Video_Title": video_title,
                            "Comment": comment_text,
                            "Genre": genre,
                            "Sentiment_Score": score,
                            "Sentiment_Label": label,
                            "URL": url
                        })
            time.sleep(2) # Avoid getting blocked
        except Exception as e:
            print(f"❌ Error on {url}: {e}")

    return pd.DataFrame(all_results)

# --- 3. EXECUTION ---
url_list = [
    "PASTE_URL_1_HERE",
    "PASTE_URL_2_HERE"
]

if url_list[0] != "PASTE_URL_1_HERE":
    df_final = scrape_and_categorize(url_list)
    print(df_final.head())
    df_final.to_csv("analyzed_comments.csv", index=False)
    print("✅ Analysis Complete! File saved as analyzed_comments.csv")
