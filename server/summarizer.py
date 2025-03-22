import os
import pprint
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import textwrap
import unicodedata
import re
from google import genai
from dotenv import load_dotenv
from googletrans import Translator
import asyncio

load_dotenv()

model_name = "facebook/bart-large-cnn"
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")


def clean_text(text):
    """Normalize and remove non-ASCII characters."""
    text = unicodedata.normalize("NFKD", text)  # Normalize special characters
    text = re.sub(r"[^\x00-\x7F]+", "", text)  # Remove non-ASCII characters
    text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with a single newline
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    return text.strip()


# def split_text(text, max_chars=1000):
#     sentences = re.split(r'(?<=[.!?])\s+', text)  # Split by sentence
#     chunks, chunk = [], ""
#
#     try:
#         curr_sentence_index = 0
#         for sentence in sentences:
#             curr_sentence_index += 1
#             if len(chunk) + len(sentence) <= max_chars:
#                 chunk += sentence.strip() + " "
#             else:
#                 chunk = clean_text(chunk.strip())
#                 chunks.append(chunk[:max_chars])
#
#                 if len(chunk) > max_chars:
#                     chunk = chunk[max_chars:]
#                 # If current sentence is last
#                 if curr_sentence_index == len(sentences):
#                     while len(sentence) > 0:
#                         chunks.append(chunk[:max_chars])
#                         if len(chunk) > max_chars:
#                             chunk = chunk[max_chars:]
#                 else:
#                     if len(chunk) > max_chars:
#                         chunk = chunk[max_chars:] + " " + sentence.strip() + " "
#                     else:
#                         chunk = sentence.strip() + " "
#
#         if chunk:
#             chunk = clean_text(chunk.strip())
#             chunks.append(chunk)
#
#         return chunks
#     except Exception as e:
#         print(f"Failed to divide data to chunks: {e}")
#         return chunks


def split_text(text, max_chars=1000):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Split by sentence
    chunks, chunk = [], ""

    for sentence in sentences:
        sentence = clean_text(sentence.strip())
        if len(chunk) + len(sentence) <= max_chars:
            chunk += sentence.strip() + " "
        else:
            chunks.append(chunk[:max_chars])
            chunk = sentence.strip() + " "

    if chunk:
        chunks.append(chunk[:max_chars])

    return chunks


def filter_relevant_text(chunks, article_title):
    """Keep only text that is relevant to the given article title."""
    relevant_chunks = [chunk for chunk in chunks if article_title.lower() in chunk.lower()]
    return relevant_chunks if relevant_chunks else chunks


async def fetch_article_html(url):
    """ Fetches raw HTML content of a given news article """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None, None

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find("h1")
    if not title:
        title = soup.find("title")
    title = title.get_text(strip=True) if title else "Failed to get title"

    async with Translator() as translator:
        translated = await translator.translate(title, dest='en')
        title = translated.text

    return title, soup.text


def safe_summarize(text, max_length=1000, min_length=25):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length)
    summary_ids = model.generate(**inputs, max_length=max_length, min_length=min_length, do_sample=False)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


def summarize_article_content(url, use_gemini=False):
    article_title, article_text = asyncio.run(fetch_article_html(url))

    if article_title is None and article_text is None:
        return {"Title": None, "Summary": "Error in summarization."}

    if use_gemini:
        gemini_response = summarize_article_content_with_gemini(article_title, article_text)
        if "Failed to summarize article due to" not in gemini_response["Summary"]:
            return gemini_response
        else:
            print("ERROR IN gemini_response")

    chunks = split_text(article_text, max_chars=1000)

    # filtered_chunks = filter_relevant_text(chunks, article_title)
    filtered_chunks = chunks

    try:
        summaries = [safe_summarize(f"{article_title} - {chunk}") for chunk in filtered_chunks]

        final_summary = safe_summarize(" ".join(summaries), max_length=1000, min_length=50)

        return {"Title": clean_text(article_title), "Summary": clean_text(final_summary)}
    except Exception as e:
        print(f"Summarization failed: {e}")
        return {"Title": clean_text(article_title), "Summary": "Error in summarization."}


