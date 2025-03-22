import os
import re
import markdown
import threading
from text_to_speech import clean_old_audio
from dotenv import load_dotenv
import io

load_dotenv()


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
