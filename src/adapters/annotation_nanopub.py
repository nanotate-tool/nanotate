from src.models.nanopub_request import NanopubRequest
from src.models.annotation_tag import AnnotationTag
from .graph_nanopub import GraphNanopub
import rdflib
from rdflib.namespace import RDF, DC, XSD, RDFS
from .assertion_strategy import AssertionStrategy, LiteralAssertionStrategy


class AnnotationNanopub(GraphNanopub):
    """
    Representa una nanopublicacion generada desde un NanopubRequest pasado
    """

    def __init__(
        self,
        request: NanopubRequest,
        strategy: AssertionStrategy = None,
        settings: dict = None,
    ):
        self.request = request
        self.assertionStrategy = (
            strategy if strategy != None else LiteralAssertionStrategy()
        )
        super(AnnotationNanopub, self).__init__(
            url=request.step.url,
            author=self.request.user,
            derived_from=self.derived_from,
            settings=settings,
        )

    @property
    def derived_from(self) -> list:
        return list(
            map(
                lambda annotation: rdflib.URIRef(
                    "https://hypothes.is/a/" + annotation.id
                ),
                self.request.annotations,
            )
        )

    def _computeAssertion(self, assertion: rdflib.Graph = None) -> rdflib.Graph:
        assertion = assertion if assertion != None else rdflib.Graph()
        for tag_config in self.TAGS_CONFIG:
            # procesando todas las anotaciones configuradas
            annotations_of_tag = self.request.annotationsOf(tag_config["tag"])
            if annotations_of_tag and len(annotations_of_tag) > 0:
                for annotation in annotations_of_tag:
                    self.assertionStrategy.add(self, assertion, tag_config, annotation)
        return assertion