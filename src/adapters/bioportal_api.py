import urllib.request
import urllib.parse
import json
import string


class BioPortalApi:
    """ Implementacion simple de la api de bioportal http://data.bioontology.org/documentation """

    def __init__(self, settings):
        self.REST_URL = settings['url']
        self.API_KEY = settings['key']

    def annotator(self, text: str, ontologies: list = []):
        """examina el texto pasado y retorna las classes relevantes asociadas al termino see http://data.bioontology.org/documentation#nav_annotator"""
        query_ontologies = '&ontologies=' + \
            ','.join(map(urllib.parse.quote, ontologies)
                     ) if len(ontologies) > 0 else ''
        return self.__get_json('/annotator?include=prefLabel&text=' + urllib.parse.quote(text)+query_ontologies)

    def __get_json(self, url: str):
        """lanza una peticion a la api insertando en esta la llave api de la instancia
            y parseando los resultados en jsons validos
        """
        opener = urllib.request.build_opener()
        opener.addheaders = [('Authorization', 'apikey token=' + self.API_KEY)]
        return json.loads(opener.open(self.REST_URL + url).read())
