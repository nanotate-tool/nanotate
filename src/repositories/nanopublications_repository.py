from src.models import Nanopublication
from .workflows_repository import WorkflowsRepository


class NanopublicationRepository:

    PROTOCOL_MATCH = lambda protocol: {"$match": {"protocol": protocol}}
    TAG_FILTER = lambda tags, _in: {
        "$match": {
            "components.tags": {"$nin": [tags, "$components.tags"]}
            if not _in
            else {"$in": [tags, "$components.tags"]}
        }
    }
    GROUP_BY_TAGS = [
        {"$unwind": "$components.tags"},
        {"$group": {"_id": "$components.tags", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "label": "$_id", "count": "$count"}},
        {"$sort": {"count": -1}},
    ]
    GROUP_BY_ONTOLOGIES = [
        {"$unwind": "$components.ontologies"},
        {"$group": {"_id": "$components.ontologies", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "label": "$_id", "count": "$count"}},
        {"$sort": {"count": -1}},
    ]
    TERM_USED = [
        {"$group": {"_id": "$components.term", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "label": "$_id", "count": "$count"}},
    ]
    TERM_RELATED = [
        {"$unwind": "$components.rel_uris"},
        {
            "$group": {
                "_id": {
                    "term": "$components.term",
                    "uri": "$components.rel_uris",
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"count": -1}},
        {
            "$group": {
                "_id": "$_id.term",
                "uris": {"$addToSet": {"label": "$_id.uri", "count": "$count"}},
            }
        },
        {"$project": {"_id": 0, "term": "$_id", "uris": 1}},
    ]

    def __init__(self, workflows_repository: WorkflowsRepository = None):
        super().__init__()
        self.workflows_repository = workflows_repository

    def save(self, nanopub: Nanopublication) -> Nanopublication:
        """
        Realiza el almacenado de la nanopublicacion pasada
        """
        if nanopub != None:
            return nanopub.save()
        return None

    def delete(self, nanopub: Nanopublication) -> dict:
        """
        Realiza la eliminacion de la nanopublicacion pasada
        """
        if nanopub != None:
            nanopub.delete()
            return {"status": "ok"}

        return {"status": "error"}

    def getNanopub(
        self, id: str, protocol=None, default: Nanopublication = None
    ) -> Nanopublication:
        """
        Realiza la consulta de la nanopublicacion asociada a los filtros pasados.
        en caso de la consulta no retornar un valor se retornara el default pasado
        """
        query = {"id": id}
        if protocol != None:
            query["protocol"] = protocol
        db_nanopub = Nanopublication.objects(**query).first()
        if db_nanopub != None:
            self.__load_workflows_of_nanopub(db_nanopub)
            return db_nanopub

        return default

    def getNanopubsByProtocol(self, protocol: str) -> list:
        """
        retorna la lista de nanopublicaciones asociadas a la uri del protocolo pasado
        """
        return list(
            map(
                (lambda nanopub: self.__load_workflows_of_nanopub(nanopub=nanopub)),
                Nanopublication.objects(protocol=protocol),
            )
        )

    def getNanopubByArtifactCode(self, artifact_code: str) -> Nanopublication:
        """
        retorna la primera Nanopublication relacionada al artifact_code pasado, este se relaciona
        con el PublicationInfo.artifact_code de la misma
        """
        db_nanopub = Nanopublication.objects(
            publication_info__artifact_code=artifact_code
        ).first()
        return self.__load_workflows_of_nanopub(nanopub=db_nanopub)

    def getEssentialStats(self, protocol: str = None):
        """
        retorna las estadisticas esenciales del protocolo si este se envia.
        (en caso de no enviarlo se calcula de forma global)
        esta incluye estadisticas de tags, ontologias, terminos
        [\n
            {
                "ontologies": [{ "label":<tag>, "count":<number of use> }],
                "tags": [{ "label":<tag>, "count":<number of use> }],
                "terms": {
                    "related":[
                        { "term":<term>, "uris":[ {"label":<uri>,"count":<use> } ] }
                    ],
                    "used": [{ "label":<term>, "count":<number of use> }]
                }
            }
        \n]
        """
        not_step_tag_filter = [NanopublicationRepository.TAG_FILTER("step", False)]
        pipeline = NanopublicationRepository._withProtocolFilter(
            protocol,
            [
                {"$unwind": {"path": "$components"}},
                {
                    "$facet": {
                        "tags": self.GROUP_BY_TAGS,
                        "ontologies": self.GROUP_BY_ONTOLOGIES,
                        "terms_used": not_step_tag_filter + self.TERM_USED,
                        "terms_related": not_step_tag_filter + self.TERM_RELATED,
                    }
                },
                {
                    "$project": {
                        "tags": 1,
                        "ontologies": 1,
                        "terms": {"used": "$terms_used", "related": "$terms_related"},
                    }
                },
            ],
        )
        return list(Nanopublication.objects().aggregate(pipeline))

    def getTermStats(self, protocol: str = None) -> list:
        """
        retorna las estadisticas de uso de de las terminos para el protocolo si este se envia,
        (en caso de no enviarlo se calcula de forma global)
        [\n
            "related":[
                { "term":<term>, "uris":[ {"label":<uri>,"count":<use> } ] }
            ],
            "used": [{ "label":<term>, "count":<number of use> }]
        \n]
        """
        not_step_tag_filter = [NanopublicationRepository.TAG_FILTER("step", False)]
        pipeline = NanopublicationRepository._withProtocolFilter(
            protocol,
            [
                {"$unwind": "$components"},
                {
                    "$facet": {
                        "used": not_step_tag_filter + self.TERM_USED,
                        "related": not_step_tag_filter + self.TERM_RELATED,
                    }
                },
            ],
        )
        return list(Nanopublication.objects().aggregate(pipeline))

    def getTagsStats(self, protocol: str = None) -> list:
        """
        retorna las estadisticas de uso de de las tags para el protocolo si este se envia,
        (en caso de no enviarlo se calcula de forma global)
        [\n
            { "label":<tag>, "count":<number of use> }
        \n]
        """
        pipeline = NanopublicationRepository._withProtocolFilter(
            protocol, [{"$unwind": "$components"}] + self.GROUP_BY_TAGS
        )
        return list(Nanopublication.objects().aggregate(pipeline))

    def getOntologiesStats(self, protocol: str = None) -> list:
        """
        retorna las estadisticas de uso de de las ontologias para el protocolo si este se envia,
        (en caso de no enviarlo se calcula de forma global)
        [\n
            { "label":<tag>, "count":<number of use> }
        \n]
        """
        pipeline = NanopublicationRepository._withProtocolFilter(
            protocol, [{"$unwind": "$components"}] + self.GROUP_BY_ONTOLOGIES
        )
        return list(Nanopublication.objects().aggregate(pipeline))

    @staticmethod
    def _withProtocolFilter(protocol: str, pipeline: list):
        final_pipeline = (
            [NanopublicationRepository.PROTOCOL_MATCH(protocol)]
            if protocol != None
            else []
        ) + pipeline
        return final_pipeline

    def __load_workflows_of_nanopub(self, nanopub: Nanopublication) -> list:
        """
        shortcut and validator to load associated workflows of passed nanopub
        """
        if self.workflows_repository != None and nanopub != None:
            workflows = self.workflows_repository.get_workflows_of_nanopub(
                nanopub_id=nanopub.id
            )
            nanopub.workflows = workflows

        return nanopub
