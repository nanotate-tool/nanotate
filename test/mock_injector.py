# mock injector
import unittest.mock
from src.injector import Injector
from nanopub import NanopubClient
from .mongo_mock import MockMongoDb
from .constants import published_trusted_uri


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
mock_injector.nanopubClient.override(mock_nanopub_client)
