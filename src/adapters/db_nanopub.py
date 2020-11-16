from src.models import Nanopublication
from .graph_nanopub import GraphNanopub
from .assertion_strategy import AssertionStrategy
from rdflib.namespace import RDFS
import rdflib
import io


class DBNanopub(GraphNanopub):
    """
    Nanopublicacion generada desde el contenido de una nanopublicacion que
    fue almacenada en una base de datos
    """

    dateTimeFormat = "%Y-%m-%dT%H:%M:%S.%f%z"

    def __init__(self, nanopub: Nanopublication, settings: dict = None):
        self.dbnanopub = nanopub
        created = (
            self.dbnanopub.generatedAtTime
            if self.dbnanopub.generatedAtTime != None
            else self.dbnanopub.created_at.strftime(self.dateTimeFormat)
        )
        super().__init__(
            url=self.dbnanopub.protocol.uri,
            created=created,
            author=self.dbnanopub.author,
            derived_from=self.derived_from,
            settings=settings,
        )

    @property
    def derived_from(self) -> list:
        return list(
            map(
                lambda component: rdflib.URIRef(
                    "https://hypothes.is/a/" + component.id
                ),
                self.dbnanopub.components,
            )
        )

    def _computeAssertion(self, assertion: rdflib.Graph = None) -> rdflib.Graph:
        assertion = assertion if assertion != None else rdflib.Graph()
        for tag_config in self.TAGS_CONFIG:
            components = self.dbnanopub.componentsByTag(tag_config["tag"].value)
            for component in components:
                if len(component.rel_uris) > 0:
                    AssertionStrategy.addRelUris(
                        nanoPub=self,
                        assertion=assertion,
                        ref=tag_config["ref"],
                        exact=component.term,
                        uris=component.rel_uris,
                    )
                else:
                    AssertionStrategy.addLiteral(
                        nanoPub=self,
                        assertion=assertion,
                        ref=tag_config["ref"],
                        exact=component.term,
                    )
        return assertion
