from src.models import Nanopublication
from src.models.annotation_tag import AnnotationTag
from .graph_nanopub import GraphNanopub
from .assertion_strategy import AssertionStrategy
from nanopub import NanopubClient, Publication
from rdflib.namespace import RDFS
import rdflib
import io


class DBNanopub(GraphNanopub):
    """
    Nanopublicacion generada desde el contenido de una nanopublicacion que
    fue almacenada en una base de datos
    """

    dateTimeFormat = "%Y-%m-%dT%H:%M:%S.%f%z"

    def __init__(
        self,
        db_nano_pub: Nanopublication,
        settings: dict = None,
        np_client: NanopubClient = None,
        from_db_rdf: bool = False,
    ):
        self.dbnanopub = db_nano_pub
        # fetch Publication for published nanopub
        nanopub = None
        if np_client != None and self.dbnanopub.publication_info != None:
            nanopub = np_client.fetch(uri=db_nano_pub.publication_info.nanopub_uri)
        elif from_db_rdf and self.dbnanopub.rdf_raw != None:
            nanopub_rdf = rdflib.ConjunctiveGraph()
            nanopub_rdf.parse(data=self.dbnanopub.rdf_raw, format="trig")
            nanopub = Publication(rdf=nanopub_rdf)

        if nanopub != None and self.dbnanopub.publication_info != None:
            nanopub.rdf.bind(
                "", rdflib.Namespace(self.dbnanopub.publication_info.nanopub_uri + "#")
            )

        super().__init__(
            url=self.dbnanopub.protocol.uri,
            author=self.dbnanopub.author,
            derived_from=self.derived_from,
            settings=settings,
            nanopub=nanopub,
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

    def _compute_assertion(self, assertion: rdflib.Graph = None) -> rdflib.Graph:
        assertion = assertion if assertion != None else rdflib.Graph()
        for tag_config in self.TAGS_CONFIG:
            components = self.dbnanopub.componentsByTag(tag_config["tag"].value)
            for component in components:
                if len(component.rel_uris) > 0:
                    AssertionStrategy.add_rel_uris(
                        nano_pub=self,
                        assertion=assertion,
                        ref=tag_config["ref"],
                        exact=component.term,
                        uris=component.rel_uris,
                    )
                else:
                    AssertionStrategy.add_literal(
                        nano_pub=self,
                        assertion=assertion,
                        ref=tag_config["ref"],
                        exact=component.term,
                        with_node=not (tag_config["tag"] == AnnotationTag.step),
                    )
        return assertion
