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
        )
        self.__computeAssertion()

    def _initProvenance(self):
        """ inicializa la cabezera ':provenance' de la nanopublicacion"""
        super()._initProvenance()
        # insertando components
        for component in self.nanopub.components:
            self.provenance.add(
                (
                    self.np.assertion,
                    GraphNanopub.PROV.wasDerivedFrom,
                    rdflib.URIRef("https://hypothes.is/a/" + component.id),
                )
            )

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
