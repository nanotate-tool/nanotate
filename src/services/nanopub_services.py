from src.models.annotation import Annotation
from src.models.nanopub_request import NanopubRequest
from src.adapters.annotation_nanopub import AnnotationNanopub
from src.adapters.db_nanopub import DBNanopub
from src.adapters.assertion_strategy import BioportalAssertionStrategy
from src.adapters.bioportal_api import BioPortalApi
from src.models import (
    Protocol,
    Nanopublication,
    NanopublicationComponent,
    PublicationInfo,
)
from src.repositories import NanopublicationRepository, ProtocolsRepository
from nanopub import NanopubClient
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
        nanopubremote: NanopubClient,
    ):
        self.bioPortal_API = bioportal_api
        self.assertion_strategy = BioportalAssertionStrategy(self.bioPortal_API)
        self.protocolsRepo = protocolsRepo
        self.nanopubsRepo = nanopubsRepo
        self.nanopubremote = nanopubremote

    def nanopubsByProtocol(
        self, protocol, json: bool = False, rdf_format: str = "trig"
    ) -> list:
        """
        retorna las nanopublicaciones realacionadas al protocolo pasado
        """
        nanopubs = self.nanopubsRepo.getNanopubsByProtocol(protocol=protocol)
        return list(
            map(
                lambda nanopub: self.__exportNanopublication(
                    nanopub=nanopub, json=json, rdf_format=rdf_format
                ),
                nanopubs,
            )
        )

    def nanopubById(self, id: str, json: bool = False, rdf_format: str = "trig"):
        """
        retorna la nanopublicacion relacionada al identificador pasado
        """
        nanopub = self.nanopubsRepo.getNanopub(id=id)
        return self.__exportNanopublication(
            nanopub=nanopub, json=json, rdf_format=rdf_format
        )

    def nanopubByArtifactCode(
        self, artifact_code: str, json: bool = False, rdf_format: str = "trig"
    ):
        """
        retorna la nanopublicacion relacionada al artifact_code pasado
        """
        nanopub = self.nanopubsRepo.getNanopubByArtifactCode(
            artifact_code=artifact_code
        )
        return self.__exportNanopublication(
            nanopub=nanopub, json=json, rdf_format=rdf_format
        )

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
        nanoPub = AnnotationNanopub(nanoPubRequest, self.assertion_strategy)
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
        rdf_nanopub = DBNanopub(nanopublication)
        # remote fairflows remote registration
        nanopublication.publication_info = self._publish_fairWorksFlowsNanopub(
            rdf_nanopub
        )
        print(nanopublication.publication_info)
        nanopublication.rdf_raw = rdf_nanopub.serialize("trig")
        return (protocol, nanopublication)

    def _publish_fairWorksFlowsNanopub(
        self, graph_nanopub: DBNanopub
    ) -> PublicationInfo:
        """
        registra la nanopublicacion pasada de forma remota utilizando la libreria ['nanopub'](https://github.com/fair-workflows/nanopub)
        """
        try:
            # remote fairflows remote registration
            publication_info = self.nanopubremote.publish(
                graph_nanopub.fairWorkflowsNanopub()
            )
            nanopub_uri: str = publication_info["nanopub_uri"]
            artifact_code = nanopub_uri.replace(graph_nanopub.np, "")
            published_at = "http://server.nanopubs.lod.labs.vu.nl"
            return PublicationInfo(
                nanopub_uri=nanopub_uri,
                artifact_code=artifact_code,
                published_at=published_at,
                canonical_url=published_at + "/" + artifact_code,
            )
        except Exception as e:
            print("have error on remote publish", e.__class__, e)
            return None

    def __exportNanopublication(
        self, nanopub: Nanopublication, json: bool = False, rdf_format: str = None
    ):
        if nanopub != None:
            if rdf_format != None and rdf_format != "trig":
                nanopub.rdf_raw = DBNanopub(nanopub).serialize(rdf_format)
            return nanopub.to_json_map() if json else nanopub
        else:
            return {"error": "not-found"}
