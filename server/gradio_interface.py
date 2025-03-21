import gradio as gr
from app import analyze_company
from text_to_speech import generate_audio


def text_to_speech_interface():
    iface = gr.Interface(
        fn=generate_audio,
        inputs=[gr.Textbox(label="Enter Text"), gr.Dropdown(["en", "hi", "es"], label="Language", value="en")],
        outputs=gr.Audio(label="Generated Speech"),
        title="Text-to-Speech Converter",
        description="Enter text and choose a language to generate speech audio."
    )

    iface.launch()


def complete_ui():
    iface = gr.Interface(
        fn=analyze_company,
        inputs=[
            gr.Textbox(label="Enter Company Name"),
            gr.Number(label="Max Articles (Less than 10)", value=5, minimum=1, maximum=10, step=1),
            gr.Number(label="Skip Value (Pagination)", value=0, minimum=0, step=1),
            gr.Radio(
                ["No", "Yes"],
                label="Use Gemini AI?",
                value="No",
                interactive=True,
                info="Gemini AI can extract a maximum of 3 articles at a time. Avoid excessive usage."
            ),
        ],
        outputs=[
            gr.HTML(),  # News articles with summaries in a grid
            gr.Text(label="Sentiment Summary"),
            gr.Audio(label="Summarized News Audio", interactive=True),  # List of audio outputs
        ],
    )

    iface.launch(share=True)


complete_ui()
