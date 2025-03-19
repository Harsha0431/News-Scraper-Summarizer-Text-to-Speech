from transformers import pipeline
import os


os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Load summarization model (BART is good for news articles)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def summarize_text(text, max_length=100, min_length=30):
    if len(text.split()) < 50:  # If text is too short, return as is
        return text

    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']
