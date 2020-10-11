from dependency_injector import providers, containers
from src.services.bioportal_service import BioPortalService
from src.services.nanopub_services import NanoPubServices
from src.adapters.bioportal_api import BioPortalApi
from src.adapters.assertion_strategy import BioportalAssertionStrategy
from src.neo4j_db import Neo4jDB
from src.repositories.nanopublications_repository import NanoPublicationsRepository


class Injector(containers.DeclarativeContainer):
    """
    Inyector de dependencias de la aplicacion
    """

    env = providers.Configuration()
    # components
    bioportalApi = providers.Singleton(BioPortalApi, settings=env.bioportal)
    neo4jDB = providers.Singleton(
        Neo4jDB,
        http_url=env.neo4j.http_url,
        db=env.neo4j.db,
        uri=env.neo4j.uri,
        user=env.neo4j.user,
        password=env.neo4j.password
    )
    # services
    bioportalService = providers.Factory(BioPortalService, bioportal_api=bioportalApi)
    nanopubsService = providers.Factory(NanoPubServices, bioportal_api=bioportalApi)
    # repositories
    nanopublicationsRepository = providers.Factory(
        NanoPublicationsRepository, _db=neo4jDB
    )
