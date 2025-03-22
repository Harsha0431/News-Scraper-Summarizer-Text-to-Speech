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
        if max_articles > 3:
            max_articles = 3
    else:
        if max_articles > 10:
            max_articles = 10

    # articles, sentiment_summary = get_news_summary_sentiment(company, max_articles, skip=skip, use_gemini=use_gemini)

    articles = [{'Sentiment': 'Positive',
                 'Summary': 'Hindustan Construction Company-Tata Projects JV wins Rs 2,191 '
                            'crore contract. JV will be owned by Hindaland Construction '
                            'Company and Tata Projects. Package IN-05R is first and only '
                            'underground segment of the 31.32-km Indore Metro Phase 1 '
                            'project.',
                 'Title': 'Hindustan Construction Company-Tata Projects JV wins Rs 2,191 '
                          'crore contract',
                 'URL': 'https://m.economictimes.com/news/company/corporate-trends/hindustan-construction-company-tata-projects-jv-wins-rs-2191-crore-contract/articleshow/119104071.cms'},
                {'Sentiment': 'Positive',
                 'Summary': 'Lendbox, a peer-to-peer (P2P) non-banking financial company '
                            '(NBFC), has secured the top spot in this prestigious list. '
                            'Founded in 2015, Lendbox is just 10 years old but has rapidly '
                            'climbed the ranks. India stands out with 81 companies in the '
                            'list, which highlights firms achieving significant revenue '
                            'growth between 2020 and 2023.',
                 'Title': 'This new company overtook Ratan Tatas company, Aditya Birlas '
                          'group, secures spot in top 500 of..., grew by more than 500% '
                          'per...',
                 'URL': 'https://www.india.com/business/this-new-company-overtook-ratan-tata-aditya-birlas-group-secures-spot-in-top-500-of-high-growth-asia-pacific-companiesgrew-by-more-than-500-percent-per-year-7694678/'},
                {'Sentiment': 'Neutral',
                 'Summary': 'Tata Play is a joint venture between Tata Sons and Tata Group. '
                            'Tata Play is one of the leading content distribution platforms '
                            'providing Pay TV and Over-the-top (OTT) services. As of '
                            'September last year, Tata Play and Airtel Digital TV accounted '
                            'for more than 35 million paid subscribers.',
                 'Title': 'Tata Sons gets CCI clearance to acquire additional 10% stake in '
                          'Tata Play',
                 'URL': 'https://www.etnownews.com/companies/tata-sons-gets-cci-clearance-to-acquire-additional-10-in-tata-play-article-119122993'}]

    sentiment_summary = {
        "Positive": 1,
        "Negative": 0,
        "Neutral": 2
    }

    if len(articles) == 0:
        return "Sorry, no article found at the movement.", "Sorry, no article found at the movement.", None

    sentiment_summary_text = (f"Positive: {sentiment_summary['Positive']}, Negative: {sentiment_summary['Negative']}, "
                              f"Neutral: {sentiment_summary['Neutral']}")

    for article in articles:
        time.sleep(1)
        article['Audio'] = generate_audio(article['Summary'])

    audio_file = generate_audio(sentiment_summary_text)

    return articles, sentiment_summary_text, audio_file
