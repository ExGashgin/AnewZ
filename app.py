import streamlit as st
import yt_dlp
import os
from yt_dlp.networking.impersonate import ImpersonateTarget

def scrape_tiktok_final(url):
    cookie_file = "tiktok_cookies.txt"
    
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'extract_flat': False,
        'cookiefile': cookie_file,
        # Mandatory for 2026: Mimic a real Chrome browser handshake
        'impersonate': ImpersonateTarget.from_str('chrome'),
        'http_headers': {
            # Replace this with your actual browser's User-Agent if 403 persists
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'extractor_args': {
            'tiktok': {
                'api_hostname': 'api22-normal-c-useast2a.tiktokv.com',
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We use extract_info to trigger the JS challenge solver
            info = ydl.extract_info(url, download=False)
            return info.get('comments', [])
    except Exception as e:
        return f"ERROR: {str(e)}"
