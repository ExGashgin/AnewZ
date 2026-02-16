from newspaper import Article
# ... rest of your code

from newspaper import Article, Config, ArticleException

# 1. Setup Configuration (The "Fake Identity")
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
config = Config()
config.browser_user_agent = user_agent
config.request_timeout = 10  # Don't wait forever if the site is slow

# 2. Use the real URL you found
url = 'https://anewz.tv/region/south-caucasus/18124/president-of-azerbaijan-ilham-aliyev-concludes-serbia-visit/news'

article = Article(url, config=config)

try:

    print("--- Starting Download ---")
    article.download()
    
    print("--- Starting Parse ---")
    article.parse()
    
    # NLP requires the 'punkt' dataset we downloaded earlier
    print("--- Starting NLP ---")
    article.nlp()

    # 3. Output the data
    print(f"\nSUCCESS!")
    print(f"Title: {article.title}")
    print(f"Authors: {article.authors}")
    print(f"Keywords: {article.keywords[:5]}") # Print first 5 keywords
    print(f"Summary: {article.summary[:100]}...") # Print a snippet

except ArticleException as e:
    print(f"\nFAILED: The website blocked us or the link is dead.")
    print(f"Error details: {e}")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")
