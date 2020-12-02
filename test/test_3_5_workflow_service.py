from .mock_injector import mock_injector
from src.services import WorkflowsService
from src.models import Workflow
from .constants import (
    protocol_uri,
    is_slice_in_list,
    workflow_request,
    empty_protocol_uri,
)
import pytest


# check each operation available in stats service
# !warning exec after test_nanopub_service.py

service_instance: WorkflowsService = mock_injector.workflows_service()

workflow_id = None


def test_create_workflow():
    data = service_instance.create(workflow=workflow_request)
    pytest.workflow_id = data["data"]["id"]
    assert data["status"] == "ok"
    assert data["status"] == "ok" and data["data"] != None


def test_get_workflow_by_id():
    not_exist = service_instance.get_workflow(workflow_id="not-exists")
    not_exist_json = service_instance.get_workflow(workflow_id="not-exists", json=True)
    data = service_instance.get_workflow(workflow_id=pytest.workflow_id)
    data_json = service_instance.get_workflow(workflow_id=pytest.workflow_id, json=True)
    data_any_format = service_instance.get_workflow(
        workflow_id=pytest.workflow_id, rdf_format="turtle"
    )
    data_for_compare = service_instance.get_workflow(
        workflow_id=pytest.workflow_id, rdf_format="xml"
    )
    assert data != None and isinstance(data, Workflow) and data.id == pytest.workflow_id
    assert (
        data_json != None
        and isinstance(data_json, dict)
        and data_json["id"] == pytest.workflow_id
    )
    assert (
        data_any_format != None
        and isinstance(data_any_format, Workflow)
        and data_any_format.id == pytest.workflow_id
        and data_any_format.rdf != data.rdf
    )
    assert (
        data_for_compare != None
        and isinstance(data_for_compare, Workflow)
        and data_for_compare.id == pytest.workflow_id
        and data_for_compare.rdf != data_any_format.rdf
    )
    assert isinstance(not_exist, dict) and not_exist["error"] == "not-found"
    assert isinstance(not_exist_json, dict) and not_exist_json["error"] == "not-found"


def test_get_workflows_by_protocol():
    data = service_instance.workflows_of_protocol(protocol_uri=protocol_uri)
    data_json = service_instance.workflows_of_protocol(
        protocol_uri=protocol_uri, json=True
    )
    data_any_format = service_instance.workflows_of_protocol(
        protocol_uri=protocol_uri, rdf_format="xml"
    )
    data_empty = service_instance.workflows_of_protocol(protocol_uri=empty_protocol_uri)
    assert data != None and len(data) == 1 and isinstance(data[0], Workflow)
    assert data_empty != None and len(data_empty) == 0
    assert data_json != None and len(data_json) == 1 and isinstance(data_json[0], dict)
    assert (
        data_any_format != None
        and len(data_any_format) == 1
        and data_any_format[0].rdf != data[0].rdf
    )


def test_delete_workflow():
    data = service_instance.delete(workflow_key=pytest.workflow_id)
    data_notexist = service_instance.delete(workflow_key="not-exist")
    assert data != None and isinstance(data, dict) and data["status"] == "ok"
    assert (
        data_notexist != None
        and isinstance(data, dict)
        and data_notexist["status"] == "error"
        and data_notexist["message"] == "Workflow not found"
    )
