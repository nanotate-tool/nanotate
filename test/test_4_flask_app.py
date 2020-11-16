import pytest
from .mock_injector import mock_injector
from .constants import (
    protocol_uri,
    nanopub_key,
    test_annotations_json_path,
    empty_protocol_uri,
    is_slice_in_list,
)
from src.app import application
from flask import url_for, Response
from flask.testing import FlaskClient
import json


@pytest.fixture
def annotations_json():
    with open(test_annotations_json_path) as infile:
        data = json.load(infile)
        annotations = data
    return annotations


@pytest.fixture
def client():
    app = application(dev=False, injector=mock_injector)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# nanopub_controller for api


def test_settings(client: FlaskClient):
    response: Response = client.get("/settings", follow_redirects=True)
    assert (
        response != None
        and response.status_code == 200
        and isinstance(response.get_json(), dict)
        and is_slice_in_list(["tags", "ontologies"], response.get_json())
    )

def test_api_annotations_preview(client: FlaskClient, annotations_json):
    response: Response = client.post(
        "/api/nanopub/preview",
        data=json.dumps(annotations_json),
        follow_redirects=True,
        content_type="application/json",
    )
    assert response != None and response.status_code == 200
    assert (
        response != None
        and isinstance(response.get_json(), list)
        and len(response.get_json()) == 1
        and isinstance(response.get_json()[0], dict)
    )


def test_api_get_nanopubs(client: FlaskClient):
    query = {"uri": protocol_uri}
    response: Response = client.get(
        "/api/nanopub",
        query_string=query,
        follow_redirects=True,
    )
    query["rdf_format"] = "turtle"
    response_other_format: Response = client.get(
        "/api/nanopub",
        query_string=query,
        follow_redirects=True,
    )
    query["uri"] = empty_protocol_uri
    response_empty = client.get(
        "/api/nanopub",
        query_string=query,
        follow_redirects=True,
    )
    assert response != None and response.status_code == 200
    assert (
        response != None
        and isinstance(response.get_json(), list)
        and len(response.get_json()) == 1
        and isinstance(response.get_json()[0], dict)
    )
    assert response_other_format != None and response_other_format.status_code == 200
    assert (
        response_other_format != None
        and isinstance(response_other_format.get_json(), list)
        and len(response_other_format.get_json()) == 1
        and isinstance(response_other_format.get_json()[0], dict)
        and response_other_format.get_json()[0]["rdf_raw"]
        != response.get_json()[0]["rdf_raw"]
    )
    assert (
        response_empty != None
        and response_empty.status_code == 200
        and isinstance(response_empty.get_json(), list)
        and len(response_empty.get_json()) == 0
    )


def test_api_get_nanopub(client: FlaskClient):
    uri = "/api/nanopub/" + nanopub_key
    response: Response = client.get(uri)
    response_other_format: Response = client.get(
        uri, query_string={"rdf_format": "xml"}
    )
    response_not_found: Response = client.get("/api/nanopub/not-exist")
    assert (
        response != None
        and response.status_code == 200
        and isinstance(response.get_json(), dict)
    )
    assert (
        response_not_found != None
        and response_not_found.status_code == 200
        and response_not_found.get_json()["error"] == "not-found"
    )
    assert (
        response_other_format != None
        and response_other_format.status_code == 200
        and isinstance(response_other_format.get_json(), dict)
        and response_other_format.get_json()["rdf_raw"]
        != response.get_json()["rdf_raw"]
    )


def test_api_delete_nanopub(client: FlaskClient):
    response: Response = client.delete("/api/nanopub/" + nanopub_key)
    response_not_exist: Response = client.delete("/api/nanopub/not-exist")
    assert (
        response != None
        and response.status_code == 200
        and isinstance(response.get_json(), dict)
        and response.get_json()["status"] == "ok"
    )
    assert (
        response_not_exist != None
        and response_not_exist.status_code == 200
        and isinstance(response_not_exist.get_json(), dict)
        and response_not_exist.get_json()["status"] == "error"
        and response_not_exist.get_json()["message"] == "Nanopublication not found"
    )


def test_api_register_nanopub(client: FlaskClient, annotations_json):
    response: Response = client.post(
        "/api/nanopub/rgs",
        data=json.dumps(annotations_json),
        follow_redirects=True,
        content_type="application/json",
    )
    assert (
        response != None
        and isinstance(response.get_json(), dict)
        and response.get_json()["status"] == "ok"
        and response.get_json()[nanopub_key]["status"] == "ok"
    )


# protocol_controller for api


def test_api_get_protocol(client: FlaskClient):
    response: Response = client.get(
        "/api/protocols",
        query_string={"uri": protocol_uri},
        follow_redirects=True,
    )
    response_empty_protocol: Response = client.get(
        "/api/protocols",
        query_string={"uri": empty_protocol_uri},
        follow_redirects=True,
    )
    response_bad: Response = client.get(
        "/api/protocols",
        follow_redirects=True,
    )
    assert (
        response != None
        and response.status_code == 200
        and isinstance(response.get_json(), dict)
    )
    assert (
        response_empty_protocol != None
        and response_empty_protocol.status_code == 200
        and isinstance(response_empty_protocol.get_json(), dict)
    )
    assert response_bad != None and response_bad.status_code == 400


# stats_controller for api


def test_api_essential_stats(client: FlaskClient):
    response: Response = client.get(
        "/api/stats",
        query_string={"uri": protocol_uri},
        follow_redirects=True,
    )
    response_empty_protocol: Response = client.get(
        "/api/stats",
        query_string={"uri": empty_protocol_uri},
        follow_redirects=True,
    )
    response_bad: Response = client.get(
        "/api/stats",
        follow_redirects=True,
    )
    assert (
        response != None
        and response.status_code == 200
        and isinstance(response.get_json(), list)
        and len(response.get_json()) == 1
    )
    assert (
        response_empty_protocol != None
        and response_empty_protocol.status_code == 200
        and isinstance(response_empty_protocol.get_json(), list)
        and len(response_empty_protocol.get_json()) == 1
    )
    assert response_bad != None and response_bad.status_code == 400


def test_api_generic_filter(client: FlaskClient):
    response: Response = client.get(
        "/api/stats/tags",
        query_string={"uri": protocol_uri},
        follow_redirects=True,
    )
    response_empty_protocol: Response = client.get(
        "/api/stats/terms",
        query_string={"uri": empty_protocol_uri},
        follow_redirects=True,
    )
    response_bad: Response = client.get(
        "/api/stats/not-filter",
        follow_redirects=True,
    )
    assert (
        response != None
        and response.status_code == 200
        and isinstance(response.get_json(), list)
        and len(response.get_json()) == 2
    )
    assert (
        response_empty_protocol != None
        and response_empty_protocol.status_code == 200
        and isinstance(response_empty_protocol.get_json(), list)
        and len(response_empty_protocol.get_json()) == 1
    )
    assert response_bad != None and response_bad.status_code == 404
