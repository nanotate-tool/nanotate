from src.models.nanopub_request import NanopubRequest
from src.models.annotation_tag import AnnotationTag
from .assertion_strategy import AssertionStrategy, LiteralAssertionStrategy
from src.utils.html_utils import format_text_to_html
import rdflib
import re
import functools
from rdflib.namespace import DC, XSD
from datetime import datetime
from nanopub import Publication


class GraphNanopub:
    """
    Clase Base para la representación de las nanopublicaciones
    """

    # inicial namespaces
    AUT = rdflib.Namespace("https://hypothes.is/a/")
    SP = rdflib.Namespace("http://purl.org/net/SMARTprotocol#")
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
        url: str,
        created: datetime,
        author: str,
        derived_from: list,
    ):
        self.step = rdflib.term.URIRef(url + "#step")
        self.creationtime = rdflib.Literal(created, datatype=XSD.dateTime)
        self.author = self.AUT[author]
        self.nanopub = Publication.from_assertion(
            assertion_rdf=self._computeAssertion(),
            nanopub_author=self.author,
            derived_from=derived_from,
        )
        self.__addNamespaces()

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

    def __addNamespaces(self):
        """
        add custom namespaces to Publication rdf
        """
        self.nanopub.rdf.bind("authority", GraphNanopub.AUT)
        self.nanopub.rdf.bind("sp", GraphNanopub.SP)
        self.nanopub.rdf.bind("bs", GraphNanopub.BS)
        self.nanopub.rdf.bind("dc", DC)

    def _computeAssertion(self) -> rdflib.ConjunctiveGraph:
        """
        build the assertion subgraph
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
