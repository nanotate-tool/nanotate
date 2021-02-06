from src.models.nanopub_request import NanopubRequest
from src.models.annotation_tag import AnnotationTag
from .assertion_strategy import AssertionStrategy, LiteralAssertionStrategy
from src.utils.html_utils import format_text_to_html
import rdflib
import re
import functools
from rdflib.namespace import DC, XSD, RDF
from datetime import datetime
from nanopub import Publication
from nanopub.definitions import DUMMY_NANOPUB_URI


class GraphNanopub:
    """
    Clase Base para la representación de las nanopublicaciones
    """

    # inicial namespaces
    AUT = rdflib.Namespace("https://hypothes.is/a/")
    AUTU = rdflib.Namespace("https://hypothes.is/users/")
    PAV = rdflib.Namespace("http://purl.org/pav/")
    SP = rdflib.Namespace("http://purl.org/net/SMARTprotocol#")
    PPLAN = rdflib.Namespace("http://purl.org/net/p-plan#")
    BS = rdflib.Namespace(
        "https://bioschemas.org/profiles/LabProtocol/0.4-DRAFT-2020_07_23/#"
    )

    # configuracion de cada tag para el assertion
    TAGS_CONFIG = [
        {"tag": AnnotationTag.step, "ref": DC.description},
        {"tag": AnnotationTag.sample, "ref": BS.bioSampleUsed},
        {"tag": AnnotationTag.equipment, "ref": BS.labEquipmentUsed},
        {"tag": AnnotationTag.reagent, "ref": BS.reagentUsed},
        {"tag": AnnotationTag.input, "ref": SP.hasExperimentalInput},
        {"tag": AnnotationTag.output, "ref": SP.hasExperimentalOutput},
    ]

    def __init__(
        self,
        author: str,
        derived_from: list,
        url: str = DUMMY_NANOPUB_URI,
        settings: dict = None,
        nanopub: Publication = None,
    ):
        self.settings = settings
        self.url = rdflib.URIRef(url)
        self.step = rdflib.term.URIRef(DUMMY_NANOPUB_URI + "#step")
        self.author = self.AUTU[GraphNanopub.clear_author_name(author)]
        if nanopub == None:
            # initial_triple added for skip validation for empty assertion graph for nanopub
            # this is made with purpose of remove identifier in BNodes added in assertion graph,
            # this only occurs when merge initial assertion graph in nanopub with sended assertion graph via 'from_assertion' method
            # so the assertion graph construction is let after of nanopub build
            initial_assertion = rdflib.Graph()
            initial_assertion.add((self.step, RDF.type, GraphNanopub.PPLAN.Step))
            initial_triple = (self.step, DC.initial, rdflib.Literal("initial"))
            initial_assertion.add(initial_triple)
            self.nanopub = Publication.from_assertion(
                assertion_rdf=initial_assertion,
                assertion_attributed_to=self.author,
                publication_attributed_to=self.author,
                derived_from=derived_from,
                introduces_concept=rdflib.term.BNode("step"),
            )
            # remove initial_triple added in assertion graph
            self.nanopub.rdf.remove(initial_triple)
            # compute assertion graph after of nanopub build
            self._computeAssertion(self.assertion)
            self.__addNamespaces()
            self._computeProvenance()
        else:
            self.nanopub = nanopub

    @property
    def assertion(self):
        return self.nanopub.assertion

    @property
    def pubinfo(self):
        return self.nanopub.pubinfo

    @property
    def provenance(self):
        return self.nanopub.provenance

    @property
    def np(self):
        for namespace in self.nanopub.rdf.namespaces():
            if namespace[0] == "" or namespace[0] == "this":
                return rdflib.Namespace(namespace[1])

    @property
    def createdWhit(self):
        return (
            rdflib.URIRef(self.settings["client-url"])
            if self.settings != None and "client-url" in self.settings
            else self.url
        )

    def __addNamespaces(self):
        """
        add custom namespaces to Publication rdf
        """
        self.nanopub.rdf.bind("authority", GraphNanopub.AUT)
        self.nanopub.rdf.bind("sp", GraphNanopub.SP)
        self.nanopub.rdf.bind("bs", GraphNanopub.BS)
        self.nanopub.rdf.bind("dc", DC)
        self.nanopub.rdf.bind("pav", GraphNanopub.PAV)
        self.nanopub.rdf.bind("p-plan", GraphNanopub.PPLAN)

    def _computeProvenance(self):
        """
        compute custom properties for provenance subgraph
        """
        assertion_uri = self.np.assertion
        self.provenance.add((assertion_uri, self.PAV.createdWith, self.createdWhit))

    def _computeAssertion(self, assertion: rdflib.Graph = None) -> rdflib.Graph:
        """
        build the assertion subgraph
        \n
        Args:
            assertion : graph base for assertion
        """
        raise NotImplementedError

    def serialize(self, _format):
        """ realiza el proceso de serializacion de los datos de la nanopublicacion"""
        if _format == "json-html":
            return self.__json_html()
        else:
            return self.nanopub.rdf.serialize(format=_format).decode("utf-8")

    def __json_html(self):
        """realiza el proceso de serializacion de la nanopublicacion en un formato 'json-html'
        en el cual cada componente de la nanopublicacion esta separada por una en un formato json
        para presentar esta en html\n
        {
            \n
            '@prefixs': list
            '@assertion': list
            '@provenance': list
            '@pubInfo': list
            '@Head': list
            'exact': str
            \n
        }
        """
        nanopubTrig = self.serialize("trig")
        prefixs = re.findall(r"\@prefix(.*).", nanopubTrig)
        assertion = re.search(r":assertion {.*?\}\n", nanopubTrig, re.DOTALL)
        provenance = re.search(r":provenance {.*?\}\n", nanopubTrig, re.DOTALL)
        pubInfo = re.search(r":pubInfo {.*?\}\n", nanopubTrig, re.DOTALL)
        Head = re.search(r":Head {.*?\}\n", nanopubTrig, re.DOTALL)
        return {
            "@prefixs": list(
                map((lambda prefix: format_text_to_html(prefix)), prefixs)
            ),
            "@assertion": format_text_to_html(assertion.group(0)),
            "@provenance": format_text_to_html(provenance.group(0)),
            "@pubInfo": format_text_to_html(pubInfo.group(0)),
            "@Head": format_text_to_html(Head.group(0)),
            "exact": nanopubTrig,
        }

    @staticmethod
    def clear_author_name(author: str) -> str:
        """
        clears a author name when this comes whit the format:
            'acct:<username>@hypothes.is' -> acct:miguel.ruano@hypothes.is
        """
        if author != None:
            au_regex = re.search("(?<=acct:)(.*)(?=@)", author)
            if au_regex:
                return au_regex.group(1)
        return author
