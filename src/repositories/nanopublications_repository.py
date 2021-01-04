from src.models import Nanopublication
from .workflows_repository import WorkflowsRepository


class NanopublicationRepository:

    PROTOCOL_MATCH = lambda protocol: {"$match": {"protocol": protocol}}
    AUTHOR_FILTER = lambda users: {"$match": {"author": {"$in": users}}}
    GENERIC_REDUCE = lambda input_field: {
        "$reduce": {
            "input": input_field,
            "initialValue": "",
            "in": {"$concat": ["$$value", "$$this", ",\n"]},
        }
    }
    TAG_FILTER = lambda tags, _in: {
        "$match": {
            "components.tags": {"$nin": [tags, "$components.tags"]}
            if not _in
            else {"$in": tags}
        }
    }
    GROUP_BY_TAGS = lambda tags: (
        [
            {"$unwind": "$components.tags"},
        ]
        + ([{"$match": {"components.tags": {"$in": tags}}}] if tags else [])
        + [
            {"$group": {"_id": "$components.tags", "count": {"$sum": 1}}},
            {"$project": {"_id": 0, "label": "$_id", "count": "$count"}},
            {"$sort": {"count": -1}},
        ]
    )
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

    def getEssentialStats(
        self, protocol: str = None, users: list = None, tags: list = None
    ):
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
            pipeline=[
                {"$unwind": {"path": "$components"}},
                {
                    "$facet": {
                        "tags": NanopublicationRepository.GROUP_BY_TAGS(tags),
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
            protocol=protocol,
            users=users,
            tags=tags,
        )
        return list(Nanopublication.objects().aggregate(pipeline))

    def getTermStats(
        self, protocol: str = None, users: list = None, tags: list = None
    ) -> list:
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
            pipeline=[
                {"$unwind": "$components"},
                {
                    "$facet": {
                        "used": not_step_tag_filter + self.TERM_USED,
                        "related": not_step_tag_filter + self.TERM_RELATED,
                    }
                },
            ],
            protocol=protocol,
            tags=tags,
            users=users,
        )
        return list(Nanopublication.objects().aggregate(pipeline))

    def getTagsStats(
        self, protocol: str = None, users: list = None, tags: list = None
    ) -> list:
        """
        retorna las estadisticas de uso de de las tags para el protocolo si este se envia,
        (en caso de no enviarlo se calcula de forma global)
        [\n
            { "label":<tag>, "count":<number of use> }
        \n]
        """
        pipeline = NanopublicationRepository._withProtocolFilter(
            pipeline=[{"$unwind": "$components"}]
            + NanopublicationRepository.GROUP_BY_TAGS(tags),
            protocol=protocol,
            tags=tags,
            users=users,
        )
        return list(Nanopublication.objects().aggregate(pipeline))

    def getOntologiesStats(
        self, protocol: str = None, users: list = None, tags: list = None
    ) -> list:
        """
        retorna las estadisticas de uso de de las ontologias para el protocolo si este se envia,
        (en caso de no enviarlo se calcula de forma global)
        [\n
            { "label":<tag>, "count":<number of use> }
        \n]
        """
        pipeline = NanopublicationRepository._withProtocolFilter(
            pipeline=[{"$unwind": "$components"}] + self.GROUP_BY_ONTOLOGIES,
            protocol=protocol,
            users=users,
            tags=tags,
        )
        return list(Nanopublication.objects().aggregate(pipeline))

    def get_nanopubs_by_author_stats(self, protocol: str = None):
        """
        returns the amount of annotations make for user in a protocol
        if this is sended otherwise returns for all protocols
        [\n
            { "label":<author>, "count":<number of nano publications> }
        \n]
        """
        pipeline = NanopublicationRepository._withProtocolFilter(
            pipeline=[
                {"$group": {"_id": "$author", "count": {"$sum": 1}}},
                {"$project": {"_id": 0, "label": "$_id", "count": "$count"}},
            ],
            protocol=protocol,
        )
        return list(Nanopublication.objects().aggregate(pipeline))

    def nanopubs_stats(
        self, protocol: str = None, users: list = None, tags: list = None, page: int = 1
    ) -> list:
        conditions = NanopublicationRepository._withProtocolFilter(
            pipeline=[{"$unwind": "$components"}],
            protocol=protocol,
            tags=tags,
            users=users,
        )
        projection = [
            {
                "$project": {
                    "_id": 0,
                    "id": "$components.id",
                    "text": "$components.term",
                    "tag": NanopublicationRepository.GENERIC_REDUCE("$components.tags"),
                    "text_position": {
                        "$concat": [
                            {"$toString": "$components.text_position.start"},
                            ",",
                            {"$toString": "$components.text_position.end"},
                        ]
                    },
                    "ontologies": NanopublicationRepository.GENERIC_REDUCE(
                        "$components.ontologies_info.url"
                    ),
                    "ontologies_label": NanopublicationRepository.GENERIC_REDUCE(
                        "$components.ontologies_info.label"
                    ),
                    "ontologies_term": NanopublicationRepository.GENERIC_REDUCE(
                        "$components.ontologies_info.term"
                    ),
                }
            }
        ]
        (empty, pipeline) = NanopublicationRepository._with_pagination(
            projection=projection, conditions=conditions, page=page, size=40
        )
        data = list(Nanopublication.objects().aggregate(pipeline))
        return data[0] if len(data) == 1 else empty

    @staticmethod
    def _withProtocolFilter(
        pipeline: list, protocol: str = None, users: list = None, tags: list = None
    ):
        final_pipeline = (
            (
                [NanopublicationRepository.PROTOCOL_MATCH(protocol)]
                if protocol != None and protocol != "global"
                else []
            )
            + (
                [NanopublicationRepository.AUTHOR_FILTER(users)]
                if users != None and len(users) > 0
                else []
            )
            + (
                [NanopublicationRepository.TAG_FILTER(tags, True)]
                if tags != None and len(tags) > 0
                else []
            )
            + pipeline
        )
        return final_pipeline

    @staticmethod
    def _with_pagination(
        conditions: list, projection=list, page: int = 1, size: int = 10
    ):
        page = 1 if page < 1 else page
        skip = (page - 1) * size
        limit = skip + size
        return (
            {"data": [], "page": {"totalRecords": 0, "page": page, "size": size}},
            conditions
            + [
                {
                    "$facet": {
                        "page": [
                            {"$group": {"_id": "1", "count": {"$sum": 1}}},
                            {
                                "$project": {
                                    "_id": 0,
                                    "totalRecords": "$count",
                                    "page": {"$literal": page},
                                    "size": {"$literal": size},
                                }
                            },
                        ],
                        "data": projection + [{"$skip": skip}, {"$limit": limit}],
                    },
                },
                {"$unwind": "$page"},
                {"$project": {"page": 1, "data": 1}},
            ],
        )

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
