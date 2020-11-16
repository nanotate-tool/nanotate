from .mock_injector import mock_injector
from src.services import StatsService
from src.models import Protocol
from .constants import protocol_uri, is_slice_in_list

# check each operation available in stats service
# !warning exec after test_nanopub_service.py

service_instance: StatsService = mock_injector.statsService()


def test_stats_essentials():
    expected_keys = ["tags", "ontologies", "terms"]
    data = service_instance.essentials(protocol=protocol_uri)
    assert data != None and isinstance(data, list) and len(data) == 1
    assert (
        data[0] != None
        and isinstance(data[0], dict)
        and is_slice_in_list(expected_keys, data[0].keys())
    )


def test_stats_for_tags():
    expected_keys = ["label", "count"]
    data = service_instance.forTags(protocol=protocol_uri)
    assert data != None and isinstance(data, list) and len(data) == 2
    assert (
        data[0] != None
        and isinstance(data[0], dict)
        and is_slice_in_list(expected_keys, data[0].keys())
    )


def test_stats_terms():
    expected_keys = ["used", "related"]
    data = service_instance.forTerms(protocol=protocol_uri)
    assert data != None and isinstance(data, list) and len(data) == 1
    assert (
        data[0] != None
        and isinstance(data[0], dict)
        and is_slice_in_list(expected_keys, data[0].keys())
    )


def test_stats_ontologies():
    expected_keys = ["label", "count"]
    data = service_instance.forOntologies(protocol=protocol_uri)
    assert data != None and isinstance(data, list) and len(data) == 1
    assert (
        data[0] != None
        and isinstance(data[0], dict)
        and is_slice_in_list(expected_keys, data[0].keys())
    )