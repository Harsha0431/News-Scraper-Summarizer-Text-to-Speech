from sentiment_analysis import analyze_sentiment


def compare_sentiments(articles):
    summary = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for article in articles:
        sentiment = analyze_sentiment("".join(f" {article['Title']} - ").join(article["Summary"]))
        article["Sentiment"] = sentiment
        summary[sentiment] += 1
    return articles, summary
