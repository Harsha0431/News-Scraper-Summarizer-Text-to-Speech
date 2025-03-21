import requests
from bs4 import BeautifulSoup
import time
import pprint
from summarizer import summarize_article_content


def get_google_news_links(company_name, max_articles=10, skip=0):
    search_url = f'https://www.google.com/search?q=company:"{company_name}"+news&tbm=nws'

    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract news links
    links = []
    for link in soup.select("a[href^='/url?q=']"):  # Google search links
        url = link["href"].split("&")[0].replace("/url?q=", "")
        if "google.com" not in url:  # Filter out Google redirect links
            links.append(url)

    return links[skip:max_articles]


def is_static_page(url):
    """ Check if a webpage is static (not requiring JavaScript) """
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # Heuristic: If body is empty or has JS-based prompts, it's likely JavaScript-based
        body_text = soup.get_text(strip=True)
        if "enable JavaScript" in body_text or len(body_text) < 500:
            return False
        return True
    except requests.exceptions.RequestException:
        return False


def extract_news_content(url, use_gemini=False):
    final_summary = summarize_article_content(url, use_gemini=use_gemini)

    return {"Title": final_summary['Title'], "Summary": final_summary['Summary'], "URL": url}


def get_news_articles(company_name, max_articles=10, skip=0, use_gemini=False):
    all_links = get_google_news_links(company_name, max_articles=max_articles * 2, skip=skip)
    static_links = [link for link in all_links if is_static_page(link)]

    if len(static_links) == 0:
        return []

    news_data = []
    for url in static_links[skip:max_articles]:
        news_data.append(extract_news_content(url, use_gemini=use_gemini))
        time.sleep(1)

    return news_data


def fetch_news(company, max_articles=10, skip=0, use_gemini=False):
    articles = get_news_articles(company, max_articles=max_articles, skip=skip, use_gemini=use_gemini)
    return articles
