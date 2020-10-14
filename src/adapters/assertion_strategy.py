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

    @staticmethod
    def addLiteral(nanoPub, ref, exact: str):
        nanoPub.assertion.add((nanoPub.step, ref, rdflib.Literal(exact)))

    @staticmethod
    def addRelUris(nanoPub, ref, exact: str, uris: list):
        for uri in uris:
            uri_iri = rdflib.URIRef(uri)
            nanoPub.assertion.add((nanoPub.step, ref, uri_iri))
            nanoPub.assertion.add(
                (
                    uri_iri,
                    RDFS.label,
                    rdflib.Literal(exact),
                )
            )


class LiteralAssertionStrategy(AssertionStrategy):
    """ estrategia de 'assertion' en el cual la propiedad 'exact' de la 'anotacion' se inserta como literal """

    def add(self, nanoPub, tagConfig, annotation: Annotation):
        AssertionStrategy.addLiteral(nanoPub, tagConfig["ref"], annotation.exact)


class BioportalAssertionStrategy(LiteralAssertionStrategy):
    """estrategia de 'assertion' en el cual la propiedad 'exact' de la 'anotacion' se busca en la
    api de bioportal para relacionarla a una(s) ontologias\n

    la 'anotacion' con tag 'step' sera ignorada de esta busqueda y se usara la estrategia Literal (LiteralAssertionStrategy)
    para el 'assertion' de esta
    """

    DEFAULT_ONTOLOGIES = [
        "ERO",
        "SP",
        "CHEBI",
        "OBI",
        "BAO",
        "NCBITAXON",
        "UBERON",
        "EFO",
    ]

    def __init__(self, api: BioPortalApi):
        self.api = api

    def add(self, nanoPub, tagConfig, annotation: Annotation):
        if tagConfig["tag"] == AnnotationTag.step:
            super().add(nanoPub, tagConfig, annotation)
        else:
            bio_annotations = self.bioAnnotations(annotation)
            if len(bio_annotations) > 0:
                AssertionStrategy.addRelUris(
                    nanoPub, tagConfig["ref"], annotation.exact, bio_annotations
                )
            else:
                super().add(nanoPub, tagConfig, annotation)

    def bioAnnotations(self, annotation: Annotation) -> list:
        """
        retorna una lista de las anotaciones relacionadas a la anotacion
        """
        # prevents step annotation calculate bio_annotations
        if AnnotationTag.step.value in annotation.tags:
            return []

        ontologies = (
            annotation.ontologies
            if len(annotation.ontologies) > 0
            else self.DEFAULT_ONTOLOGIES
        )
        bio_annotations = self.api.annotator(annotation.exact, ontologies)
        bio_annotations = list(
            map(
                lambda bio_annotation: bio_annotation["annotatedClass"]["@id"],
                filter(
                    (
                        lambda bio_annotation: annotation.varIncludes(
                            "bio_annotations", bio_annotation["annotatedClass"]["@id"]
                        )
                    ),
                    bio_annotations,
                ),
            )
        )
        return bio_annotations
