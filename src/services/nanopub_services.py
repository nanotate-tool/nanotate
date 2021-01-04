from .workflows_service import WorkflowsService
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
    OntologyInfo,
)
from src.repositories import (
    NanopublicationRepository,
    ProtocolsRepository,
)
from nanopub import NanopubClient
from urllib.parse import urlparse
from src.utils.site_metadata_puller import clean_url_with_settings
import json
from .bioportal_service import BioPortalService


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
        workflows_service: WorkflowsService,
        settings: dict,
    ):
        self.bioPortal_API = bioportal_api
        self.assertion_strategy = BioportalAssertionStrategy(self.bioPortal_API)
        self.protocolsRepo = protocolsRepo
        self.nanopubsRepo = nanopubsRepo
        self.nanopubremote = nanopubremote
        self.settings = settings
        self.workflows_service = workflows_service

    def nanopubsByProtocol(
        self, protocol: str, json: bool = False, rdf_format: str = "trig"
    ) -> list:
        """
        returns the nanopublications related to passed protocol\n
            params:
                protocol: url of protocol
                json: true for return data in json format, false otherwise
                rdf_format: valid format for nanopublication rdf
        """
        clean_protocol = clean_url_with_settings(url=protocol, settings=self.settings)
        nanopubs = self.nanopubsRepo.getNanopubsByProtocol(protocol=clean_protocol)
        return list(
            map(
                lambda nanopub: self.__exportNanopublication(
                    nanopub=nanopub, json=json, rdf_format=rdf_format
                ),
                nanopubs,
            )
        )

    def nanopubById(
        self,
        id: str,
        json: bool = False,
        rdf_format: str = "trig",
        for_compare: bool = False,
    ):
        """
        retorna la nanopublicacion relacionada al identificador pasado
        """
        nanopub = self.nanopubsRepo.getNanopub(id=id)
        return self.__exportNanopublication(
            nanopub=nanopub, json=json, rdf_format=rdf_format, tempRdf=for_compare
        )

    def nanopubByArtifactCode(
        self,
        artifact_code: str,
        json: bool = False,
        rdf_format: str = "trig",
        for_compare: bool = False,
    ):
        """
        retorna la nanopublicacion relacionada al artifact_code pasado
        """
        nanopub = self.nanopubsRepo.getNanopubByArtifactCode(
            artifact_code=artifact_code
        )
        return self.__exportNanopublication(
            nanopub=nanopub, json=json, rdf_format=rdf_format, tempRdf=for_compare
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

    def deleteNanopublication(self, nanopublication_key: str):
        """
        realiza la eliminacion de la nanopublicacion relacionada al identificador pasado
        """
        nanopub = self.nanopubsRepo.getNanopub(nanopublication_key)
        if nanopub != None:
            workflows = list(nanopub.workflows)
            result = self.nanopubsRepo.delete(nanopub)
            if result["status"] == "ok":
                self._retract_fairWorksFlowsNanopub(nanopublication=nanopub)
                # deleting related workflows
                if len(workflows) > 0:
                    for workflow in workflows:
                        print("deleting workflow with id ", workflow.id)
                        self.workflows_service.delete(workflow_key=workflow.id)
            return result
        else:
            return {"status": "error", "message": "Nanopublication not found"}

    def registerFromNanopubRequest(self, request: NanopubRequest):
        """
        Realiza el registro de la nanopublicacion contenida en el NanopubRequest pasado
        """
        (protocol, nanopub) = self.__updateNanopubAndProtocol(request)
        return {
            "protocol": protocol.to_json_map(),
            "nanopub": nanopub.to_json_map(),
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
        nanoPub = AnnotationNanopub(
            nanoPubRequest, self.assertion_strategy, self.settings
        )
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
        (los cambios realizados se persistiran)\n

        retorna una tupla donde el primer parametro es el protocolo(Protocol) seguido de la nanopublicacion(Nanopublication)
        """
        clean_url = clean_url_with_settings(url=request.url, settings=self.settings)
        protocol = self.protocolsRepo.getProtocol(
            uri=clean_url,
            default=Protocol.fromAnnotation(request.step, settings=self.settings),
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
            bio_annotations = list(
                map(
                    lambda ontology: BioPortalService.annotationParse(ontology),
                    self.assertion_strategy.bioAnnotations(
                        annotation=annotation, full=True
                    ),
                )
            )
            component.rel_uris = list(
                map(lambda ontology: ontology["id"], bio_annotations)
            )
            component.ontologies_info = list(
                map(
                    lambda ontology: OntologyInfo(
                        label=ontology["ontologyLabel"],
                        url=ontology["id"],
                        term=ontology["prefLabel"],
                        selector=ontology["selector"][0],
                    ),
                    bio_annotations,
                )
            )
            return component

        # aply new changes in nanopub
        nanopublication.components = NanopublicationComponent.fromAnnotations(
            annotations=request.annotations, iterator=componentsIterator
        )
        # previous nanopub uri if exist
        previous_nanopub_uri = (
            nanopublication.publication_info.nanopub_uri
            if nanopublication.publication_info != None
            else None
        )
        # nanopublication remote registration
        rdf_nanopub = DBNanopub(dbnanopub=nanopublication, settings=self.settings)
        nanopublication.publication_info = self._publish_fairWorksFlowsNanopub(
            rdf_nanopub
        )
        # fetch remote rdf for local mirror
        if nanopublication.publication_info != None:
            rdf_nanopub = DBNanopub(
                dbnanopub=nanopublication,
                settings=self.settings,
                npClient=self.nanopubremote,
            )
        nanopublication.rdf_raw = rdf_nanopub.serialize("trig")
        # persist data
        self.nanopubsRepo.save(nanopub=nanopublication)
        self.protocolsRepo.save(protocol=protocol)
        # retraction of previous remote nanopublication
        if previous_nanopub_uri != None:
            self._retract_fairWorksFlowsNanopub(nanopub_uri=previous_nanopub_uri)

        return (protocol, nanopublication)

    def _publish_fairWorksFlowsNanopub(
        self, graph_nanopub: DBNanopub
    ) -> PublicationInfo:
        """
        registra la nanopublicacion pasada de forma remota utilizando la libreria ['nanopub'](https://github.com/fair-workflows/nanopub)
        """
        try:
            # remote fairflows remote registration
            publication_info = self.nanopubremote.publish(graph_nanopub.nanopub)
            nanopub_uri: str = publication_info["nanopub_uri"]
            nanopub_uri_p = urlparse(nanopub_uri)
            artifact_code = nanopub_uri_p.path.rsplit("/", 1)[-1]
            return PublicationInfo(
                nanopub_uri=nanopub_uri,
                artifact_code=artifact_code,
            )
        except Exception as e:
            print("have error on remote publish", e.__class__, e)
            raise e

    def _retract_fairWorksFlowsNanopub(
        self, nanopublication: Nanopublication = None, nanopub_uri: str = None
    ):
        """
        makes the process of retraction of nanopublication that was published remotely
        """
        try:
            nanopub_uri = (
                nanopublication.publication_info.nanopub_uri
                if nanopublication != None and nanopublication.publication_info != None
                else nanopub_uri
            )

            if nanopub_uri != None:
                self.nanopubremote.retract(uri=nanopub_uri, force=True)
            else:
                raise "empty nanopub_uri for retract"
        except Exception as e:
            print("have error on remote retracting", e.__class__, e)
            return None

    def __exportNanopublication(
        self,
        nanopub: Nanopublication,
        json: bool = False,
        rdf_format: str = None,
        tempRdf: bool = False,
    ):
        if nanopub != None:
            if rdf_format != None and rdf_format != "trig":
                nanopub.rdf_raw = DBNanopub(
                    dbnanopub=nanopub, settings=self.settings, fromDbrdf=(not tempRdf)
                ).serialize(rdf_format)
            return nanopub.to_json_map() if json else nanopub
        else:
            return {"error": "not-found"}
