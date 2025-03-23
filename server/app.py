import gradio as gr
from text_to_speech import generate_audio
from utils import get_news_ui_css, markdown_to_plain_text, periodic_clean, analyze_company
from summarizer import all_articles_summary_with_gemini, all_articles_comparative_analysis_with_gemini


# Can be used for testing
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

    with ((gr.Blocks(css=get_news_ui_css(), theme=gr.themes.Default(text_size=gr.themes.sizes.text_lg))) as news_ui):
        gr.Markdown("## Company News Summary")

        summarize_all_state = gr.State(value={
            "DataFetched": False,
            "Data": None,
            "Failed": False,
            "FailedMessage": None,
            "AudioSummary": None
        })

        comparative_analysis_state = gr.State(value={
            "DataFetched": False,
            "Data": None,
            "Failed": False,
            "FailedMessage": None,
            "AudioSummary": None,
            "AccordionData": None
        })

        articles_list_state = gr.State(value=[])

        sentiment_summary_state = gr.State(value=None)

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
                    info="Gemini AI can extract a maximum of 5 articles at a time. Avoid excessive usage.",
                    min_width=300
                )

            with gr.Row(elem_classes='center_items'):
                submit_btn = gr.Button("Get News", elem_classes='btn__get_news', min_width=300)
                reset_btn = gr.Button("Reset", min_width=300)

        @gr.render(inputs=[company_name, max_articles, skip_value, use_gemini], triggers=[submit_btn.click])
        def render_data(company_name_val, max_articles_val, skip_value_val, use_gemini_val):
            try:
                if len(articles_list_state.value) > 0:
                    reset_ui_for_new_search()
                    gr.Warning("Please click on Reset button and refresh the page before searching for a new query.")
                    return

                info_duration = 30 if use_gemini_val == "Yes" else 40

                gr.Info(f"Hang tight... Loading articles related to {company_name_val}",
                        duration=max_articles_val * info_duration)

                article_list, sentiment_summary, summary_audio = analyze_company(company_name_val, max_articles_val,
                                                                                 skip_value_val, use_gemini_val)

                articles_list_state.value = article_list
                sentiment_summary_state.value = sentiment_summary

                if isinstance(article_list, str):
                    gr.Warning(article_list)
                    return

                with gr.Tab(label="Articles"):
                    with gr.Row():
                        overview_show_btn = gr.Button(value="Get Overall Insights & Summary", visible=True,
                                                      min_width=300)
                        comparative_analysis_btn = gr.Button(value="Get Comparative Analysis", visible=True,
                                                             min_width=300)

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
                                            gr.Markdown(value=article['Summary'],
                                                        show_copy_button=True, container=False, label="Summary")
                                            gr.Audio(label="Summary Audio", value=article['Audio'], interactive=False,
                                                     editable=False)

                with gr.Tab(label="Overall Insights & Summary", visible=False, elem_id="tab__overview"
                            ) as overview_tab:
                    gr.Markdown("## Overall Insights & Summary")
                    with gr.Column(visible=False) as overview_success_content:
                        # summarize_all_state.value["Data"]
                        with gr.Row():
                            overview_summary_audio = gr.Audio(label="Audio", interactive=False, min_width=250, scale=6)
                            overview_sentiment_summary = gr.Text(label="Sentiment Summary", interactive=False,
                                                                 min_width=300, scale=4)

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

                with gr.Tab(label="Comparative Analysis", visible=False) as analysis_tab:
                    gr.Markdown("## Comparative Sentiment Analysis")
                    with gr.Column(visible=False) as analysis_success_content:
                        with gr.Accordion(label="Reference: Article List", open=False):
                            analysis_articles_indies = gr.Markdown()

                        analysis_summary_audio = gr.Audio(label="Audio", interactive=False)
                        analysis_summary_output = gr.Markdown()

                    with gr.Column(visible=False) as analysis_loading_content:
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
                                        content: "Running comparative analysis... Hang tight!";
                                    }
                                    @keyframes l3 {
                                        to {
                                            background-position: 80% 100%;
                                        }
                                    }
                                </style>
                                <div class="loader"></div>
                            """)

                    with gr.Column(visible=False) as analysis_failure_content:
                        analysis_failure_output = gr.Markdown()

                # Show overview tab and fetch required data
                overview_show_btn.click(fn=tab_switched, inputs=[], outputs=[
                    overview_show_btn,  # Overview btn visibility
                    overview_tab,  # Tab visibility
                    overview_success_content,  # Success content visibility
                    overview_loading_content,  # Loading content visibility
                    overview_failure_content,  # Failure content visibility
                    overview_summary_output,  # Success content data
                    overview_summary_audio,  # Audio summary
                    overview_sentiment_summary,  # Sentiment summary
                    overview_failure_output,  # Failure content data
                ])

                def unload_news_ui():
                    overview_tab.visible = False  # Tab visibility
                    overview_success_content.visible = False  # Success content visibility
                    overview_loading_content.visible = False  # Loading content visibility
                    overview_failure_content.visible = False  # Failure content visibility

                    # Analysis tab data
                    analysis_tab.visible = False  # Tab visibility
                    analysis_success_content.visible = False  # Success content visibility
                    analysis_loading_content.visible = False  # Loading content visibility
                    analysis_failure_content.visible = False  # Failure content visibility

                    summarize_all_state.value["DataFetched"] = False
                    summarize_all_state.value["Data"] = None
                    summarize_all_state.value["Failed"] = False
                    summarize_all_state.value["FailedMessage"] = None
                    summarize_all_state.value["AudioSummary"] = None

                    comparative_analysis_state.value["DataFetched"] = False
                    comparative_analysis_state.value["Data"] = None
                    comparative_analysis_state.value["Failed"] = False
                    comparative_analysis_state.value["FailedMessage"] = None
                    comparative_analysis_state.value["AudioSummary"] = None
                    comparative_analysis_state.value["AccordionData"] = None

                    sentiment_summary_state.value = None

                    articles_list_state.value = []

                # Unload gradio component
                news_ui.unload(fn=unload_news_ui)

                # Comparative analysis btn
                comparative_analysis_btn.click(fn=get_comparative_analysis_data, inputs=[], outputs=[
                    comparative_analysis_btn,  # Comparative analysis btn visibility
                    analysis_tab,  # Tab visibility
                    analysis_success_content,  # Success content visibility
                    analysis_loading_content,  # Loading content visibility
                    analysis_failure_content,  # Failure content visibility
                    analysis_summary_output,  # Success content data
                    analysis_summary_audio,  # Analysis audio
                    analysis_failure_output,  # Failure content data
                    analysis_articles_indies  # Accordion data
                ])

                # Reset fields for new query
                reset_btn.click(fn=reset_ui_for_new_search, inputs=[], outputs=[
                    overview_tab,  # Tab visibility
                    overview_success_content,  # Success content visibility
                    overview_loading_content,  # Loading content visibility
                    overview_failure_content,  # Failure content visibility
                    overview_summary_output,  # Success content data
                    overview_summary_audio,  # Summary audio
                    overview_failure_output,  # Failure content data
                    # Analysis tab data
                    analysis_tab,  # Tab visibility
                    analysis_success_content,  # Success content visibility
                    analysis_loading_content,  # Loading content visibility
                    analysis_failure_content,  # Failure content visibility
                    analysis_summary_output,  # Success content data
                    analysis_summary_audio,  # Analysis audio
                    analysis_failure_output,  # Failure content data
                    analysis_articles_indies,  # Accordion data,
                    # State variables
                    summarize_all_state,
                    comparative_analysis_state,
                    sentiment_summary_state,
                    articles_list_state
                ])

            except Exception as e:
                gr.Warning(f"Something went wrong due to {e}")
                return

        def reset_ui_for_new_search():
            summarize_all_state.value = {
                "DataFetched": False,
                "Data": None,
                "Failed": False,
                "FailedMessage": None,
                "AudioSummary": None
            }

            comparative_analysis_state.value = {
                "DataFetched": False,
                "Data": None,
                "Failed": False,
                "FailedMessage": None,
                "AudioSummary": None,
                "AccordionData": None
            }

            sentiment_summary_state.value = None

            articles_list_state.value = []

            return (
                gr.update(visible=False),  # Show the tab
                gr.update(visible=False),  # Show the success content
                gr.update(visible=False),  # Hide the loading content
                gr.update(visible=False),  # Hide the failure content
                summarize_all_state.value["Data"],  # Update the success content
                summarize_all_state.value["AudioSummary"],
                summarize_all_state.value["FailedMessage"],  # Update failed message
                # Reset analysis tab data
                gr.update(visible=False),  # Show the tab
                gr.update(visible=False),  # Show the success content
                gr.update(visible=False),  # Hide the loading content
                gr.update(visible=False),  # Hide the failure content
                comparative_analysis_state.value["Data"],  # Update the success content
                comparative_analysis_state.value["AudioSummary"],  # Audio analysis
                comparative_analysis_state.value["FailedMessage"],  # Update failed message
                comparative_analysis_state.value["AccordionData"],  # Accordion data
                # State variables
                summarize_all_state,
                comparative_analysis_state,
                sentiment_summary_state,
                articles_list_state
            )

        # Get overall insights & summary
        def tab_switched():
            gr.Info("Loading overall insights & summary...", duration=60)
            summarize_all_state.value["Failed"] = False
            summarize_all_state.value["FailedMessage"] = None
            if summarize_all_state.value["DataFetched"]:
                gr.Info("Please switch to Overall Insights & Summary tab.")
                return (
                    gr.update(visible=False),  # Overview btn visibility
                    gr.update(visible=True),  # Show the tab
                    gr.update(visible=True),  # Show the success content
                    gr.update(visible=False),  # Hide the loading content
                    gr.update(visible=False),  # Hide the failure content
                    summarize_all_state.value["Data"],  # Update the success content
                    summarize_all_state.value["AudioSummary"],  # Audio summary
                    sentiment_summary_state.value,  # Sentiment summary
                    summarize_all_state.value["FailedMessage"],  # Update failed message
                )
            try:
                if len(articles_list_state.value) == 0:
                    summarize_all_state.value["Failed"] = True
                    summarize_all_state.value["FailedMessage"] = ("There no any articles fetched to provide overall "
                                                                  "insights.")
                    summarize_all_state.value["Data"] = None
                    summarize_all_state.value["DataFetched"] = False
                    summarize_all_state.value["AudioSummary"] = None
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
                gr.update(visible=False),  # Overview btn visibility
                gr.update(visible=True),  # Show the tab
                gr.update(visible=True),  # Show the success content
                gr.update(visible=False),  # Hide the loading content
                gr.update(visible=False),  # Hide the failure content
                summarize_all_state.value["Data"],  # Update the success content
                summarize_all_state.value["AudioSummary"],  # Audio summary
                sentiment_summary_state.value,  # Sentiment summary
                summarize_all_state.value["FailedMessage"],  # Update failed message
            )

        def get_comparative_analysis_data():
            gr.Info("Loading comparative analysis...", duration=60)
            comparative_analysis_state.value["Failed"] = False
            comparative_analysis_state.value["FailedMessage"] = None

            try:
                if comparative_analysis_state.value["DataFetched"]:
                    gr.Info("Please switch to Comparative Analysis tab.")
                    return (
                        gr.update(visible=False),  # Comparative analysis btn visibility
                        gr.update(visible=True),  # Show the tab
                        gr.update(visible=True),  # Show the success content
                        gr.update(visible=False),  # Hide the loading content
                        gr.update(visible=False),  # Hide the failure content
                        comparative_analysis_state.value["Data"],  # Update the success content
                        comparative_analysis_state.value["AudioSummary"],  # Audio summary
                        comparative_analysis_state.value["FailedMessage"],  # Update failed message
                        comparative_analysis_state.value["AccordionData"]  # Accordion data
                    )

                joined_summary = "\n".join(
                    f"Article-{i + 1}: **{article['Title']}** - {article['Summary']}"
                    for i, article in enumerate(articles_list_state.value)
                )

                comparative_analysis_status, comparative_analysis_response_data = all_articles_comparative_analysis_with_gemini(
                    joined_summary)

                if not comparative_analysis_status:
                    comparative_analysis_state.value["Failed"] = True
                    comparative_analysis_state.value["FailedMessage"] = comparative_analysis_response_data
                    comparative_analysis_state.value["Data"] = None
                    comparative_analysis_state.value["DataFetched"] = False
                    comparative_analysis_state.value["AudioSummary"] = None
                    comparative_analysis_state.value["AccordionData"] = None
                    raise gr.Error(all_summary_response_data)

                accordion_data = "\n".join(f"- Article {i + 1} - [{article['Title']}]({article['URL']})"
                                           for i, article in enumerate(articles_list_state.value)
                                           )

                comparative_analysis_state.value["Failed"] = False
                comparative_analysis_state.value["FailedMessage"] = None

                comparative_analysis_state.value["DataFetched"] = comparative_analysis_status
                comparative_analysis_state.value["Data"] = comparative_analysis_response_data

                comparative_analysis_state.value["AudioSummary"] = generate_audio(markdown_to_plain_text(
                    comparative_analysis_response_data))

                comparative_analysis_state.value["AccordionData"] = accordion_data

            except Exception as e:
                prev_summarize_all_state_failed = comparative_analysis_state.value["Failed"]
                if not prev_summarize_all_state_failed:
                    comparative_analysis_state.value["Failed"] = True
                    comparative_analysis_state.value["FailedMessage"] = f"Failed to get comparative analysis due to {e}"
                    comparative_analysis_state.value["Data"] = None
                    comparative_analysis_state.value["DataFetched"] = False
                    comparative_analysis_state.value["AudioSummary"] = None
                    comparative_analysis_state.value["AccordionData"] = None
                    raise gr.Error(f"Failed to get comparative analysis due to {e}")

            gr.Info("Please switch to Comparative Analysis tab.")
            return (
                gr.update(visible=False),  # Comparative analysis btn visibility
                gr.update(visible=True),  # Show the tab
                gr.update(visible=True),  # Show the success content
                gr.update(visible=False),  # Hide the loading content
                gr.update(visible=False),  # Hide the failure content
                comparative_analysis_state.value["Data"],  # Update the success content
                comparative_analysis_state.value["AudioSummary"],  # Audio analysis
                comparative_analysis_state.value["FailedMessage"],  # Update failed message
                comparative_analysis_state.value["AccordionData"]  # Accordion data
            )

    news_ui.launch(share=True)


complete_ui()
# periodic_clean()
