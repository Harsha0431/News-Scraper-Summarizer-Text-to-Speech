import gradio as gr
from comparative_analysis import compare_sentiments
from text_to_speech import generate_audio
from model import fetch_news


def analyze_company(company):
    articles = fetch_news(company)

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
            color: #f4f4f5
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
    </style>
    <div class="custom-panel">
        <h4>News Articles</h4>
        <div class="grid-container">
    """

    for article in articles:
        html_content += f"""
        <div class="grid-item">
            <a href="{article['url']}" target="_blank">{article['title']}</a>
        </div>
        """

    html_content += "</div></div>"

    summary = compare_sentiments(articles)
    summary_text = f"Positive: {summary['Positive']}, Negative: {summary['Negative']}, Neutral: {summary['Neutral']}"

    audio_file = generate_audio(summary_text)

    return html_content, summary_text, audio_file


iface = gr.Interface(
    fn=analyze_company,
    inputs=gr.Textbox(label="Enter Company Name"),
    outputs=[
        gr.HTML(),  # News articles with summaries in a grid
        gr.Text(label="Sentiment Summary"),
        gr.Audio(label="Summarized News Audio", interactive=True)  # List of audio outputs
    ],
)

iface.launch(share=True)
