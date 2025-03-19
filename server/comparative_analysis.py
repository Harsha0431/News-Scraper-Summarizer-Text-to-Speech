from sentiment_analysis import analyze_sentiment


def compare_sentiments(articles):
    summary = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for article in articles:
        sentiment = analyze_sentiment(article["title"])
        summary[sentiment] += 1
    return summary

