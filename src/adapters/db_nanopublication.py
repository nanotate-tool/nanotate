from src.models import Nanopublication
from .nanopublication import Nanopublication as GraphNanopublication
from .assertion_strategy import AssertionStrategy
from rdflib.namespace import RDFS
import rdflib
import io


class DBNanopublication(GraphNanopublication):
    """
    Nanopublicacion generada desde el contenido de una nanopublicacion que
    fue almacenada en una base de datos
    """

    def __init__(self, nanopub: Nanopublication):
        self.nanopub = nanopub
        super().__init__(
            url=self.nanopub.protocol.uri,
            created=self.nanopub.created_at,
            author=self.nanopub.author,
        )
        self.__computeAssertion()

    def __computeAssertion(self):
        if self.assertion != None:
            for tag_config in self.TAGS_CONFIG:
                components = self.nanopub.componentsByTag(tag_config["tag"].value)
                for component in components:
                    if len(component.rel_uris) > 0:
                        AssertionStrategy.addRelUris(
                            nanoPub=self,
                            ref=tag_config["ref"],
                            exact=component.term,
                            uris=component.rel_uris,
                        )
                    else:
                        AssertionStrategy.addLiteral(
                            nanoPub=self, ref=tag_config["ref"], exact=component.term
                        )
