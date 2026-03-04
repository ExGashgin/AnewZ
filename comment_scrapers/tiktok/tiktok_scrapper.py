import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 1. Initialize the VADER analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment_category(text):
    """Categorizes text based on VADER compound score."""
    if not text or pd.isna(text):
        return "Neutral"
    
    # Calculate sentiment scores
    scores = analyzer.polarity_scores(str(text))
    compound = scores['compound']
    
    # Standard VADER thresholds
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# 2. Example: Loading your Apify dataset
# Replace 'apify_comments.csv' with your actual file or DataFrame
df = pd.read_csv('apify_comments.csv')

# 3. Add the 'Category' column
# Ensure the column name matches your data (usually 'content' or 'text')
df['Category'] = df['text'].apply(get_sentiment_category)

# 4. Display or save results
print(df[['text', 'Category']].head())
df.to_csv('categorized_comments.csv', index=False)
