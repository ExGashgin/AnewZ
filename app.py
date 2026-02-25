import requests
import re

def get_tiktok_comments_free(url):
    # This tries to extract the Video ID from the URL
    video_id = re.findall(r'video/(\d+)', url)
    if not video_id:
        st.error("Invalid TikTok URL format.")
        return None
    
    # TikTok's internal comment API endpoint (Simplified example)
    # WARNING: This endpoint changes frequently in 2026
    api_url = f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id[0]}&count=20"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        comments = data.get('comments', [])
        return [{"Author": c['user']['nickname'], "Text": c['text'], "URL": url} for c in comments]
    else:
        st.error(f"TikTok blocked the request (Status: {response.status_code}).")
        return None
