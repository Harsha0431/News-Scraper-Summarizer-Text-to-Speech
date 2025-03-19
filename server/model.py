import requests
from bs4 import BeautifulSoup
import time
import pprint


def get_google_news_links(company_name, max_articles=10):
    search_url = f"https://www.google.com/search?q={company_name}+news&tbm=nws"

    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract news links
    links = []
    for link in soup.select("a[href^='/url?q=']"):  # Google search links
        url = link["href"].split("&")[0].replace("/url?q=", "")
        if "google.com" not in url:  # Filter out Google redirect links
            links.append(url)

    return links[:max_articles]


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


def extract_news_content(url):
    """Extract title, summary, and metadata from a news article."""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": "Failed to fetch article"}

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title (from <h1>, <title>, or meta tags)
    title = soup.find("h1")
    if not title:
        title = soup.find("title")
    title = title.get_text(strip=True) if title else "No title available"

    # Extract all text from <article>, <div>, <p>, <span>
    article_content = []
    for tag in soup.find_all(["p"]):
        text = tag.get_text(strip=True)
        article_content.append(text)

    summary = " ".join(article_content)

    return {"title": title, "summary": summary, "url": url}


def get_news_articles(company_name, max_articles=10):
    all_links = get_google_news_links(company_name, max_articles * 2)  # Fetch extra links for filtering
    static_links = [link for link in all_links if is_static_page(link)]

    news_data = []
    for url in static_links[:max_articles]:
        news_data.append(extract_news_content(url))
        time.sleep(1)  # Avoid getting blocked

    return news_data


def fetch_news(company, max_articles=10):
    articles = get_news_articles(company, max_articles=max_articles)
    pprint.pprint(articles)
    return articles


pprint.pprint(fetch_news('Tata'))
