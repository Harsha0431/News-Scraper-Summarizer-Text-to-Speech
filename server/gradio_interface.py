import gradio as gr
from app import analyze_company
from text_to_speech import generate_audio
from utils import get_news_ui_css, markdown_to_plain_text
from summarizer import all_articles_summary_with_gemini


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
    summarize_all_state = gr.State(value={
        "DataFetched": False,
        "Data": None,
        "Failed": False,
        "FailedMessage": None,
        "AudioSummary": None
    })

    articles_list_state = gr.State(value=[])

    with ((gr.Blocks(css=get_news_ui_css(), theme=gr.themes.Default(text_size=gr.themes.sizes.text_lg))) as news_ui):
        gr.Markdown("## Company News Summary")

        # Input fields
        with gr.Column(elem_classes='input_container'):
            company_name = gr.Textbox(label="Enter Company Name")

            with gr.Row():
                max_articles = gr.Number(label="Max Articles (Less than 10)", value=5, minimum=1, maximum=10, step=1,
                                         min_width=250)
                skip_value = gr.Number(label="Skip Value (Pagination)", value=0, minimum=0, step=1, min_width=250)

                use_gemini = gr.Radio(
                    ["No", "Yes"],
                    label="Use Gemini AI?", value="No", interactive=True,
                    info="Gemini AI can extract a maximum of 3 articles at a time. Avoid excessive usage.",
                    min_width=300
                )
            with gr.Row(elem_classes='center_items'):
                submit_btn = gr.Button("Get News", elem_classes='btn__get_news')

        @gr.render(inputs=[company_name, max_articles, skip_value, use_gemini], triggers=[submit_btn.click])
        def render_data(company_name_val, max_articles_val, skip_value_val, use_gemini_val):

            if len(articles_list_state.value) > 0:
                gr.Warning("Please refresh the page before searching for a new query.")
                return

            article_list, sentiment_summary, summary_audio = analyze_company(company_name_val, max_articles_val,
                                                                             skip_value_val, use_gemini_val)

            articles_list_state.value = article_list

            if isinstance(article_list, str):
                raise gr.Error(article_list)

            with gr.Tab(label="Articles"):
                with gr.Column():
                    overview_show_btn = gr.Button(value="Get Overall Insights & Summary")

                with gr.Column():
                    article_index = 0
                    for i in range(0, len(article_list), 2):  # Iterate in steps of 2 for pairs of articles
                        with gr.Row():
                            for j in range(2):
                                if i + j < len(article_list):  # Check if article exists for the current pair
                                    article = article_list[i + j]
                                    article_index += 1
                                    with gr.Column(min_width=500, variant='panel'):
                                        gr.HTML(f"""
                                                    <h3>
                                                        {article_index}. <a href="{article['URL']}" target="_blank">
                                                            {article['Title']}
                                                        </a>
                                                    </h3>
                                                """)
                                        gr.TextArea(value=article['Summary'], interactive=False, type='text',
                                                    show_copy_button=False, container=False, label="Summary")
                                        gr.Audio(label="Summary Audio", value=article['Audio'], interactive=False,
                                                 editable=False)

            with gr.Tab(label="Overall Insights & Summary", visible=False, elem_id="tab__overview"
                        ) as overview_tab:
                with gr.Column(visible=False) as overview_success_content:
                    gr.Markdown("## Overall Insights & Summary")
                    # summarize_all_state.value["Data"]
                    overview_summary_audio = gr.Audio(label="Audio", interactive=False, min_width=250)
                    overview_summary_output = gr.Markdown()

                with gr.Column(visible=False) as overview_loading_content:
                    gr.HTML("""
                            <style>
                                .loader {
                                    width: fit-content;
                                    font-weight: bold;
                                    font-family: sans-serif;
                                    font-size: 30px;
                                    padding: 0 5px 8px 0;
                                    background: repeating-linear-gradient(90deg, currentColor 0 8%, #0000 0 10%) 200% 100% / 200% 3px no-repeat;
                                    animation: l3 2s steps(6) infinite;
                                }
                                .loader:before {
                                    content: "Analyzing articles... Hang tight!";
                                }
                                @keyframes l3 {
                                    to {
                                        background-position: 80% 100%;
                                    }
                                }
                            </style>
                            <div class="loader"></div>
                        """)

                with gr.Column(visible=False) as overview_failure_content:
                    overview_failure_output = gr.Markdown()  # f"**{summarize_all_state.value["FailedMessage"]}**"

            with gr.Tab(label="Sentiment Analysis"):
                with gr.Row():
                    gr.Text(sentiment_summary, label="Sentiment Summary", interactive=False, scale=5,
                            min_width=300)
                    gr.Audio(summary_audio, label="Sentiment Summary Audio", interactive=False, min_width=200,
                             scale=2)

            overview_show_btn.click(fn=tab_switched, inputs=[],
                                    outputs=[
                                        overview_tab,  # Tab visibility
                                        overview_success_content,  # Success content visibility
                                        overview_loading_content,  # Loading content visibility
                                        overview_failure_content,  # Failure content visibility
                                        overview_summary_output,  # Success content data
                                        overview_summary_audio,  # Audio summary
                                        overview_failure_output,  # Failure content data
                                    ])

            # Reset fields for new query
            submit_btn.click(fn=reset_ui_for_new_search, inputs=[], outputs=[
                overview_tab,  # Tab visibility
                overview_success_content,  # Success content visibility
                overview_loading_content,  # Loading content visibility
                overview_failure_content,  # Failure content visibility
                overview_summary_output,  # Success content data
                overview_summary_audio,  # Summary audio
                overview_failure_output,  # Failure content data
            ])

        def reset_ui_for_new_search():
            summarize_all_state.value["DataFetched"] = False,
            summarize_all_state.value["Data"] = None,
            summarize_all_state.value["Failed"] = False,
            summarize_all_state.value["FailedMessage"] = None
            summarize_all_state.value["AudioSummary"] = None

            articles_list_state.value = []

            return (
                gr.update(visible=False),  # Show the tab
                gr.update(visible=False),  # Show the success content
                gr.update(visible=False),  # Hide the loading content
                gr.update(visible=False),  # Hide the failure content
                summarize_all_state.value["Data"],  # Update the success content
                summarize_all_state.value["AudioSummary"],
                summarize_all_state.value["FailedMessage"],  # Update failed message
            )

        def tab_switched():
            gr.Info("Loading overall insights & summary...", duration=30)
            summarize_all_state.value["Failed"] = False
            summarize_all_state.value["FailedMessage"] = None
            if summarize_all_state.value["DataFetched"]:
                gr.Info("Please switch to Overall Insights & Summary tab.")
                return (
                    gr.update(visible=True),  # Show the tab
                    gr.update(visible=True),  # Show the success content
                    gr.update(visible=False),  # Hide the loading content
                    gr.update(visible=False),  # Hide the failure content
                    summarize_all_state.value["Data"],  # Update the success content
                    summarize_all_state.value["AudioSummary"],  # Audio summary
                    summarize_all_state.value["FailedMessage"],  # Update failed message
                )
            try:
                if len(articles_list_state.value) == 0:
                    summarize_all_state.value["Failed"] = True
                    summarize_all_state.value["FailedMessage"] = ("There no any articles fetched to provide overall "
                                                                  "insights.")
                    raise gr.Error(f"There no any articles fetched to provide overall insights.")

                joined_summary = "\n".join(
                    f"{article['Title']} - {article['Summary']}" for article in articles_list_state.value)

                all_summary_response_status, all_summary_response_data = all_articles_summary_with_gemini(
                    joined_summary)

                if not all_summary_response_status:
                    summarize_all_state.value["Failed"] = True
                    summarize_all_state.value["FailedMessage"] = all_summary_response_data
                    summarize_all_state.value["Data"] = None
                    summarize_all_state.value["DataFetched"] = False
                    summarize_all_state.value["AudioSummary"] = None
                    raise gr.Error(all_summary_response_data)

                summarize_all_state.value["Failed"] = False
                summarize_all_state.value["FailedMessage"] = None

                summarize_all_state.value["DataFetched"] = all_summary_response_status
                summarize_all_state.value["Data"] = all_summary_response_data

                summarize_all_state.value["AudioSummary"] = generate_audio(markdown_to_plain_text(
                    all_summary_response_data))

            except Exception as e:
                prev_summarize_all_state_failed = summarize_all_state.value["Failed"]
                if not prev_summarize_all_state_failed:
                    summarize_all_state.value["Failed"] = True
                    summarize_all_state.value["FailedMessage"] = f"Failed to summarize all the articles due to {e}"
                    summarize_all_state.value["Data"] = None
                    summarize_all_state.value["DataFetched"] = False
                    summarize_all_state.value["AudioSummary"] = None
                    raise gr.Error(f"Failed to summarize all the articles due to {e}")

            gr.Info("Please switch to Overall Insights & Summary tab.")
            return (
                gr.update(visible=True),  # Show the tab
                gr.update(visible=True),  # Show the success content
                gr.update(visible=False),  # Hide the loading content
                gr.update(visible=False),  # Hide the failure content
                summarize_all_state.value["Data"],  # Update the success content
                summarize_all_state.value["AudioSummary"],  # Audio summary
                summarize_all_state.value["FailedMessage"],  # Update failed message
            )

    news_ui.launch(share=True)


complete_ui()
