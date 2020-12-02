from nanopub import NanopubClient
from .mock_injector import mock_injector
from src.adapters.bioportal_api import BioPortalApi
from src.db_mongo import MongoDb
from src.repositories import ProtocolsRepository, NanopublicationRepository, WorkflowsRepository
from src.services import (
    BioPortalService,
    NanoPubServices,
    ProtocolsService,
    StatsService,
    WorkflowsService
)

# checks each property provide by Injector has correct integrity

def test_injector_prop_env():
    """ env is instance """
    assert isinstance(mock_injector.env(), dict)
    assert isinstance(mock_injector.env.settings(), dict)
    assert isinstance(mock_injector.env.bioportal(), dict)
    assert isinstance(mock_injector.env.mongo(), dict)

def test_injector_prop_bioportal_api():
    assert isinstance(mock_injector.bioportalApi(), BioPortalApi)

def test_injector_prop_mongo_db():
    assert isinstance(mock_injector.mongoDb(), MongoDb)

def test_injector_prop_nanopub_client():
    assert isinstance(mock_injector.nanopubClient(), NanopubClient)

def test_injector_prop_protocols_repository():
    assert isinstance(mock_injector.protocolsRepository(), ProtocolsRepository)

def test_injector_prop_nanopubs_repository():
    assert isinstance(mock_injector.nanopubsRepository(), NanopublicationRepository)

def test_injector_prop_bioportal_service():
    assert isinstance(mock_injector.bioportalService(), BioPortalService)
    assert isinstance(mock_injector.bioportalService().bioPortal_API, BioPortalApi)

def test_injector_prop_nanopubs_service():
    assert isinstance(mock_injector.nanopubsService(), NanoPubServices)
    assert isinstance(mock_injector.nanopubsService().bioPortal_API, BioPortalApi)
    assert isinstance(mock_injector.nanopubsService().protocolsRepo, ProtocolsRepository)
    assert isinstance(mock_injector.nanopubsService().nanopubsRepo, NanopublicationRepository)
    assert isinstance(mock_injector.nanopubsService().nanopubremote, NanopubClient)
    assert isinstance(mock_injector.nanopubsService().settings, dict)

def test_injector_prop_protocols_service():
    assert isinstance(mock_injector.protocolsService(), ProtocolsService)
    assert isinstance(mock_injector.protocolsService().protocolsRepo, ProtocolsRepository)

def test_injector_prop_stats_service():
    assert isinstance(mock_injector.statsService(), StatsService)
    assert isinstance(mock_injector.statsService().nanopubsRepo, NanopublicationRepository)

def test_injector_prop_workflows_service():
    assert isinstance(mock_injector.workflows_service(), WorkflowsService)
    assert isinstance(mock_injector.workflows_service().workflows_repository, WorkflowsRepository)