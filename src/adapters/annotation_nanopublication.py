from src.models.nanopub_request import NanopubRequest
from src.models.annotation_tag import AnnotationTag
from .nanopublication import Nanopublication
import rdflib
from rdflib.namespace import RDF, DC, XSD, RDFS
from .assertion_strategy import AssertionStrategy, LiteralAssertionStrategy


class AnnotationNanopublication(Nanopublication):
    """
    Representa una nanopublicacion generada desde un NanopubRequest pasado
    """

    def __init__(self, request: NanopubRequest, strategy: AssertionStrategy = None):
        self.request = request
        self.assertionStrategy = (
            strategy if strategy != None else LiteralAssertionStrategy()
        )
        super(AnnotationNanopublication, self).__init__(
            url=request.step.url,
            author=self.request.user,
            created=self.request.step.created,
        )
        # calc values
        self.__calcAssertion()

    def _initProvenance(self):
        """ inicializa la cabezera ':provenance' de la nanopublicacion"""
        super()._initProvenance()
        # insertando annotations
        for annotation in self.request.annotations:
            self.provenance.add(
                (
                    self.np.assertion,
                    Nanopublication.PROV.wasDerivedFrom,
                    rdflib.URIRef("https://hypothes.is/a/" + annotation.id),
                )
            )

    def __calcAssertion(self):
        """
        realiza el proceso de calculo del area 'assertion' de la nanopublicacion a partir de los datos
        de las annotaciones del request de la instancia actual 'self.request.annotations'
        """
        if self.assertion != None:
            for tag_config in self.TAGS_CONFIG:
                # procesando todas las anotaciones configuradas
                annotations_of_tag = self.request.annotationsOf(tag_config["tag"])
                if annotations_of_tag and len(annotations_of_tag) > 0:
                    for annotation in annotations_of_tag:
                        self.assertionStrategy.add(self, tag_config, annotation)