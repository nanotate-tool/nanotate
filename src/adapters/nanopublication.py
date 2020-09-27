from src.models.nanopub_request import NanopubRequest
from src.models.annotation_tag import AnnotationTag
from .assertion_strategy import AssertionStrategy, LiteralAssertionStrategy
from src.utils.html_utils import format_text_to_html
import rdflib
import re
import functools
from rdflib.namespace import RDF, DC, XSD


class Nanopublication:
    # inicial namespaces
    NP = rdflib.Namespace("http://www.nanopub.org/nschema#")
    PPLAN = rdflib.Namespace("http://purl.org/net/p-plan#")
    PROV = rdflib.Namespace("http://www.w3.org/ns/prov#")
    DUL = rdflib.Namespace(
        "http://ontologydesignpatterns.org/wiki/Ontology:DOLCE+DnS_Ultralite/")
    BPMN = rdflib.Namespace("https://www.omg.org/spec/BPMN/")
    PWO = rdflib.Namespace("http://purl.org/spar/pwo/")
    AUT = rdflib.Namespace("https://hypothes.is/a/")
    PLEX = rdflib.Namespace("https://w3id.org/fair/plex")
    SP = rdflib.Namespace("http://purl.org/net/SMARTprotocol#")
    BS = rdflib.Namespace(
        "https://bioschemas.org/profiles/LabProtocol/0.4-DRAFT-2020_07_23/#")
    # configuracion de cada tag para el assertion
    TAGS_CONFIG = [
        {
            'tag': AnnotationTag.step,
            'ref': DC.description
        },
        {
            'tag': AnnotationTag.sample,
            'ref': BS.bioSampleUsed
        },
        {
            'tag': AnnotationTag.equipment,
            'ref': BS.labEquipmentUsed
        },
        {
            'tag': AnnotationTag.reagent,
            'ref': BS.reagentUsed
        },
        {
            'tag': AnnotationTag.input,
            'ref': SP.hasExperimentalInput
        },
        {
            'tag': AnnotationTag.output,
            'ref': SP.hasExperimentalOutput
        }
    ]

    def __init__(self, request: NanopubRequest, strategy: AssertionStrategy = None):
        url = request.step.url
        self.assertionStrategy = strategy if strategy != None else LiteralAssertionStrategy()
        self.request = request
        self.np = rdflib.Namespace(url+'#')
        self.step = rdflib.term.URIRef(url + '#step')
        self.np_rdf = rdflib.ConjunctiveGraph()
        self.creationtime = rdflib.Literal(
            request.step.created, datatype=XSD.dateTime)
        # initial namespaces
        self.__initInitialNamespaces()
        # head
        self.__initHead()
        # assertion
        self.__initAssertion()
        # provenance
        self.__initProvenance()
        # pubinfo
        self.__initPubinfo()
        # calc values
        self.__calcAssertion()

    def __initInitialNamespaces(self):
        """ inicializa los namespaces base de la nanopublicacion"""
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

    def __initHead(self):
        """ inicializa la cabezera ':Head' de la nanopublicacion"""
        self.head = rdflib.Graph(self.np_rdf.store, self.np.Head)
        self.head.add(
            (self.np[''], RDF.type, Nanopublication.NP.Nanopublication))
        self.head.add(
            (self.np[''], Nanopublication.NP.hasAssertion, self.np.assertion))
        self.head.add(
            (self.np[''], Nanopublication.NP.hasProvenance, self.np.provenance))
        self.head.add(
            (self.np[''], Nanopublication.NP.hasPublicationInfo, self.np.pubInfo))

    def __initAssertion(self):
        """ inicializa la cabezera ':assertion' de la nanopublicacion"""
        self.assertion = rdflib.Graph(self.np_rdf.store, self.np.assertion)

    def __initProvenance(self):
        """ inicializa la cabezera ':provenance' de la nanopublicacion"""
        self.provenance = rdflib.Graph(self.np_rdf.store, self.np.provenance)
        self.provenance.add(
            (self.np.assertion, Nanopublication.PROV.generatedAtTime, self.creationtime))
        # insertando annotations
        for annotation in self.request.annotations:
            self.provenance.add((self.np.assertion, Nanopublication.PROV.wasDerivedFrom,
                                 rdflib.URIRef("https://hypothes.is/a/"+annotation.id)))

    def __initPubinfo(self):
        """ inicializa la cabezera ':pubInfo' de la nanopublicacion"""
        self.pubInfo = rdflib.Graph(
            self.np_rdf.store, self.np.pubInfo)
        self.pubInfo.add(
            (self.np[''], Nanopublication.PROV.wasAttributedTo, Nanopublication.AUT[self.request.user]))
        self.pubInfo.add(
            (self.np[''], Nanopublication.PROV.generatedAtTime, self.creationtime))

    def __calcAssertion(self):
        """ realiza el proceso de calculo del area 'assertion' de la nanopublicacion a partir de los datos
            de las annotaciones del request de la instancia actual 'self.request.annotations'
        """
        if self.assertion != None:
            for tag_config in Nanopublication.TAGS_CONFIG:
                # procesando todas las anotaciones configuradas
                annotations_of_tag = self.request.annotationsOf(
                    tag_config['tag'])
                if annotations_of_tag and len(annotations_of_tag) > 0:
                    for annotation in annotations_of_tag:
                        self.assertionStrategy.add(
                            self, tag_config, annotation)

    def serialize(self, _format):
        """ realiza el proceso de serializacion de los datos de la nanopublicacion"""
        if _format == "json-html":
            return self.__json_html()
        else:
            return self.np_rdf.serialize(format=_format).decode('utf-8')

    def __json_html(self):
        """ realiza el proceso de serializacion de la nanopublicacion en un formato 'json-html'
            en el cual cada componente de la nanopublicacion esta separada por una en un formato json
            para presentar esta en html\n
            {
                \n
                '@prefixs': list
                '@assertion': list
                '@provenance': list
                '@pubInfo': list
                '@Head': list
                \n
            }
        """
        nanopubTrig = self.serialize('trig')
        prefixs = re.findall(r"\@prefix(.*).", nanopubTrig)
        assertion = re.search(r":assertion {.*?\}\n", nanopubTrig, re.DOTALL)
        provenance = re.search(r":provenance {.*?\}\n", nanopubTrig, re.DOTALL)
        pubInfo = re.search(r":pubInfo {.*?\}\n", nanopubTrig, re.DOTALL)
        Head = re.search(r":Head {.*?\}\n", nanopubTrig, re.DOTALL)
        return {
            '@prefixs': list(map((lambda prefix: format_text_to_html(prefix)), prefixs)),
            '@assertion': format_text_to_html(assertion.group(0)),
            '@provenance': format_text_to_html(provenance.group(0)),
            '@pubInfo': format_text_to_html(pubInfo.group(0)),
            '@Head': format_text_to_html(Head.group(0)),
        }
