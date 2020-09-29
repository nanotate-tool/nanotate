import urllib.request
import urllib.parse
import json
import string


class BioPortalApi:
    """ Implementacion simple de la api de bioportal http://data.bioontology.org/documentation """
    REST_URL = "http://data.bioontology.org"

    def __init__(self, apikey: str):
        self.API_KEY = apikey

    def annotator(self, text: str, ontologies: list = []):
        """examina el texto pasado y retorna las classes relevantes asociadas al termino see http://data.bioontology.org/documentation#nav_annotator"""
        query_ontologies = '&ontologies=' + \
            ','.join(map(urllib.parse.quote, ontologies)
                     ) if len(ontologies) > 0 else ''
        return self.__getJson('/annotator?include=prefLabel&text=' + urllib.parse.quote(text)+query_ontologies)

    def __getJson(self, url: str):
        """lanza una peticion a la api insertando en esta la llave api de la instancia
            y parseando los resultados en jsons validos
        """
        opener = urllib.request.build_opener()
        opener.addheaders = [('Authorization', 'apikey token=' + self.API_KEY)]
        return json.loads(opener.open(BioPortalApi.REST_URL + url).read())
