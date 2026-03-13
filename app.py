import newsapi
import pywhatkit
import schedule
import time
from datetime import datetime

# Setup your API Key
newsapi_client = newsapi.NewsApiClient(api_key='YOUR_NEWS_API_KEY')

def fetch_top_5(country_code, country_name):
    """Fetches top 5 headlines for a specific country."""
    top_headlines = newsapi_client.get_top_headlines(country=country_code, language='en', page_size=5)
    articles = top_headlines.get('articles', [])
    
    report = f"\n{country_name} Top 5:\n"
    for i, art in enumerate(articles, 1):
        report += f"{i}. {art['title']}\n"
    return report

def get_morning_briefing():
    print(f"Generating report for {datetime.now().strftime('%Y-%m-%d %H:%M')}...")
    
    # 1. Gather Data
    report = "🌅 *Your 8:00 AM News Briefing* 🌅\n"
    report += fetch_top_5('az', '🇦🇿 Azerbaijan')
    report += fetch_top_5('tr', '🇹🇷 Turkey')
    
    # Global Trends
    global_news = newsapi_client.get_top_headlines(language='en', page_size=5)
    report += "\n🌍 Global Top 5:\n"
    for i, art in enumerate(global_news.get('articles', []), 1):
        report += f"{i}. {art['title']}\n"
        
    # 2. Send via WhatsApp
    # Note: Replace with your phone number including country code
    # wait_time=15 gives the web browser time to load
    pywhatkit.sendwhatmsg_instantly("+994XXXXXXXXX", report, wait_time=15, tab_close=True)
    print("Message sent!")

# 3. Schedule for 08:00 AM
schedule.every().day.at("08:00").do(get_morning_briefing)

print("Automated News Bot is running... waiting for 08:00 AM.")
while True:
    schedule.run_pending()
    time.sleep(60) # Check every minute
