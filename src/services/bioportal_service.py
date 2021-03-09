from src.adapters.bioportal_api import BioPortalApi
import re


class BioPortalService:
    """
    Servicio del control de operaciones sobre la api de bioportal
    """

    def __init__(self, bioportal_api: BioPortalApi):
        self.bioportal_api = bioportal_api

    def annotations(self, ontologies: list, text: str):
        """retorna las anotaciones relacionadas al termino buscado en la api de bioportal con el siguiente formato
        de parseo determinado por ```BioPortalService.annotationParse```
        """
        api_annotations = self.bioportal_api.annotator(text, ontologies)
        return list(map(BioPortalService.annotation_parse, api_annotations))

    @staticmethod
    def annotation_parse(annotation):
        """realiza el parseo de las anotaciones rescatadas desde la api de bioportal a un formato comun para las aplicaciones\n
        {\n\t
            'ontologyLabel':str,// label de la ontologia
            'prefLabel':str, // perfLabel
            'id':str, // identificador de la ontologia
            'class':str, //link de la clase
            'ontology':str, //link de la ontologia
            'selector': list, //datos del selector
        \n\t}
        """
        annotated_class = annotation["annotatedClass"]
        ontology_link = annotated_class["links"]["ontology"]
        return {
            "ontologyLabel": re.sub(r".*\/", "", ontology_link),
            "prefLabel": annotated_class["prefLabel"],
            "id": annotated_class["@id"],
            "class": annotated_class["links"]["ui"],
            "ontology": ontology_link,
            "selector": annotation["annotations"],
        }
