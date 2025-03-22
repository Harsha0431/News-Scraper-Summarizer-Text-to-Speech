import os

from flask import Flask, request, jsonify, send_file
from utils import get_news_summary_sentiment
from text_to_speech import generate_audio
from summarizer import all_articles_summary_with_gemini, all_articles_comparative_analysis_with_gemini
import io
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


@app.route('/api/news/summarize', methods=['GET'])
def get_news():
    try:
        company = request.args.get('company', '')
        if not company:
            return jsonify({"error": "Company name is required"}), 400

        limit = request.args.get('limit', '')
        if not limit:
            limit = 5
        else:
            try:
                limit = int(limit)
                if limit > 10:
                    limit = 10
            except Exception as e:
                limit = 5

        skip = request.args.get('skip', '')
        if not skip:
            skip = 0
        else:
            try:
                skip = int(skip)
            except Exception as e:
                skip = 0

        use_gemini_ai = request.args.get("gemini", False)
        if isinstance(use_gemini_ai, str):
            use_gemini_ai = use_gemini_ai.lower()
            use_gemini_ai = use_gemini_ai == 'true'
        else:
            use_gemini_ai = False

        if use_gemini_ai:
            if limit > 5:
                limit = 5

        articles, sentiment_summary = get_news_summary_sentiment(company, limit, skip, use_gemini_ai)

        if len(articles) == 0:
            return jsonify({"error": "Sorry, no article found at the movement."}), 404

        response = {
            "Company": company,
            "Articles": articles,
            "Sentiment Distribution": sentiment_summary
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Failed to get related dues articles due to {e}"}), 500


@app.route('/api/text/audio', methods=['POST'])
def text_to_audio():
    try:
        data = request.get_json()
        text = data.get("text", "")
        lang = data.get("lang", "hi")

        if not text or len(text) <= 0:
            return jsonify({"error": "Text is required"}), 400

        audio_file = generate_audio(text, lang=lang)
        return send_file(audio_file, mimetype="audio/mpeg", as_attachment=True), 200
    except Exception as e:
        return jsonify({"error": f"Failed to convert text to speech due to {e}"}), 500


@app.route('/api/news/overview', methods=['POST'])
def get_overall_summary__insights():
    try:
        data = request.get_json()
        articles = data["articles"]

        if (not isinstance(articles, list)) or len(articles) == 0:
            return jsonify({"error": "Please provide list of articles"}), 400

        for index, article in enumerate(articles):
            if not isinstance(article, dict) or "title" not in article or "summary" not in article:
                return jsonify({
                    "error": f"Article at index {index} is missing 'title' or 'summary'."
                }), 400

        joined_summary = "\n".join(
            f"{article['title']} - {article['summary']}" for article in articles)

        all_summary_response_status, all_summary_response_data = all_articles_summary_with_gemini(joined_summary)

        if not all_summary_response_status:
            return jsonify({"error": all_summary_response_data}), 400

        # Response data will be in Markdown format
        return jsonify({"data": all_summary_response_data}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to summarize and provide insights on the articles due to {e}"}), 500


@app.route("/api/news/analysis", methods=['POST'])
def get_comparative_analysis():
    try:
        data = request.get_json()
        articles = data["articles"]

        if (not isinstance(articles, list)) or len(articles) == 0:
            return jsonify({"error": "Please provide list of articles"}), 400

        for index, article in enumerate(articles):
            if not isinstance(article, dict) or "title" not in article or "summary" not in article:
                return jsonify({
                    "error": f"Article at index {index} is missing 'title' or 'summary'."
                }), 400

        joined_summary = "\n".join(
            f"Article-{i + 1}: **{article['title']}** - {article['summary']}"
            for i, article in enumerate(articles)
        )

        status, analysis = all_articles_comparative_analysis_with_gemini(joined_summary)

        if not status:
            return jsonify({"error": analysis}), 400

        # Response data will be in Markdown format
        return jsonify({"data": analysis}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to provide comparative analysis due to {e}"}), 500


# Load port value
PORT = os.getenv("FLASK_PORT", "5000")

try:
    PORT = int(PORT)
except ValueError:
    PORT = 5000


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=PORT)
