from src.models.nanopub_request import NanopubRequest
from src.models.annotation_tag import AnnotationTag
from .nanopublication import Nanopublication
import rdflib
from rdflib.namespace import RDF, DC, XSD, RDFS
from .assertion_strategy import AssertionStrategy, LiteralAssertionStrategy


class AnnotationNanopublication(Nanopublication):
    """
    Representa una nanopublicacion generada desde un NanopubRequest pasado
    """
    # configuracion de cada tag para el assertion
    TAGS_CONFIG = [
        {"tag": AnnotationTag.step, "ref": DC.description},
        {"tag": AnnotationTag.sample, "ref": Nanopublication.BS.bioSampleUsed},
        {"tag": AnnotationTag.equipment, "ref": Nanopublication.BS.labEquipmentUsed},
        {"tag": AnnotationTag.reagent, "ref": Nanopublication.BS.reagentUsed},
        {"tag": AnnotationTag.input, "ref": Nanopublication.SP.hasExperimentalInput},
        {"tag": AnnotationTag.output, "ref": Nanopublication.SP.hasExperimentalOutput},
    ]

    def __init__(self, request: NanopubRequest, strategy: AssertionStrategy = None):
        url = request.step.url
        self.np = rdflib.Namespace(url + "#")
        super(AnnotationNanopublication, self).__init__(self.np)
        
        self.assertionStrategy = (
            strategy if strategy != None else LiteralAssertionStrategy()
        )
        self.request = request
        
        self.step = rdflib.term.URIRef(url + "#step")
        self.creationtime = rdflib.Literal(request.step.created, datatype=XSD.dateTime)
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

    def __initHead(self):
        """ inicializa la cabezera ':Head' de la nanopublicacion"""
        self.head = rdflib.Graph(self.np_rdf.store, self.np.Head)
        self.head.add((self.np[""], RDF.type, Nanopublication.NP.Nanopublication))
        self.head.add((self.np[""], Nanopublication.NP.hasAssertion, self.np.assertion))
        self.head.add(
            (self.np[""], Nanopublication.NP.hasProvenance, self.np.provenance)
        )
        self.head.add(
            (self.np[""], Nanopublication.NP.hasPublicationInfo, self.np.pubInfo)
        )
        self.head.add((self.np.assertion, RDFS.member, self.step))

    def __initAssertion(self):
        """ inicializa la cabezera ':assertion' de la nanopublicacion"""
        self.assertion = rdflib.Graph(self.np_rdf.store, self.np.assertion)

    def __initProvenance(self):
        """ inicializa la cabezera ':provenance' de la nanopublicacion"""
        self.provenance = rdflib.Graph(self.np_rdf.store, self.np.provenance)
        self.provenance.add(
            (self.np.assertion, Nanopublication.PROV.generatedAtTime, self.creationtime)
        )
        # insertando annotations
        for annotation in self.request.annotations:
            self.provenance.add(
                (
                    self.np.assertion,
                    Nanopublication.PROV.wasDerivedFrom,
                    rdflib.URIRef("https://hypothes.is/a/" + annotation.id),
                )
            )

    def __initPubinfo(self):
        """ inicializa la cabezera ':pubInfo' de la nanopublicacion"""
        self.pubInfo = rdflib.Graph(self.np_rdf.store, self.np.pubInfo)
        self.pubInfo.add(
            (
                self.np[""],
                Nanopublication.PROV.wasAttributedTo,
                Nanopublication.AUT[self.request.user],
            )
        )
        self.pubInfo.add(
            (self.np[""], Nanopublication.PROV.generatedAtTime, self.creationtime)
        )

    def __calcAssertion(self):
        """realiza el proceso de calculo del area 'assertion' de la nanopublicacion a partir de los datos
        de las annotaciones del request de la instancia actual 'self.request.annotations'
        """
        if self.assertion != None:
            for tag_config in self.TAGS_CONFIG:
                # procesando todas las anotaciones configuradas
                annotations_of_tag = self.request.annotationsOf(tag_config["tag"])
                if annotations_of_tag and len(annotations_of_tag) > 0:
                    for annotation in annotations_of_tag:
                        self.assertionStrategy.add(self, tag_config, annotation)