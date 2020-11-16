from .mock_injector import mock_injector
from src.services import ProtocolsService
from src.models import Protocol
from .constants import protocol_uri, empty_protocol_uri

# check each operation available in protocol service
# !warning exec after test_nanopub_service.py

service_instance: ProtocolsService = mock_injector.protocolsService()


def test_get_protocol():
    not_exist = service_instance.getProtocol(uri=empty_protocol_uri)
    data = service_instance.getProtocol(uri=protocol_uri)
    assert data != None and isinstance(data, dict)
    assert not_exist != None and isinstance(not_exist, dict)
