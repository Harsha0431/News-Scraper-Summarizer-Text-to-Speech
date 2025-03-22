import re
import markdown


def get_news_ui_css():
    news_ui_css = """
    .center_items{
        display: flex;
        justify-content: center;
        align-items: center;
        place-items: center; 
    }
    
    .btn__get_news{
        width: fit-content !important;
    }
    
    .input_container{
        max-width: 840px;
    }
    """

    return news_ui_css


def markdown_to_plain_text(md_text):
    # Convert Markdown to HTML
    html_text = markdown.markdown(md_text)

    # Remove HTML tags
    plain_text = re.sub(r'<[^>]+>', '', html_text)

    # Replace multiple newlines with a single newline
    plain_text = re.sub(r'\n+', '\n', plain_text).strip()

    return plain_text
