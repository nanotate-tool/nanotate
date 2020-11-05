from dependency_injector import providers, containers
from src.services.bioportal_service import BioPortalService
from src.services.nanopub_services import NanoPubServices
from src.services.protocols_service import ProtocolsService
from src.services.stats_service import StatsService
from src.adapters.bioportal_api import BioPortalApi
from src.adapters.assertion_strategy import BioportalAssertionStrategy
from .db_mongo import MongoDb
from .repositories import NanopublicationRepository, ProtocolsRepository
from nanopub import NanopubClient


class Injector(containers.DeclarativeContainer):
    """
    Inyector de dependencias de la aplicacion
    """

    env = providers.Configuration()
    # components
    bioportalApi = providers.Singleton(BioPortalApi, settings=env.bioportal)
    mongoDb = providers.Singleton(
        MongoDb,
        host=env.mongo.host,
        database=env.mongo.database,
        port=env.mongo.port,
        auth=env.mongo.auth,
    )
    nanopubClient = providers.Singleton(NanopubClient)
    # respos
    protocolsRepository = providers.Singleton(ProtocolsRepository)
    nanopubsRepository = providers.Singleton(NanopublicationRepository)
    # services
    bioportalService = providers.Factory(BioPortalService, bioportal_api=bioportalApi)
    nanopubsService = providers.Factory(
        NanoPubServices,
        bioportal_api=bioportalApi,
        nanopubsRepo=nanopubsRepository,
        protocolsRepo=protocolsRepository,
        nanopubremote=nanopubClient,
    )
    protocolsService = providers.Factory(
        ProtocolsService, protocolsRepo=protocolsRepository
    )
    statsService = providers.Factory(StatsService, nanopubsRepo=nanopubsRepository)
