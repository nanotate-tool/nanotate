from src.models.nanopub_request import NanopubRequest
from src.models.annotation_tag import AnnotationTag
from .assertion_strategy import AssertionStrategy, LiteralAssertionStrategy
from src.utils.html_utils import format_text_to_html
import rdflib
import re
import functools
from rdflib.namespace import RDF, DC, XSD, RDFS
from datetime import datetime
from nanopub import Nanopub


class GraphNanopub:
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
        rdf_base: rdflib.ConjunctiveGraph = None,
    ):
        self.np = rdflib.Namespace(url + "#")
        self.step = rdflib.term.URIRef(url + "#step")
        self.creationtime = rdflib.Literal(created, datatype=XSD.dateTime)
        self.author = author
        if rdf_base == None:
            self.np_rdf = rdflib.ConjunctiveGraph()
            # initial namespaces
            self._initInitialNamespaces()
            # head
            self._initHead()
            # assertion
            self._initAssertion()
            # provenance
            self._initProvenance()
            # pubinfo
            self._initPubinfo()
        else:
            self.np_rdf = rdf_base

    def _initInitialNamespaces(self):
        """ inicializa los namespaces base de la nanopublicaciones"""
        self.np_rdf.bind("", self.np)
        self.np_rdf.bind("np", GraphNanopub.NP)
        self.np_rdf.bind("p-plan", GraphNanopub.PPLAN)
        self.np_rdf.bind("authority", GraphNanopub.AUT)
        self.np_rdf.bind("prov", GraphNanopub.PROV)
        self.np_rdf.bind("dul", GraphNanopub.DUL)
        self.np_rdf.bind("bpmn", GraphNanopub.BPMN)
        self.np_rdf.bind("pwo", GraphNanopub.PWO)
        self.np_rdf.bind("dc", DC)
        self.np_rdf.bind("plex", GraphNanopub.PLEX)
        self.np_rdf.bind("sp", GraphNanopub.SP)
        self.np_rdf.bind("bs", GraphNanopub.BS)

    def _initHead(self):
        """ inicializa la cabezera ':Head' de la nanopublicacion"""
        self.head = rdflib.Graph(self.np_rdf.store, self.np.Head)
        self.head.add((self.np[""], RDF.type, GraphNanopub.NP.Nanopublication))
        self.head.add((self.np[""], GraphNanopub.NP.hasAssertion, self.np.assertion))
        self.head.add(
            (self.np[""], GraphNanopub.NP.hasProvenance, self.np.provenance)
        )
        self.head.add(
            (self.np[""], GraphNanopub.NP.hasPublicationInfo, self.np.pubInfo)
        )
        self.head.add((self.np.assertion, RDFS.member, self.step))

    def _initAssertion(self):
        """ inicializa la cabezera ':assertion' de la nanopublicacion"""
        self.assertion = rdflib.Graph(self.np_rdf.store, self.np.assertion)

    def _initProvenance(self):
        """ inicializa la cabezera ':provenance' de la nanopublicacion"""
        self.provenance = rdflib.Graph(self.np_rdf.store, self.np.provenance)
        self.provenance.add(
            (self.np.assertion, GraphNanopub.PROV.generatedAtTime, self.creationtime)
        )

    def _initPubinfo(self):
        """ inicializa la cabezera ':pubInfo' de la nanopublicacion"""
        self.pubInfo = rdflib.Graph(self.np_rdf.store, self.np.pubInfo)
        self.pubInfo.add(
            (
                self.np[""],
                GraphNanopub.PROV.wasAttributedTo,
                GraphNanopub.AUT[self.author],
            )
        )
        self.pubInfo.add(
            (self.np[""], GraphNanopub.PROV.generatedAtTime, self.creationtime)
        )

    def serialize(self, _format):
        """ realiza el proceso de serializacion de los datos de la nanopublicacion"""
        if _format == "json-html":
            return self.__json_html()
        else:
            return self.np_rdf.serialize(format=_format).decode("utf-8")

    def fairWorkflowsNanopub(self):
        return Nanopub(rdf=self.np_rdf)

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
