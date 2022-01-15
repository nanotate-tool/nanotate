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
import math
from .bioportal_service import BioPortalService


class NanoPubServices:
    """
    Servicio para el manejo de las Nanopublicaciones
    """

    def __init__(
        self,
        bioportal_api: BioPortalApi,
        protocols_repo: ProtocolsRepository,
        nanopubs_repo: NanopublicationRepository,
        nanopubremote: NanopubClient,
        workflows_service: WorkflowsService,
        settings: dict,
    ):
        self.bioportal_api = bioportal_api
        self.assertion_strategy = BioportalAssertionStrategy(self.bioportal_api)
        self.protocols_repo = protocols_repo
        self.nanopubs_repo = nanopubs_repo
        self.nanopubremote = nanopubremote
        self.settings = settings
        self.workflows_service = workflows_service

    def nanopubs_by_protocol(
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
        nanopubs = self.nanopubs_repo.get_nanopubs_by_protocol(protocol=clean_protocol)
        return list(
            map(
                lambda nanopub: self.__export_nanopublication(
                    nanopub=nanopub, json=json, rdf_format=rdf_format
                ),
                nanopubs,
            )
        )

    def nanopub_by_id(
        self,
        id: str,
        json: bool = False,
        rdf_format: str = "trig",
        for_compare: bool = False,
    ):
        """
        retorna la nanopublicacion relacionada al identificador pasado
        """
        nanopub = self.nanopubs_repo.get_nanopub(id=id)
        return self.__export_nanopublication(
            nanopub=nanopub, json=json, rdf_format=rdf_format, temp_rdf=for_compare
        )

    def nanopub_by_artifact_code(
        self,
        artifact_code: str,
        json: bool = False,
        rdf_format: str = "trig",
        for_compare: bool = False,
    ):
        """
        retorna la nanopublicacion relacionada al artifact_code pasado
        """
        nanopub = self.nanopubs_repo.get_nanopub_by_artifact_code(
            artifact_code=artifact_code
        )
        return self.__export_nanopublication(
            nanopub=nanopub, json=json, rdf_format=rdf_format, tempRdf=for_compare
        )

    def register_from_annotations(self, annotations: list):
        """
        Realiza el proceso de registro de las nanopublicaciones que se puedan
        construir a partir de la lista de anotaciones pasadas
        """
        nanopub_request = NanopubRequest.splitAnnotations(annotations)
        mapped = {"status": "ok"}
        for request in nanopub_request:
            result = self.register_from_nanopub_request(request)
            if result["status"] != "ok":
                mapped["status"] = "with-errors"
            mapped[request.id] = result
        return mapped

    def delete_nanopublication(self, nanopublication_key: str):
        """
        realiza la eliminacion de la nanopublicacion relacionada al identificador pasado
        """
        nanopub = self.nanopubs_repo.get_nanopub(nanopublication_key)
        if nanopub != None:
            workflows = list(nanopub.workflows)
            result = self.nanopubs_repo.delete(nanopub)
            if result["status"] == "ok":
                self._retract_fairworksflows_nanopub(nanopublication=nanopub)
                # deleting related workflows
                if len(workflows) > 0:
                    for workflow in workflows:
                        print("deleting workflow with id ", workflow.id)
                        self.workflows_service.delete(workflow_key=workflow.id)
            return result
        else:
            return {"status": "error", "message": "Nanopublication not found"}

    def register_from_nanopub_request(self, request: NanopubRequest):
        """
        Realiza el registro de la nanopublicacion contenida en el NanopubRequest pasado
        """
        (protocol, nanopub) = self.__update_nanopub_and_protocol(request)
        return {
            "protocol": protocol.to_json_map(),
            "nanopub": nanopub.to_json_map(),
            "status": "ok",
        }

    def preview_annotations(self, annotations: list, format: str = "trig"):
        """
        realiza la generacion de la info de las 'NanopubRequest' que se puedan calcular a partir de las annotaciones pasadas\n
        see #previewNanoPubRequest
        """
        nanopub_request_list = NanopubRequest.splitAnnotations(annotations)
        previews = []
        for nanopub_request in nanopub_request_list:
            previews.append(self.preview_nanopub_request(nanopub_request, format))
        return previews

    def preview_nanopub_request(
        self, nanopub_request: NanopubRequest, rdf_format: str = "trig"
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
        rdf_format = rdf_format if rdf_format != None else "trig"
        nanopub = AnnotationNanopub(
            nanopub_request, self.assertion_strategy, self.settings
        )
        return {
            "id": nanopub_request.id,
            "user": nanopub_request.user,
            "url": nanopub_request.url,
            "rdf": nanopub.serialize(rdf_format),
            "format": rdf_format,
        }

    def all_nanopubs(self, page: int = 1, projection_mode: str = None):
        data = self.nanopubs_repo.all_nanopubs(page, 100, projection_mode)
        return data

    def all_nanopubs_metadata(self, page: int =1):
        metadata = self.nanopubs_repo.all_nanopubs_metadata(100)
        max_pages = math.ceil(metadata['totalRecords'] / metadata['size'])
        page = max_pages if page is None else page
        args = {
            'minpages': 1,
            'nextpage': int(page) + 1 if page < max_pages else 0,
            'prevpage': int(page) - 1 if page > 1 else 0,
            'maxpages': max_pages,
            'begun': (page - 1) * metadata['size'],
            'page': page
        }
        return args

    def __update_nanopub_and_protocol(self, request: NanopubRequest) -> tuple:
        """
        realiza la actualizacion o creacion de la nanopublicacion y su protocolo realacionado, constuyendo esta a partir de
        los datos del Nanopubrequest\n
        (los cambios realizados se persistiran)\n

        retorna una tupla donde el primer parametro es el protocolo(Protocol) seguido de la nanopublicacion(Nanopublication)
        """
        clean_url = clean_url_with_settings(url=request.url, settings=self.settings)
        protocol = self.protocols_repo.get_protocol(
            uri=clean_url,
            default=Protocol.fromAnnotation(request.step, settings=self.settings),
        )
        nanopublication = self.nanopubs_repo.get_nanopub(
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
        def components_iterator(component, annotation):
            bio_annotations = list(
                map(
                    lambda ontology: BioPortalService.annotation_parse(ontology),
                    self.assertion_strategy.bio_annotations(
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
            annotations=request.annotations, iterator=components_iterator
        )
        # previous nanopub uri if exist
        previous_nanopub_uri = (
            nanopublication.publication_info.nanopub_uri
            if nanopublication.publication_info != None
            else None
        )
        # nanopublication remote registration
        rdf_nanopub = DBNanopub(db_nano_pub=nanopublication, settings=self.settings)
        nanopublication.publication_info = self._publish_fairworksflows_nanopub(
            rdf_nanopub
        )
        # fetch remote rdf for local mirror
        if nanopublication.publication_info != None:
            rdf_nanopub = DBNanopub(
                db_nano_pub=nanopublication,
                settings=self.settings,
                np_client=self.nanopubremote,
            )
        nanopublication.rdf_raw = rdf_nanopub.serialize("trig")
        # persist data
        self.nanopubs_repo.save(nanopub=nanopublication)
        self.protocols_repo.save(protocol=protocol)
        # retraction of previous remote nanopublication
        if previous_nanopub_uri != None:
            self._retract_fairworksflows_nanopub(nanopub_uri=previous_nanopub_uri)

        return (protocol, nanopublication)

    def _publish_fairworksflows_nanopub(
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

    def _retract_fairworksflows_nanopub(
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

    def __export_nanopublication(
        self,
        nanopub: Nanopublication,
        json: bool = False,
        rdf_format: str = None,
        temp_rdf: bool = False,
    ):
        if nanopub != None:
            if rdf_format != None and rdf_format != "trig":
                nanopub.rdf_raw = DBNanopub(
                    db_nano_pub=nanopub, settings=self.settings, from_db_rdf=(not temp_rdf)
                ).serialize(rdf_format)
            return nanopub.to_json_map() if json else nanopub
        else:
            return {"error": "not-found"}
