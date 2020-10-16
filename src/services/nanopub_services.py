from src.models.annotation import Annotation
from src.adapters.annotation_nanopublication import (
    AnnotationNanopublication,
    NanopubRequest,
)
from src.adapters.db_nanopublication import DBNanopublication
from src.adapters.assertion_strategy import BioportalAssertionStrategy
from src.adapters.bioportal_api import BioPortalApi
from src.models import Protocol, Nanopublication, NanopublicationComponent
from src.repositories import NanopublicationRepository, ProtocolsRepository
import json


class NanoPubServices:
    """
    Servicio para el manejo de las Nanopublicaciones
    """

    def __init__(
        self,
        bioportal_api: BioPortalApi,
        protocolsRepo: ProtocolsRepository,
        nanopubsRepo: NanopublicationRepository,
    ):
        self.bioPortal_API = bioportal_api
        self.assertion_strategy = BioportalAssertionStrategy(self.bioPortal_API)
        self.protocolsRepo = protocolsRepo
        self.nanopubsRepo = nanopubsRepo

    def nanopubsByProtocol(
        self, protocol, json: bool = False, rdf_format: str = "trig"
    ) -> list:
        """
        retorna las nanopublicaciones realacionadas al protocolo pasado
        """
        nanopubs = self.nanopubsRepo.getNanopubsByProtocol(protocol=protocol)
        if rdf_format != None and rdf_format != "trig":
            for nanopub in nanopubs:
                nanopub.rdf_raw = DBNanopublication(nanopub).serialize(rdf_format)
        return (
            list(map(lambda nanopub: nanopub.to_json_map(), nanopubs))
            if json
            else nanopubs
        )

    def nanopubById(self, id: str, json: bool = False, rdf_format: str = "trig"):
        """
        retorna la nanopublicacion relacionada al identificador pasado
        """
        nanopub = self.nanopubsRepo.getNanopub(id=id)
        if nanopub != None:
            if rdf_format != None and rdf_format != "trig":
                nanopub.rdf_raw = DBNanopublication(nanopub).serialize(rdf_format)
            return nanopub.to_json_map() if json else nanopub
        else:
            return {"error": "not-found"}

    def registerFromAnnotations(self, annotations: list):
        """
        Realiza el proceso de registro de las nanopublicaciones que se puedan
        construir a partir de la lista de anotaciones pasadas
        """
        nanopubRequest = NanopubRequest.splitAnnotations(annotations)
        mapped = {"status": "ok"}
        for request in nanopubRequest:
            result = self.registerFromNanopubRequest(request)
            if result["status"] != "ok":
                mapped["status"] = "with-errors"
            mapped[request.id] = result
        return mapped

    def registerFromNanopubRequest(self, request: NanopubRequest):
        """
        Realiza el registro de la nanopublicacion contenida en el NanopubRequest pasado
        """
        data_updated = self.__updateNanopubAndProtocol(request)
        for data in data_updated:
            data.save()
        return {
            "protocol": data_updated[0].to_json_map(),
            "nanopub": data_updated[1].to_json_map(),
            "status": "ok",
        }

    def previewAnnotations(self, annotations: list, format: str = "trig"):
        """
        realiza la generacion de la info de las 'NanopubRequest' que se puedan calcular a partir de las annotaciones pasadas\n
        see #previewNanoPubRequest
        """
        nanoPubRequest_list = NanopubRequest.splitAnnotations(annotations)
        previews = []
        for nanoPubRequest in nanoPubRequest_list:
            previews.append(self.previewNanoPubRequest(nanoPubRequest, format))
        return previews

    def previewNanoPubRequest(
        self, nanoPubRequest: NanopubRequest, format: str = "trig"
    ):
        """
        realiza la generacion de la info de la 'NanopubRequest' retornando su nanopublicacion en
        el formato pasado '(trig formato default)', en un formato json bajo el siguiente formato\n
        {
            \n
            'id':str, //identificador del usuario que genera la anotacion,
            'user':str //usuario que genera la anotacion
            'url':str //url de origen de la annotacion
            'rdf':str //data de la nanopublicacion en el formato pasado
            'format':str //formato solicitiado
            \n
        }
        """
        format = format if format != None else "trig"
        nanoPub = AnnotationNanopublication(nanoPubRequest, self.assertion_strategy)
        return {
            "id": nanoPubRequest.id,
            "user": nanoPubRequest.user,
            "url": nanoPubRequest.url,
            "rdf": nanoPub.serialize(format),
            "format": format,
        }

    def __updateNanopubAndProtocol(self, request: NanopubRequest) -> tuple:
        """
        realiza la actualizacion o creacion de la nanopublicacion y su protocolo realacionado, constuyendo esta a partir de
        los datos del Nanopubrequest\n
        (ningun cambio se persistira en la base de datos este proceso debe ser controlado por usted mismo)\n

        retorna una tupla donde el primer parametro es el protocolo(Protocol) seguido de la nanopublicacion(Nanopublication)
        """
        protocol = self.protocolsRepo.getProtocol(
            uri=request.url, default=Protocol.fromAnnotation(request.step)
        )
        nanopublication = self.nanopubsRepo.getNanopub(
            protocol=protocol,
            id=request.id,
            default=Nanopublication(
                id=request.id,
                protocol=protocol,
                author=request.user,
                generatedAtTime=request.step.created,
            ),
        )
        # iterator for load bio_annotations
        def componentsIterator(component, annotation):
            component.rel_uris = self.assertion_strategy.bioAnnotations(annotation)
            return component

        # aply new changes in nanopub
        nanopublication.components = NanopublicationComponent.fromAnnotations(
            annotations=request.annotations, iterator=componentsIterator
        )
        rdf_nanopub = DBNanopublication(nanopublication)
        nanopublication.rdf_raw = rdf_nanopub.serialize("trig")
        return (protocol, nanopublication)
