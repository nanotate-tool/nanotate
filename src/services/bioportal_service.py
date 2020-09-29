from src.adapters.bioportal_api import BioPortalApi
import re

class BioPortalService():
    """ Servicio del control de operaciones sobre la api de bioportal """

    def __init__(self):
        self.bioPortal_API = BioPortalApi(
            "8b5b7825-538d-40e0-9e9e-5ab9274a9aeb")

    def annotations(self, ontologies: list, text: str):
        """ retorna las anotaciones relacionadas al termino buscado en la api de bioportal con el siguiente formato
            de parseo determinado por ```BioPortalService.annotationParse```
        """
        api_annotations = self.bioPortal_API.annotator(text, ontologies)
        return list(
            map(BioPortalService.annotationParse, api_annotations)
        )

    @staticmethod
    def annotationParse(annotation):
        """ realiza el parseo de las anotaciones rescatadas desde la api de bioportal a un formato comun para las aplicaciones\n
            {\n\t
                'ontologyLabel':str,// label de la ontologia
                'prefLabel':str, // perfLabel
                'id':str, // identificador de la ontologia
                'class':str, //link de la clase 
                'ontology':str, //link de la ontologia
                'selector': list, //datos del selector
            \n\t}
        """
        annotatedClass = annotation['annotatedClass']
        ontologyLink = annotatedClass['links']['ontology']
        return {
            'ontologyLabel': re.sub(r'.*\/', '', ontologyLink),
            'prefLabel': annotatedClass['prefLabel'],
            'id': annotatedClass['@id'],
            'class': annotatedClass['links']['ui'],
            'ontology': ontologyLink,
            'selector': annotation['annotations']
        }
