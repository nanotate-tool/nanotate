from dependency_injector import providers, containers
from src.adapters.bioportal_api import BioPortalApi
from src.adapters.assertion_strategy import BioportalAssertionStrategy
from src.services import (
    BioPortalService,
    NanoPubServices,
    ProtocolsService,
    StatsService,
    WorkflowsService,
)
from .db_mongo import MongoDb
from .repositories import (
    NanopublicationRepository,
    ProtocolsRepository,
    WorkflowsRepository,
)
from nanopub import NanopubClient

negator = lambda arg1: not arg1
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
    nanopubTest = providers.Callable(negator, env.settings.production)
    nanopubClient = providers.Singleton(
        NanopubClient, use_test_server=nanopubTest
    )
    # respos
    protocolsRepository = providers.Singleton(ProtocolsRepository)
    workflows_repository = providers.Singleton(WorkflowsRepository)
    nanopubsRepository = providers.Singleton(
        NanopublicationRepository, workflows_repository=workflows_repository
    )
    # services
    bioportalService = providers.Factory(BioPortalService, bioportal_api=bioportalApi)
    protocolsService = providers.Factory(
        ProtocolsService,
        protocols_repo=protocolsRepository,
        settings=env.settings,
    )
    statsService = providers.Factory(
        StatsService, nanopubs_repo=nanopubsRepository, settings=env.settings
    )
    workflows_service = providers.Factory(
        WorkflowsService,
        workflows_repository=workflows_repository,
        nanopubs_repository=nanopubsRepository,
        settings=env.settings,
        nanopub_client=nanopubClient,
    )
    nanopubsService = providers.Factory(
        NanoPubServices,
        bioportal_api=bioportalApi,
        nanopubs_repo=nanopubsRepository,
        protocols_repo=protocolsRepository,
        nanopubremote=nanopubClient,
        workflows_service=workflows_service,
        settings=env.settings,
    )
