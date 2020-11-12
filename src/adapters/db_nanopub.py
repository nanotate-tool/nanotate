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

    def __init__(self, nanopub: Nanopublication):
        self.nanopub = nanopub
        created = (
            self.nanopub.generatedAtTime
            if self.nanopub.generatedAtTime != None
            else self.nanopub.created_at.strftime(self.dateTimeFormat)
        )
        super().__init__(
            url=self.nanopub.protocol.uri,
            created=created,
            author=self.nanopub.author,
            derived_from=self.derived_from,
        )
        # self.__computeAssertion()

    @property
    def derived_from(self) -> list:
        return list(
            map(
                lambda component: rdflib.URIRef(
                    "https://hypothes.is/a/" + component.id
                ),
                self.nanopub.components,
            )
        )

    def _computeAssertion(self) -> rdflib.ConjunctiveGraph:
        assertion = rdflib.ConjunctiveGraph()
        for tag_config in self.TAGS_CONFIG:
            components = self.nanopub.componentsByTag(tag_config["tag"].value)
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
