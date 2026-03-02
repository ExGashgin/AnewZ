def get_tiktok_comments(url):
    if not str(url).strip().startswith("http"):
        st.error(f"❌ '{url[:30]}...' is not a link.")
        return None

    ydl_opts = {
        'getcomments': True, 
        'skip_download': True, 
        'quiet': True,
        'extract_flat': True,
        # Force yt-dlp to look like a specific browser version
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'referer': 'https://www.tiktok.com/',
        # Use a configuration that helps bypass JS challenges
        'extractor_args': {'tiktok': {'impersonate': 'chrome'}}, 
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We use extract_info but specifically target comment metadata
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            
            if not comments:
                return "Empty" 
                
            return [{
                "Author": c.get('author'), 
                "Text": c.get('text'), 
                "Category": get_sentiment(c.get('text')), 
                "Video_URL": url
            } for c in comments]
    except Exception as e:
        # If blocked, we show a helpful error instead of just "No Data"
        st.warning(f"⚠️ TikTok Blocked the Scraper. This is common on cloud hosts.")
        return None
