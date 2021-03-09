import pytest
from .mock_injector import mock_injector
from src.services import NanoPubServices
from src.models import Nanopublication
import json
from src.models.annotation import Annotation
from .constants import (
    nanopub_key,
    expected_nanopubs,
    empty_protocol_uri,
    protocol_uri,
    test_annotations_json_path,
    published_trusted_uri,
    published_artifact_code,
)

# check each operation available in nanopub service


service_instance: NanoPubServices = mock_injector.nanopubsService()


@pytest.fixture
def annotations():
    with open(test_annotations_json_path) as infile:
        data = json.load(infile)
        annotations = Annotation.parse_json_arr(data)
    return annotations


def test_preview_annotations(annotations):
    empty_data = service_instance.preview_annotations(annotations=[])
    data = service_instance.preview_annotations(annotations=annotations)
    data_any_format = service_instance.preview_annotations(
        annotations=annotations, format="json-html"
    )
    assert empty_data != None and isinstance(empty_data, list) and len(empty_data) == 0
    assert (
        data != None
        and isinstance(data, list)
        and len(data) == expected_nanopubs
        and isinstance(data[expected_nanopubs - 1], dict)
        and data[expected_nanopubs - 1]["id"] == nanopub_key
    )
    assert (
        data_any_format != None
        and isinstance(data_any_format, list)
        and len(data_any_format) == expected_nanopubs
        and isinstance(data_any_format[expected_nanopubs - 1], dict)
        and data_any_format[expected_nanopubs - 1]["id"] == nanopub_key
        and data_any_format[expected_nanopubs - 1]["rdf"]
        != data[expected_nanopubs - 1]["rdf"]
    )


def test_registration_nanopub(annotations):
    data = service_instance.register_from_annotations(annotations=annotations)
    assert data["status"] == "ok"
    assert (
        data[nanopub_key]["status"] == "ok"
        and data[nanopub_key]["nanopub"]["publication_info"]["nanopub_uri"]
        == published_trusted_uri
        and data[nanopub_key]["nanopub"]["publication_info"]["artifact_code"]
        == published_artifact_code
    )


def test_get_nanopub_by_id():
    not_exist = service_instance.nanopub_by_id(id="not-exists")
    not_exist_json = service_instance.nanopub_by_id(id="not-exists", json=True)
    data = service_instance.nanopub_by_id(id=nanopub_key)
    data_json = service_instance.nanopub_by_id(id=nanopub_key, json=True)
    data_any_format = service_instance.nanopub_by_id(id=nanopub_key, rdf_format="turtle")
    data_for_compare = service_instance.nanopub_by_id(id=nanopub_key, rdf_format="turtle", for_compare= True)
    assert data != None and isinstance(data, Nanopublication) and data.id == nanopub_key
    assert (
        data_json != None
        and isinstance(data_json, dict)
        and data_json["id"] == nanopub_key
    )
    assert (
        data_any_format != None
        and isinstance(data_any_format, Nanopublication)
        and data_any_format.id == nanopub_key
        and data_any_format.rdf_raw != data.rdf_raw
    )
    assert (
        data_for_compare != None
        and isinstance(data_for_compare, Nanopublication)
        and data_for_compare.id == nanopub_key
        and data_for_compare.rdf_raw != data_any_format.rdf_raw
    )
    assert isinstance(not_exist, dict) and not_exist["error"] == "not-found"
    assert isinstance(not_exist_json, dict) and not_exist_json["error"] == "not-found"


def test_get_nanopubs_by_protocol():
    data = service_instance.nanopubs_by_protocol(protocol=protocol_uri)
    data_json = service_instance.nanopubs_by_protocol(protocol=protocol_uri, json=True)
    data_any_format = service_instance.nanopubs_by_protocol(
        protocol=protocol_uri, rdf_format="xml"
    )
    data_empty = service_instance.nanopubs_by_protocol(protocol=empty_protocol_uri)
    assert (
        data != None
        and len(data) == expected_nanopubs
        and isinstance(data[expected_nanopubs - 1], Nanopublication)
    )
    assert data_empty != None and len(data_empty) == 0
    assert (
        data_json != None
        and len(data_json) == expected_nanopubs
        and isinstance(data_json[expected_nanopubs - 1], dict)
    )
    assert (
        data_any_format != None
        and len(data_any_format) == expected_nanopubs
        and data_any_format[expected_nanopubs - 1].rdf_raw
        != data[expected_nanopubs - 1].rdf_raw
    )
