from nltk.sentiment import SentimentIntensityAnalyzer

# Initialize SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(user_message):
    # Analyze the sentiment of the user message
    sentiment_score = sia.polarity_scores(user_message)['compound']
    
    # Return a numerical value to adjust the user sentiment
    # You can scale it if needed, for example:
    if sentiment_score >= 0.05:
        return 1  # Positive sentiment
    elif sentiment_score <= -0.05:
        return -1  # Negative sentiment
    else:
        return 0  # Neutral sentiment