def summarize_article_content_with_gemini(article_title, article_text):
    final_summary = ""
    try:
        GEMINI_API_KEY = os.getenv("GEMINI_AI_API_KEY")

        if GEMINI_API_KEY is None:
            return {"Title": clean_text(article_title),
                    "Summary": f"Failed to summarize article due to Gemini model is unavailable."}

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            Summarize this below article which is scrapped from webpage. Identify content related to title and summarize and ignore redundant data.
            Title: {article_title}
            text: {article_text}
            """,
        )
        final_summary = response.text
        return {"Title": clean_text(article_title), "Summary": final_summary}
    except Exception as e:
        print(f"Error in summarizing article with Gemini: {e}")
        if len(final_summary) > 0:
            return {"Title": article_title, "Summary": final_summary}
        return {"Title": clean_text(article_title), "Summary": f"Failed to summarize article due to {e}"}


def all_articles_summary_with_gemini(data):
    final_summary = ""

    return True, "Test"

#     try:
#         GEMINI_API_KEY = os.getenv("GEMINI_AI_API_KEY")
#
#         if GEMINI_API_KEY is None:
#             return False, f"Gemini model is currently unavailable, so the articles couldn't be summarized."
#
#         prompt = f"""
# Summarize the following article summaries concisely, focusing on key insights, trends, sentiment analysis, and keywords.
# Ensure the response is structured into **four distinct sections**:
#
# 1. **Key Insights: ** (bullet points)
# 2. **Trends: ** (bullet points)
# 3. **Sentiment Analysis: **
# 4. **Keywords: ** (each keyword separated by a comma)
#
# Strictly provide the response in **plain Markdown format** (without enclosing it in triple backticks or code blocks).
# Avoid introductory phrases like "Here's a summary" or "Analyzing the articles."
# Do not include any unnecessary explanations—only the structured content.
#
# Summarized data of all articles:
#
# {data}
# """
#
#         client = genai.Client(api_key=GEMINI_API_KEY)
#
#         response = client.models.generate_content(
#             model="gemini-2.0-flash",
#             contents=prompt
#         )
#
#         final_summary = response.text
#
#         return True, final_summary
#     except Exception as e:
#         print(f"Error in summarizing article with Gemini: {e}")
#         if len(final_summary) > 0:
#             return True, final_summary
#         return False, f"Failed to summarize all the articles due to {e}"


def all_articles_comparative_analysis_with_gemini(data):
    final_summary = ""

    try:
        GEMINI_API_KEY = os.getenv("GEMINI_AI_API_KEY")

        if GEMINI_API_KEY is None:
            return False, f"Gemini model is currently unavailable, so the articles couldn't be summarized."

        prompt = f"""
Conduct a **comparative sentiment analysis** on the following articles to derive insights on how the company's news coverage varies.  
Ensure the response is structured into **four distinct sections**:

1. **Overall Sentiment Distribution:** (Summarize how the sentiment is distributed across the articles, mentioning whether the majority are positive, neutral, or negative.)
2. **Key Positive Themes:** (List the key positive aspects frequently highlighted in the articles.)
3. **Key Negative Themes:** (List the key negative aspects frequently mentioned in the articles.)
4. **Comparative Insights:** (Compare the sentiment trends across the articles, highlighting any shifts, variations, or patterns over time.)

Strictly provide the response in **plain Markdown format** (without enclosing it in triple backticks or code blocks).  
Avoid introductory phrases like "Here's an analysis" or "Analyzing the articles."  
Do not include any unnecessary explanations—only the structured content.

Summarized data of all articles:

{data}
"""

        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        final_summary = response.text

        return True, final_summary
    except Exception as e:
        print(f"Error in providing comparative analysis article with Gemini: {e}")
        if len(final_summary) > 0:
            return True, final_summary
        return False, f"Failed to providing comparative analysis due to {e}"
