from src.models import Nanopublication
from src.repositories import NanopublicationRepository


class StatsService:
    """
    Servicio encargado de proveer las estadisticas posibles de la app
    """

    def __init__(self, nanopubsRepo: NanopublicationRepository):
        self.nanopubsRepo = nanopubsRepo

    def essentials(self, protocol: str = None):
        results = self.nanopubsRepo.getEssentialStats(self.__resolveProtocol(protocol))
        return results

    def forTags(self, protocol: str = None):
        results = self.nanopubsRepo.getTagsStats(self.__resolveProtocol(protocol))
        return results

    def forTerms(self, protocol: str = None):
        results = self.nanopubsRepo.getTermStats(self.__resolveProtocol(protocol))
        return results

    def forOntologies(self, protocol: str = None):
        results = self.nanopubsRepo.getOntologiesStats(self.__resolveProtocol(protocol))
        return results

    def __resolveProtocol(self, protocol: str) -> str:
        return protocol if protocol != None and protocol != "global" else None
