import rdflib
from src.models.annotation import Annotation
from src.models.annotation_tag import AnnotationTag
from .bioportal_api import BioPortalApi
from rdflib.namespace import RDFS


class AssertionStrategy:
    """define la estrategia que se tomara para determina el 'assertion' de una 'anotacion' en la 'nanopublication'"""

    def add(self, nanoPub, tagConfig, annotation: Annotation):
        """realiza el 'assertion' en la nanopublication pasada"""
        raise NotImplementedError


class LiteralAssertionStrategy(AssertionStrategy):
    """ estrategia de 'assertion' en el cual la propiedad 'exact' de la 'anotacion' se inserta como literal """

    def add(self, nanoPub, tagConfig, annotation: Annotation):
        nanoPub.assertion.add(
            (nanoPub.step, tagConfig['ref'], rdflib.Literal(annotation.exact)))


class BioportalAssertionStrategy(LiteralAssertionStrategy):
    """ estrategia de 'assertion' en el cual la propiedad 'exact' de la 'anotacion' se busca en la
        api de bioportal para relacionarla a una(s) ontologias\n

        la 'anotacion' con tag 'step' sera ignorada de esta busqueda y se usara la estrategia Literal (LiteralAssertionStrategy)
        para el 'assertion' de esta
    """

    DEFAULT_ONTOLOGIES = ['ERO', 'SP', 'CHEBI',
                          'OBI', 'BAO', 'NCBITAXON', 'UBERON', 'EFO']

    def __init__(self, api: BioPortalApi):
        self.api = api

    def add(self, nanoPub, tagConfig, annotation: Annotation):
        if tagConfig['tag'] == AnnotationTag.step:
            super().add(nanoPub, tagConfig, annotation)
        else:
            ontologies = annotation.ontologies if len(
                annotation.ontologies) > 0 else self.DEFAULT_ONTOLOGIES
            api_annotations = self.api.annotator(annotation.exact, ontologies)
            if api_annotations != None and len(api_annotations) > 0:
                for api_annotation in api_annotations:
                    id_iri = rdflib.URIRef(
                        api_annotation['annotatedClass']['@id'])
                    nanoPub.assertion.add(
                        (nanoPub.step, tagConfig['ref'], id_iri))
                    nanoPub.assertion.add(
                        (id_iri, RDFS.label, rdflib.Literal(annotation.exact)))
