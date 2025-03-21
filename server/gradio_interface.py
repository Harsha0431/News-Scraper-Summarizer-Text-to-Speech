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
    with gr.Blocks() as news_ui:
        gr.Markdown("## Company News Summary")

        # Input fields
        with gr.Column():
            company_name = gr.Textbox(label="Enter Company Name")

            with gr.Row():
                max_articles = gr.Number(label="Max Articles (Less than 10)", value=5, minimum=1, maximum=10, step=1)
                skip_value = gr.Number(label="Skip Value (Pagination)", value=0, minimum=0, step=1)

            use_gemini = gr.Radio(
                ["No", "Yes"],
                label="Use Gemini AI?", value="No", interactive=True,
                info="Gemini AI can extract a maximum of 3 articles at a time. Avoid excessive usage."
            )

            submit_btn = gr.Button("Get News")

        @gr.render(inputs=[company_name, max_articles, skip_value, use_gemini], triggers=[submit_btn.click])
        def render_data(company_name_val, max_articles_val, skip_value_val, use_gemini_val):
            article_list, sentiment_summary, summary_audio = analyze_company(company_name_val, max_articles_val,
                                                                             skip_value_val, use_gemini_val)

            if isinstance(article_list, str):
                raise gr.Error(article_list)

            with gr.Column():
                article_index = 0
                for article in article_list:
                    article_index += 1
                    with gr.Group():
                        gr.HTML(f"""
                            <h3>
                                {article_index}. <a href="{article['URL']}" target="_blank">
                                    {article['Title']}
                                </a>
                            </h3>
                        """)
                        with gr.Row():
                            gr.TextArea(value=article['Summary'], interactive=False, type='text',
                                        show_copy_button=False, container=False, label="Summary", scale=5,
                                        min_width=300)
                            gr.Audio(label="Summary Audio", value=article['Audio'], interactive=False,
                                     editable=False, scale=2, min_width=200)

            with gr.Row():
                gr.Text(sentiment_summary, label="Sentiment Summary", interactive=False, scale=5, container=False,
                        min_width=300)
                gr.Audio(summary_audio, label="Sentiment Summary Audio", interactive=False, min_width=200, scale=2,)

    news_ui.launch(share=True)

    # iface = gr.Interface(
    #     fn=analyze_company,
    #     inputs=[
    #         gr.Textbox(label="Enter Company Name"),
    #         gr.Number(label="Max Articles (Less than 10)", value=5, minimum=1, maximum=10, step=1),
    #         gr.Number(label="Skip Value (Pagination)", value=0, minimum=0, step=1),
    #         gr.Radio(
    #             ["No", "Yes"],
    #             label="Use Gemini AI?",
    #             value="No",
    #             interactive=True,
    #             info="Gemini AI can extract a maximum of 3 articles at a time. Avoid excessive usage."
    #         ),
    #     ],
    #     outputs=[
    #         gr.D(),  # News articles with summaries in a grid
    #         gr.Text(label="Sentiment Summary"),
    #         gr.Audio(label="Summarized News Audio", interactive=True),  # List of audio outputs
    #     ],
    # )
    #
    # iface.launch(share=True)


complete_ui()
