from flask import Flask, request, jsonify, send_file
from app import get_news_summary_sentiment
from text_to_speech import generate_audio

app = Flask(__name__)


@app.route('/news/summarize', methods=['GET'])
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


@app.route('/text/audio', methods=['POST'])
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


if __name__ == '__main__':
    app.run(debug=True)
