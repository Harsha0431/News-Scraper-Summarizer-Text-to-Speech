from comparative_analysis import compare_sentiments
from text_to_speech import generate_audio
from model import fetch_news
import pprint
import gradio as gr
import time


def get_news_summary_sentiment(company, max_articles=10, skip=0, use_gemini=False):
    articles = fetch_news(company, max_articles, skip, use_gemini=use_gemini)

    if len(articles) == 0:
        return articles, {}

    articles, summary = compare_sentiments(articles)

    return articles, summary


def display_news(articles):
    with gr.Blocks() as news_block:
        with gr.Column():
            for news in articles:
                with gr.Row():
                    gr.Markdown(f"### {news['Title']}")
                with gr.Row():
                    gr.TextArea(value=news['Summary'], interactive=False)
                with gr.Row():
                    gr.Audio(label="Article audio summary in Hindi", value=news['Audio'], autoplay=False)

    return news_block


def analyze_company(company, max_articles=10, skip=0, use_gemini=False):
    if len(company) < 3:
        return ("Company name must be at least 3 characters long.", "Company name must be at least 3 characters long.",
                None)

    use_gemini = use_gemini == "Yes"

    if use_gemini:
        if max_articles > 5:
            max_articles = 5
    else:
        if max_articles > 10:
            max_articles = 10

    articles, sentiment_summary = get_news_summary_sentiment(company, max_articles, skip=skip, use_gemini=use_gemini)

    if len(articles) == 0:
        return "Sorry, no article found at the movement.", "Sorry, no article found at the movement.", None

    sentiment_summary_text = (f"Positive: {sentiment_summary['Positive']}, Negative: {sentiment_summary['Negative']}, "
                              f"Neutral: {sentiment_summary['Neutral']}")

    for article in articles:
        time.sleep(1)
        article['Audio'] = generate_audio(article['Summary'])

    audio_file = generate_audio(sentiment_summary_text)

    return articles, sentiment_summary_text, audio_file
