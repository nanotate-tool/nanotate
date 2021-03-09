from src.models import Nanopublication
from src.repositories import NanopublicationRepository
from src.utils.site_metadata_puller import clean_url_with_settings


class StatsService:
    """
    Servicio encargado de proveer las estadisticas posibles de la app
    """

    def __init__(self, nanopubs_repo: NanopublicationRepository, settings: dict):
        self.nanopubs_repo = nanopubs_repo
        self.settings = settings

    def essentials(self, protocol: str = None, users: list = None, tags: list = None):
        results = self.nanopubs_repo.get_essential_stats(
            protocol=self.__resolve_protocol(protocol), users=users, tags=tags
        )
        return results

    def for_tags(
        self, protocol: str = None, users: list = None, tags: list = None, **kwargs
    ):
        results = self.nanopubs_repo.get_tags_stats(
            protocol=self.__resolve_protocol(protocol), tags=tags, users=users
        )
        return results

    def for_terms(
        self, protocol: str = None, users: list = None, tags: list = None, **kwargs
    ):
        results = self.nanopubs_repo.get_term_stats(
            protocol=self.__resolve_protocol(protocol), tags=tags, users=users
        )
        return results

    def stats_of_nanopubs_by_user(self, protocol: str = None, **kwargs):
        results = self.nanopubs_repo.get_nanopubs_by_author_stats(
            protocol=self.__resolve_protocol(protocol=protocol)
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
        result = self.nanopubs_repo.nanopubs_stats(
            protocol=protocol, users=users, tags=tags, page=page
        )
        return result

    def for_ontologies(
        self, protocol: str = None, users: list = None, tags: list = None, **kwargs
    ):
        results = self.nanopubs_repo.get_ontologies_stats(
            protocol=self.__resolve_protocol(protocol), tags=tags, users=users
        )
        return results

    def __resolve_protocol(self, protocol: str) -> str:
        return (
            clean_url_with_settings(url=protocol, settings=self.settings)
            if protocol != None and protocol != "global"
            else None
        )
