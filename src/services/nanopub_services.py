from src.models.annotation import Annotation
from src.adapters.nanopublication import Nanopublication, NanopubRequest
from src.adapters.assertion_strategy import BioportalAssertionStrategy
from src.adapters.bioportal_api import BioPortalApi


class NanoPubServices:
    """
    Servicio para el manejo de las Nanopublicaciones
    """

    def __init__(self, bioportal_api: BioPortalApi):
        self.bioPortal_API = bioportal_api
        self.assertion_strategy = BioportalAssertionStrategy(self.bioPortal_API)

    def previewAnnotations(self, annotations: list, format: str = "trig"):
        """realiza la generacion de la info de las 'NanopubRequest' que se puedan calcular a partir de las annotaciones pasadas\n
        see #previewNanoPubRequest
        """
        nanoPubRequest_list = NanopubRequest.splitAnnotations(annotations)
        previews = []
        for nanoPubRequest in nanoPubRequest_list:
            previews.append(self.previewNanoPubRequest(nanoPubRequest, format))
        return previews

    def previewNanoPubRequest(
        self, nanoPubRequest: NanopubRequest, format: str = "trig"
    ):
        """realiza la generacion de la info de la 'NanopubRequest' retornando su nanopublicacion en
        el formato pasado '(trig formato default)', en un formato json bajo el siguiente formato\n
        {
            \n
            'id':str, //identificador del usuario que genera la anotacion,
            'user':str //usuario que genera la anotacion
            'url':str //url de origen de la annotacion
            'rdf':str //data de la nanopublicacion en el formato pasado
            'format':str //formato solicitiado
            \n
        }
        """
        format = format if format != None else "trig"
        nanoPub = Nanopublication(nanoPubRequest, self.assertion_strategy)
        return {
            "id": nanoPubRequest.id,
            "user": nanoPubRequest.user,
            "url": nanoPubRequest.url,
            "rdf": nanoPub.serialize(format),
            "format": format,
        }
