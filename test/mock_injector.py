# mock injector
import unittest.mock
import rdflib
from nanopub import Publication
from src.injector import Injector
from nanopub import NanopubClient
from .mongo_mock import MockMongoDb
from .constants import (
    published_trusted_uri,
    retracted_trusted_uri,
    expected_rdf,
    workflow_trusted_uri,
    workflow_retract_trusted_uri,
)
from src.services import WorkflowsService


mock_injector = Injector()
mock_injector.env.from_yaml("environment/environment_dev.yml")
mock_injector.mongoDb.override(MockMongoDb())
# manual connection to mongomock
mock_injector.mongoDb().connect()
# make mock for nanopubclient
mock_nanopub_client = unittest.mock.Mock(NanopubClient)
mock_nanopub_client.publish = unittest.mock.MagicMock(
    return_value={"nanopub_uri": published_trusted_uri}
)
mock_nanopub_client.retract = unittest.mock.MagicMock(
    return_value={"nanopub_uri": retracted_trusted_uri}
)

nanopub_rdf = rdflib.ConjunctiveGraph()
nanopub_rdf.parse(data=expected_rdf, format="trig")
nanopub = Publication(rdf=nanopub_rdf)
mock_nanopub_client.fetch = unittest.mock.MagicMock(return_value=nanopub)

mock_injector.nanopubClient.override(mock_nanopub_client)

# make mock for workflowsService

mock_workflows_service = mock_injector.workflows_service()
mock_workflows_service.publish_to_fairworkflow = unittest.mock.MagicMock(
    return_value={
        "nanopub_uri": workflow_trusted_uri,
        "concept_uri": workflow_trusted_uri,
    }
)
mock_workflows_service.retract_in_fairworkFlow = unittest.mock.MagicMock(
    return_value={
        "nanopub_uri": workflow_retract_trusted_uri,
    }
)

mock_injector.workflows_service.override(mock_workflows_service)