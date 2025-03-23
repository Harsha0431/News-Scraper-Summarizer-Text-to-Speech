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
                info_duration = 30 if use_gemini_val == "Yes" else 40

                gr.Info(f"Hang tight... Loading articles related to {company_name_val}",
                        duration=max_articles_val * info_duration)

                article_list, sentiment_summary, summary_audio = analyze_company(company_name_val, max_articles_val,
                                                                                 skip_value_val, use_gemini_val)

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

                # Get overall insights & summary
                def tab_switched(prev_summarize_all_state):
                    gr.Info("Loading overall insights & summary...", duration=60)
                    prev_summarize_all_state["Failed"] = False
                    prev_summarize_all_state["FailedMessage"] = None

                    if prev_summarize_all_state["DataFetched"]:
                        gr.Info("Please switch to Overall Insights & Summary tab.")
                        return (
                            gr.update(visible=False),  # Overview btn visibility
                            gr.update(visible=True),  # Show the tab
                            gr.update(visible=True),  # Show the success content
                            gr.update(visible=False),  # Hide the loading content
                            gr.update(visible=False),  # Hide the failure content
                            prev_summarize_all_state["Data"],  # Update the success content
                            prev_summarize_all_state["AudioSummary"],  # Audio summary
                            gr.State(value=sentiment_summary),  # Sentiment summary
                            prev_summarize_all_state["FailedMessage"],  # Update failed message
                            # State variable
                            prev_summarize_all_state
                        )
                    try:
                        if len(article_list) == 0:
                            prev_summarize_all_state["Failed"] = True
                            prev_summarize_all_state["FailedMessage"] = (
                                "There no any articles fetched to provide overall "
                                "insights.")
                            prev_summarize_all_state["Data"] = None
                            prev_summarize_all_state["DataFetched"] = False
                            prev_summarize_all_state["AudioSummary"] = None
                            raise gr.Error(f"There no any articles fetched to provide overall insights.")

                        joined_summary = "\n".join(
                            f"{article_i['Title']} - {article_i['Summary']}" for article_i in article_list)

                        all_summary_response_status, all_summary_response_data = all_articles_summary_with_gemini(
                            joined_summary)

                        if not all_summary_response_status:
                            prev_summarize_all_state["Failed"] = True
                            prev_summarize_all_state["FailedMessage"] = all_summary_response_data
                            prev_summarize_all_state["Data"] = None
                            prev_summarize_all_state["DataFetched"] = False
                            prev_summarize_all_state["AudioSummary"] = None
                            raise gr.Error(all_summary_response_data)

                        prev_summarize_all_state["Failed"] = False
                        prev_summarize_all_state["FailedMessage"] = None

                        prev_summarize_all_state["DataFetched"] = all_summary_response_status
                        prev_summarize_all_state["Data"] = all_summary_response_data

                        prev_summarize_all_state["AudioSummary"] = generate_audio(markdown_to_plain_text(
                            all_summary_response_data))

                    except Exception as e:
                        prev_summarize_all_state_failed = prev_summarize_all_state["Failed"]
                        if not prev_summarize_all_state_failed:
                            prev_summarize_all_state["Failed"] = True
                            prev_summarize_all_state[
                                "FailedMessage"] = f"Failed to summarize all the articles due to {e}"
                            prev_summarize_all_state["Data"] = None
                            prev_summarize_all_state["DataFetched"] = False
                            prev_summarize_all_state["AudioSummary"] = None
                            raise gr.Error(f"Failed to summarize all the articles due to {e}")

                    gr.Info("Please switch to Overall Insights & Summary tab.")
                    return (
                        gr.update(visible=False),  # Overview btn visibility
                        gr.update(visible=True),  # Show the tab
                        gr.update(visible=True),  # Show the success content
                        gr.update(visible=False),  # Hide the loading content
                        gr.update(visible=False),  # Hide the failure content
                        prev_summarize_all_state["Data"],  # Update the success content
                        prev_summarize_all_state["AudioSummary"],  # Audio summary
                        gr.State(value=sentiment_summary),  # Sentiment summary
                        prev_summarize_all_state["FailedMessage"],  # Update failed message
                        # State variable
                        prev_summarize_all_state
                    )

                # Show overview tab and fetch required data
                overview_show_btn.click(fn=tab_switched, inputs=[summarize_all_state],
                                        outputs=[
                                            overview_show_btn,  # Overview btn visibility
                                            overview_tab,  # Tab visibility
                                            overview_success_content,  # Success content visibility
                                            overview_loading_content,  # Loading content visibility
                                            overview_failure_content,  # Failure content visibility
                                            overview_summary_output,  # Success content data
                                            overview_summary_audio,  # Audio summary
                                            overview_sentiment_summary,  # Sentiment summary
                                            overview_failure_output,  # Failure content data
                                            # State variable updated
                                            summarize_all_state
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

                # Unload gradio component
                news_ui.unload(fn=unload_news_ui)

                # Fetch comparative analysis
                def get_comparative_analysis_data(prev_comparative_analysis_state):
                    gr.Info("Loading comparative analysis...", duration=60)
                    prev_comparative_analysis_state["Failed"] = False
                    prev_comparative_analysis_state["FailedMessage"] = None

                    try:
                        if prev_comparative_analysis_state["DataFetched"]:
                            gr.Info("Please switch to Comparative Analysis tab.")
                            return (
                                gr.update(visible=False),  # Comparative analysis btn visibility
                                gr.update(visible=True),  # Show the tab
                                gr.update(visible=True),  # Show the success content
                                gr.update(visible=False),  # Hide the loading content
                                gr.update(visible=False),  # Hide the failure content
                                prev_comparative_analysis_state["Data"],  # Update the success content
                                prev_comparative_analysis_state["AudioSummary"],  # Audio summary
                                prev_comparative_analysis_state["FailedMessage"],  # Update failed message
                                prev_comparative_analysis_state["AccordionData"],  # Accordion data
                                # State variable
                                prev_comparative_analysis_state
                            )

                        joined_summary = "\n".join(
                            f"Article-{index + 1}: **{article_i['Title']}** - {article_i['Summary']}"
                            for index, article_i in enumerate(article_list)
                        )

                        ca_status, comparative_analysis_response_data = all_articles_comparative_analysis_with_gemini(
                            joined_summary)

                        if not ca_status:
                            prev_comparative_analysis_state["Failed"] = True
                            prev_comparative_analysis_state["FailedMessage"] = comparative_analysis_response_data
                            prev_comparative_analysis_state["Data"] = None
                            prev_comparative_analysis_state["DataFetched"] = False
                            prev_comparative_analysis_state["AudioSummary"] = None
                            prev_comparative_analysis_state["AccordionData"] = None
                            raise gr.Error(comparative_analysis_response_data)

                        accordion_data = "\n".join(f"- Article {index + 1} - [{article_i['Title']}]({article_i['URL']})"
                                                   for index, article_i in enumerate(article_list)
                                                   )

                        prev_comparative_analysis_state["Failed"] = False
                        prev_comparative_analysis_state["FailedMessage"] = None

                        prev_comparative_analysis_state["DataFetched"] = ca_status
                        prev_comparative_analysis_state["Data"] = comparative_analysis_response_data

                        prev_comparative_analysis_state["AudioSummary"] = generate_audio(markdown_to_plain_text(
                            comparative_analysis_response_data))

                        prev_comparative_analysis_state["AccordionData"] = accordion_data

                    except Exception as e:
                        prev_summarize_all_state_failed = prev_comparative_analysis_state["Failed"]
                        if not prev_summarize_all_state_failed:
                            prev_comparative_analysis_state["Failed"] = True
                            prev_comparative_analysis_state[
                                "FailedMessage"] = f"Failed to get comparative analysis due to {e}"
                            prev_comparative_analysis_state["Data"] = None
                            prev_comparative_analysis_state["DataFetched"] = False
                            prev_comparative_analysis_state["AudioSummary"] = None
                            prev_comparative_analysis_state["AccordionData"] = None

                            raise gr.Error(f"Failed to get comparative analysis due to {e}")

                    gr.Info("Please switch to Comparative Analysis tab.")
                    return (
                        gr.update(visible=False),  # Comparative analysis btn visibility
                        gr.update(visible=True),  # Show the tab
                        gr.update(visible=True),  # Show the success content
                        gr.update(visible=False),  # Hide the loading content
                        gr.update(visible=False),  # Hide the failure content
                        prev_comparative_analysis_state["Data"],  # Update the success content
                        prev_comparative_analysis_state["AudioSummary"],  # Audio analysis
                        prev_comparative_analysis_state["FailedMessage"],  # Update failed message
                        prev_comparative_analysis_state["AccordionData"],  # Accordion data
                        # State variable
                        prev_comparative_analysis_state
                    )

                # Comparative analysis btn
                comparative_analysis_btn.click(fn=get_comparative_analysis_data,
                                               inputs=[comparative_analysis_state],
                                               outputs=[
                                                   comparative_analysis_btn,  # Comparative analysis btn visibility
                                                   analysis_tab,  # Tab visibility
                                                   analysis_success_content,  # Success content visibility
                                                   analysis_loading_content,  # Loading content visibility
                                                   analysis_failure_content,  # Failure content visibility
                                                   analysis_summary_output,  # Success content data
                                                   analysis_summary_audio,  # Analysis audio
                                                   analysis_failure_output,  # Failure content data
                                                   analysis_articles_indies,  # Accordion data
                                                   # State variable
                                                   comparative_analysis_state
                                               ])

                # Reset fields for new query
                reset_btn.click(fn=reset_ui_for_new_search, inputs=[], outputs=[
                    overview_tab,  # Tab visibility
                    overview_success_content,  # Success content visibility
                    overview_loading_content,  # Loading content visibility
                    overview_failure_content,  # Failure content visibility
                    # Analysis tab data
                    analysis_tab,  # Tab visibility
                    analysis_success_content,  # Success content visibility
                    analysis_loading_content,  # Loading content visibility
                    analysis_failure_content,  # Failure content visibility
                    # State variables
                    summarize_all_state,
                    comparative_analysis_state,
                ])

            except Exception as e:
                gr.Warning(f"Something went wrong due to {e}")
                return

        def reset_ui_for_new_search():
            summarize_all_state_reset = {
                "DataFetched": False,
                "Data": None,
                "Failed": False,
                "FailedMessage": None,
                "AudioSummary": None
            }

            comparative_analysis_state_reset = {
                "DataFetched": False,
                "Data": None,
                "Failed": False,
                "FailedMessage": None,
                "AudioSummary": None,
                "AccordionData": None
            }

            gr.Info("Please continue with your next query.", duration=20)

            return (
                gr.update(visible=False),  # Show the tab
                gr.update(visible=False),  # Show the success content
                gr.update(visible=False),  # Hide the loading content
                gr.update(visible=False),  # Hide the failure content
                # Reset analysis tab data
                gr.update(visible=False),  # Show the tab
                gr.update(visible=False),  # Show the success content
                gr.update(visible=False),  # Hide the loading content
                gr.update(visible=False),  # Hide the failure content
                # State variables
                gr.State(value=summarize_all_state_reset),
                gr.State(comparative_analysis_state_reset),
            )

    news_ui.launch(share=True)


complete_ui()
# periodic_clean()
