from flask import Flask, request, jsonify, send_file
from app import get_news_summary_sentiment
from text_to_speech import generate_audio

app = Flask(__name__)


@app.route('/news/summarize', methods=['GET'])
def get_news():
    company = request.args.get('company', '')

    if not company:
        return jsonify({"error": "Company name is required"}), 400

    limit = request.args.get('limit', '')
    if not limit:
        limit = 5
    else:
        try:
            limit = int(limit)
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

    articles, sentiment_summary = get_news_summary_sentiment(company, limit, skip)

    response = {
        "Company": company,
        "Articles": articles,
        "Sentiment Distribution": sentiment_summary
    }

    return jsonify(response)


@app.route('/text/audio', methods=['POST'])
def text_to_audio():
    data = request.get_json()
    text = data.get("text", "")
    lang = data.get("lang", "hi")

    if not text:
        return jsonify({"error": "Text is required"}), 400

    audio_file = generate_audio(text, lang=lang)
    return send_file(audio_file, mimetype="audio/mpeg", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
