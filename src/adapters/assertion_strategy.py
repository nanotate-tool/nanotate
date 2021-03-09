import rdflib
from src.models.annotation import Annotation
from src.models.annotation_tag import AnnotationTag
from .bioportal_api import BioPortalApi
from rdflib.namespace import RDFS, RDF


class AssertionStrategy:
    """define la estrategia que se tomara para determina el 'assertion' de una 'anotacion' en la 'nanopublication'"""

    def add(self, nano_pub, assertion, tag_config, annotation: Annotation):
        """realiza el 'assertion' en la nanopublication pasada"""
        raise NotImplementedError

    @staticmethod
    def add_literal(nano_pub, assertion, ref, exact: str, with_node: bool = False):
        if with_node:
            node = rdflib.BNode()
            assertion.add((nano_pub.step, ref, node))
            assertion.add((node, RDFS.label, rdflib.Literal(exact)))
        else:
            assertion.add((nano_pub.step, ref, rdflib.Literal(exact)))

    @staticmethod
    def add_rel_uris(nano_pub, assertion, ref, exact: str, uris: list):
        for uri in uris:
            uri_iri = rdflib.URIRef(uri)
            assertion.add((nano_pub.step, ref, uri_iri))
            assertion.add(
                (
                    uri_iri,
                    RDFS.label,
                    rdflib.Literal(exact),
                )
            )


class LiteralAssertionStrategy(AssertionStrategy):
    """ estrategia de 'assertion' en el cual la propiedad 'exact' de la 'anotacion' se inserta como literal """

    def add(self, nano_pub, assertion, tag_config, annotation: Annotation):
        AssertionStrategy.add_literal(
            nano_pub,
            assertion,
            tag_config["ref"],
            annotation.exact,
            not (tag_config["tag"] == AnnotationTag.step),
        )


class BioportalAssertionStrategy(LiteralAssertionStrategy):
    """estrategia de 'assertion' en el cual la propiedad 'exact' de la 'anotacion' se busca en la
    api de bioportal para relacionarla a una(s) ontologias\n

    la 'anotacion' con tag 'step' sera ignorada de esta busqueda y se usara la estrategia Literal (LiteralAssertionStrategy)
    para el 'assertion' de esta
    """

    def __init__(self, api: BioPortalApi):
        self.api = api

    def add(self, nano_pub, assertion, tag_config, annotation: Annotation):
        if tag_config["tag"] == AnnotationTag.step:
            super().add(nano_pub, assertion, tag_config, annotation)
        else:
            bio_annotations = self.bio_annotations(annotation)
            if len(bio_annotations) > 0:
                AssertionStrategy.add_rel_uris(
                    nano_pub,
                    assertion,
                    tag_config["ref"],
                    annotation.exact,
                    bio_annotations,
                )
            else:
                super().add(nano_pub, assertion, tag_config, annotation)

    def bio_annotations(self, annotation: Annotation, full: bool = False) -> list:
        """
        retorna una lista de las anotaciones relacionadas a la anotacion
        """
        # prevents step annotation calculate bio_annotations
        if AnnotationTag.step.value in annotation.tags:
            return []
        # empty ontologies array
        if len(annotation.ontologies) <= 0:
            return []

        ontologies = annotation.ontologies
        bio_annotations = self.api.annotator(annotation.exact, ontologies)
        bio_annotations = list(
            map(
                lambda bio_annotation: bio_annotation["annotatedClass"]["@id"]
                if not full
                else bio_annotation,
                filter(
                    (
                        lambda bio_annotation: annotation.var_includes(
                            "bio_annotations", bio_annotation["annotatedClass"]["@id"]
                        )
                    ),
                    bio_annotations,
                ),
            )
        )
        return bio_annotations
