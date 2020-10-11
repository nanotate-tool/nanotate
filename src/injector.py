from dependency_injector import providers, containers
from src.services.bioportal_service import BioPortalService
from src.services.nanopub_services import NanoPubServices
from src.adapters.bioportal_api import BioPortalApi
from src.adapters.assertion_strategy import BioportalAssertionStrategy


class Injector(containers.DeclarativeContainer):
    """
    Inyector de dependencias de la aplicacion
    """

    env = providers.Configuration()
    # components
    bioportalApi = providers.Singleton(BioPortalApi, settings=env.bioportal)
    # services
    bioportalService = providers.Factory(BioPortalService, bioportal_api=bioportalApi)
    nanopubsService = providers.Factory(NanoPubServices, bioportal_api=bioportalApi)
