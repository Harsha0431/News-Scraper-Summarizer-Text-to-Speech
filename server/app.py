from comparative_analysis import compare_sentiments
from text_to_speech import generate_audio
from model import fetch_news
import pprint


def get_news_summary_sentiment(company, max_articles=10, skip=0, use_gemini=False):
    articles = fetch_news(company, max_articles, skip, use_gemini=use_gemini)

    if len(articles) == 0:
        return articles, {}

    articles, summary = compare_sentiments(articles)

    return articles, summary


def analyze_company(company, max_articles=10, skip=0, use_gemini=False):
    if len(company) < 3:
        return "Company name must be at least 3 characters long.", "Company name must be at least 3 characters long.", None

    use_gemini = use_gemini == "Yes"

    if use_gemini:
        if max_articles > 3:
            max_articles = 3
    else:
        if max_articles > 10:
            max_articles = 10

    articles, sentiment_summary = get_news_summary_sentiment(company, max_articles, skip=skip, use_gemini=use_gemini)

    if len(articles) == 0:
        return "Sorry, no article found at the movement.", "Sorry, no article found at the movement.", None

    sentiment_summary_text = (f"Positive: {sentiment_summary['Positive']}, Negative: {sentiment_summary['Negative']}, "
                              f"Neutral: {sentiment_summary['Neutral']}")

    # Creating a panel-style container with a border like the default Gradio panel
    html_content = """
    <style>
        .custom-panel {
            border: 1px solid #3f3f46;
            border-radius: 4px;
            padding: 10px;
            background: #272727;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
        .grid-container {
            display: grid;
            grid-template-columns: repeat(2, 1fr); /* 2-column layout */
            gap: 10px;
        }
        .grid-item {
            padding: 10px;
            background: #27272a;
            border-radius: 4px;
            border: 1px solid #3f3f46;
            text-align: center;
            color: #f4f4f5;
            display: flex;
            gap: 2px;
        }
        .grid-item a {
            text-decoration: none;
            color: #E4E4E7;
            font-weight: bold;
            text-align: center;
        }
        
        .grid-item a{
            text-decoration: none;
        }
        
        .grid-item a::hover{
            text-decoration: underline;
        }
        
        .sentiment_bubble{
            width: 10px;
            height: 10px;
            overflow: hidden;
            border-radius: 100%;
            border: 1px solid;
        }
        
        .sentiment_neutral{
            background: #fcdb03;
            border-color: #fcdb03;
        }
        
        .sentiment_negative{
            background: #fc3d03;
            border-color: #fc3d03;
        }
        
        .sentiment_positive{
            background: #28fc03;
            border-color: #28fc03;
        }
    </style>
    <div class="custom-panel">
        <h4>News Articles</h4>
        <div class="grid-container">
    """

    for article in articles:
        html_content += f"""
        <div class="grid-item">
            <a href="{article['URL']}" target="_blank">{article['Title']}</a>
            <abbr title="Sentiment: {article['Sentiment']}">
            {
                '<div class="sentiment_bubble sentiment_neutral"></div>' if article['Sentiment'] == 'Neutral'
                else '<div class="sentiment_bubble sentiment_positive"></div>' if article['Sentiment'] == 'Positive'
                else '<div class="sentiment_bubble sentiment_negative"></div>'
            }
            </abbr>
        </div>
        """

    html_content += "</div></div>"

    audio_file = generate_audio(sentiment_summary_text)

    return html_content, sentiment_summary_text, audio_file
