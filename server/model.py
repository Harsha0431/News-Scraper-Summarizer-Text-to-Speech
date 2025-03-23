import requests
from bs4 import BeautifulSoup
import time
from summarizer import summarize_article_content


def get_google_news_links(company_name, max_articles=10, skip=0):
    start = skip
    headers = {"User-Agent": "Mozilla/5.0"}

    links = []

    while len(links) < max_articles:
        search_url = f'https://www.google.com/search?q=company:"{company_name}"+news&tbm=nws&start={start}'
        response = requests.get(search_url, headers=headers)

        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract news links
        new_links = []
        links_found = 0
        for link in soup.select("a[href^='/url?q=']"):  # Google search links
            links_found += 1
            url = link["href"].split("&")[0].replace("/url?q=", "")
            if "google.com" not in url and url not in links:  # Filter out Google links & duplicates
                new_links.append(url)

        links.extend(new_links)

        if len(new_links) == 0:
            break

        start += links_found + 1

    if max_articles < 10:
        max_articles = max_articles*2

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


def extract_news_content(url, use_gemini=False):
    final_summary = summarize_article_content(url, use_gemini=use_gemini)

    return {"Title": final_summary['Title'], "Summary": final_summary['Summary'], "URL": url}


def get_news_articles(company_name, max_articles=10, skip=0, use_gemini=False):
    all_links = get_google_news_links(company_name, max_articles=max_articles * 2, skip=skip)
    static_links = [link for link in all_links if is_static_page(link)]

    if len(static_links) == 0:
        return []

    news_data = []
    scrapped_articles = 0

    for url in static_links:
        if scrapped_articles >= max_articles:
            return news_data

        article = extract_news_content(url, use_gemini=use_gemini)
        if article['Title'] is not None:
            news_data.append(article)
            scrapped_articles += 1
        time.sleep(1)

    return news_data


def fetch_news(company, max_articles=10, skip=0, use_gemini=False):
    articles = get_news_articles(company, max_articles=max_articles, skip=skip, use_gemini=use_gemini)
    return articles
