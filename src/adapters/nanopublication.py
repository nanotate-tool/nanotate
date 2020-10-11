from src.models.nanopub_request import NanopubRequest
from src.models.annotation_tag import AnnotationTag
from .assertion_strategy import AssertionStrategy, LiteralAssertionStrategy
from src.utils.html_utils import format_text_to_html
import rdflib
import re
import functools
from rdflib.namespace import RDF, DC, XSD, RDFS


class Nanopublication:
    """
    Clase Base para la representación de las nanopublicaciones
    """

    # inicial namespaces
    NP = rdflib.Namespace("http://www.nanopub.org/nschema#")
    PPLAN = rdflib.Namespace("http://purl.org/net/p-plan#")
    PROV = rdflib.Namespace("http://www.w3.org/ns/prov#")
    DUL = rdflib.Namespace(
        "http://ontologydesignpatterns.org/wiki/Ontology:DOLCE+DnS_Ultralite/"
    )
    BPMN = rdflib.Namespace("https://www.omg.org/spec/BPMN/")
    PWO = rdflib.Namespace("http://purl.org/spar/pwo/")
    AUT = rdflib.Namespace("https://hypothes.is/a/")
    PLEX = rdflib.Namespace("https://w3id.org/fair/plex")
    SP = rdflib.Namespace("http://purl.org/net/SMARTprotocol#")
    BS = rdflib.Namespace(
        "https://bioschemas.org/profiles/LabProtocol/0.4-DRAFT-2020_07_23/#"
    )

    def __init__(
        self, npNamespace: rdflib.Namespace, rdf_base: rdflib.ConjunctiveGraph = None
    ):
        self.np = npNamespace
        if rdf_base == None:
            self.np_rdf = rdflib.ConjunctiveGraph()
            # initial namespaces
            self.__initInitialNamespaces()
        else:
            self.np_rdf = rdf_base

    def __initInitialNamespaces(self):
        """ inicializa los namespaces base de la nanopublicaciones"""
        self.np_rdf.bind("", self.np)
        self.np_rdf.bind("np", Nanopublication.NP)
        self.np_rdf.bind("p-plan", Nanopublication.PPLAN)
        self.np_rdf.bind("authority", Nanopublication.AUT)
        self.np_rdf.bind("prov", Nanopublication.PROV)
        self.np_rdf.bind("dul", Nanopublication.DUL)
        self.np_rdf.bind("bpmn", Nanopublication.BPMN)
        self.np_rdf.bind("pwo", Nanopublication.PWO)
        self.np_rdf.bind("dc", DC)
        self.np_rdf.bind("plex", Nanopublication.PLEX)
        self.np_rdf.bind("sp", Nanopublication.SP)
        self.np_rdf.bind("bs", Nanopublication.BS)

    def serialize(self, _format):
        """ realiza el proceso de serializacion de los datos de la nanopublicacion"""
        if _format == "json-html":
            return self.__json_html()
        else:
            return self.np_rdf.serialize(format=_format).decode("utf-8")

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
