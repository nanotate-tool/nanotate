from src.models import Nanopublication
from src.repositories import NanopublicationRepository
from src.utils.site_metadata_puller import clean_url_with_settings


class StatsService:
    """
    Servicio encargado de proveer las estadisticas posibles de la app
    """

    def __init__(self, nanopubsRepo: NanopublicationRepository, settings: dict):
        self.nanopubsRepo = nanopubsRepo
        self.settings = settings

    def essentials(self, protocol: str = None, users: list = None, tags: list = None):
        results = self.nanopubsRepo.getEssentialStats(
            protocol=self.__resolveProtocol(protocol), users=users, tags=tags
        )
        return results

    def forTags(
        self, protocol: str = None, users: list = None, tags: list = None, **kwargs
    ):
        results = self.nanopubsRepo.getTagsStats(
            protocol=self.__resolveProtocol(protocol), tags=tags, users=users
        )
        return results

    def forTerms(
        self, protocol: str = None, users: list = None, tags: list = None, **kwargs
    ):
        results = self.nanopubsRepo.getTermStats(
            protocol=self.__resolveProtocol(protocol), tags=tags, users=users
        )
        return results

    def stats_of_nanopubs_by_user(self, protocol: str = None, **kwargs):
        results = self.nanopubsRepo.get_nanopubs_by_author_stats(
            protocol=self.__resolveProtocol(protocol=protocol)
        )
        return results

    def stats_of_nanopubs(
        self,
        protocol: str = None,
        users: list = None,
        tags: list = None,
        page: int = 1,
        **kwargs
    ):
        result = self.nanopubsRepo.nanopubs_stats(
            protocol=protocol, users=users, tags=tags, page=page
        )
        return result

    def forOntologies(
        self, protocol: str = None, users: list = None, tags: list = None, **kwargs
    ):
        results = self.nanopubsRepo.getOntologiesStats(
            protocol=self.__resolveProtocol(protocol), tags=tags, users=users
        )
        return results

    def __resolveProtocol(self, protocol: str) -> str:
        return (
            clean_url_with_settings(url=protocol, settings=self.settings)
            if protocol != None and protocol != "global"
            else None
        )
