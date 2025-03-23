import os
import re
import markdown
import threading
from text_to_speech import clean_old_audio, generate_audio
from dotenv import load_dotenv
from comparative_analysis import compare_sentiments
from model import fetch_news
import gradio as gr
import time

load_dotenv()


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


def get_news_ui_css():
    news_ui_css = """
    .center_items{
        display: flex;
        justify-content: center;
        align-items: center;
        place-items: center; 
    }
    
    .btn__get_news{
        width: fit-content !important;
    }
    
    .input_container{
        max-width: 840px;
    }
    """

    return news_ui_css


def markdown_to_plain_text(md_text):
    # Convert Markdown to HTML
    html_text = markdown.markdown(md_text)

    # Remove HTML tags
    plain_text = re.sub(r'<[^>]+>', '', html_text)

    # Replace multiple newlines with a single newline
    plain_text = re.sub(r'\n+', '\n', plain_text).strip()
    plain_text = re.sub(r'\*+', '', plain_text)

    return plain_text


#  Periodic cleaning (Clean audio files which are older than threshold hours)
def periodic_clean():
    PERIODIC_CLEAN_TIME_SECS = os.getenv("PERIODIC_CLEAN_TIME_SECS")

    if PERIODIC_CLEAN_TIME_SECS is None:
        PERIODIC_CLEAN_TIME_SECS = float(7200.0)

    try:
        if isinstance(PERIODIC_CLEAN_TIME_SECS, str):
            PERIODIC_CLEAN_TIME_SECS = float(PERIODIC_CLEAN_TIME_SECS)
    except ValueError:
        print("Warning: Invalid PERIODIC_CLEAN_TIME_SECS environment variable. Using default.")
        PERIODIC_CLEAN_TIME_SECS = 7200.0

    run_clean_audio_threaded()
    threading.Timer(interval=PERIODIC_CLEAN_TIME_SECS, function=periodic_clean).start()


def run_clean_audio_threaded():
    """Runs clean_old_audio in a separate thread."""
    thread = threading.Thread(target=clean_old_audio)
    thread.daemon = True
    thread.start()
