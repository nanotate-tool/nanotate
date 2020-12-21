import metadata_parser
import functools
import json
from urllib.parse import urldefrag, urlparse, urljoin


class SiteMetada:
    """
    Contiene la metadata de un sitio web
    """

    # uri del sitio
    uri: str
    # titulo del sitio
    title: str
    # descripcion del sitio
    description: str
    # url de la image del sitio
    image: str
    # lista de authores de la pagina
    authors: list
    # recurso pdf del sitio
    pdf: str
    # palabras claves
    keywords: list
    # fecha de creacion
    creation_date: str
    # tipo del sitio
    _type: str

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def to_json(self):
        return self.__dict__


def pull_site_metadata(url: str, settings: dict = None) -> SiteMetada:
    """
    extrae la metadata del sitio asociado a la url pasada
    """
    try:
        page = metadata_parser.MetadataParser(url, search_head_only=True)
        # authors
        authors = page.get_metadatas("author")
        authors = authors if type(authors) is list else []
        if type(page.get_metadatas("citation_author")) is list:
            authors = authors + page.get_metadatas("citation_author")

        site_metada = SiteMetada(
            uri=clean_url_with_settings(url=url, settings=settings),
            title=joinArray_in_str(page.get_metadatas("title")),
            description=joinArray_in_str(page.get_metadatas("description")),
            image=get_first_appearance(page, "image"),
            _type=joinArray_in_str(page.get_metadatas("type")),
            authors=authors,
            pdf=get_first_appearance(page, "citation_pdf_url"),
            keywords=page.get_metadatas("keywords"),
            creation_date=joinArray_in_str(
                page.get_metadatas("citation_publication_date")
            ),
        )
        return site_metada

    except:
        return SiteMetada(uri=url, title="Site Meta data Not Found")


def get_first_appearance(page: metadata_parser.MetadataParser, prop: str) -> str:
    """
    obtiene el primer elemento para la propiedad en la pagina pasada
    """
    prop_data = page.get_metadatas(prop)
    if type(prop_data) is list:
        return prop_data[0]
    else:
        return None


def joinArray_in_str(arr: list, base: str = ""):
    """
    concatena los elementos de la lista en un string
    """
    return (
        functools.reduce((lambda a, line: a + line + " "), arr, base)
        if arr != None
        else ""
    )


def clean_url_with_settings(url: str, settings: dict = None):
    """
    same that clean_url but checks if base url have conditions for clean\n
        params:
            url: url to be cleared
            settings: global app settings (optional)
    """
    ignore_query_params = False
    if settings != None and settings["sites"] != None:
        ignore_query_params = (
            settings["sites"]["global"]["ig_query"]
            if settings["sites"]["global"] != None
            else False
        )
        url_parse = urlparse(url)
        base_url = url_parse.netloc
        for key in settings["sites"]:
            if (
                settings["sites"][key]["host"] == base_url
                and settings["sites"][key]["ig_query"]
            ):
                ignore_query_params = True
                break

    return clean_url(url=url, ignore_query_params=ignore_query_params)


def clean_url(url: str, ignore_query_params: bool = False) -> str:
    """
    parse passed url and returns url without his fragment (#fragment)\n
        params:
            url: url to be cleared
            ignore_query_params: True if ignore query paramas of url , False otherwise
    """
    if ignore_query_params:
        url_parse = urlparse(url)
        print("ignoring query params")
        print(url_parse)
        return url_parse.scheme + "://" + url_parse.netloc + url_parse.path
    else:
        url_defrag = urldefrag(url)
        return url_defrag.url