import metadata_parser
import functools
import json


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


def pull_site_metadata(url: str) -> SiteMetada:
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
            uri=url,
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
    finally:
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
