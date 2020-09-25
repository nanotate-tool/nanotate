"""
    UTILERIAS DE HTML
"""


def format_text_to_html(text: str):
    """ realiza el formato del texto pasado a un formato html"""
    html_txt = text.replace("<", '&lt;')
    html_txt = html_txt.replace(">", '&gt;').replace("\n", '<br>')
    html_txt = html_txt.replace("\t", '&#9;')
    html_txt = html_txt.replace(" ", '&nbsp;')
    return html_txt