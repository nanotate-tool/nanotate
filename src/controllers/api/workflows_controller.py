from flask import Blueprint, request, jsonify, abort
from flask_cors import CORS
from src.services import WorkflowsService
from dependency_injector.wiring import Provide
from src.injector import Injector
from src.models.workflow_request import WorkflowRequest


def api_workflows_controller(
    service: WorkflowsService = Provide[Injector.workflows_service],
):
    """
    defines controller for endpoints of workflows tasks
    """
    # flask module
    controller = Blueprint("api_workflows_controllers", __name__)

    # cors
    CORS(controller, resources={r"/api/*": {"origins": "*"}})

    # enpoints def

    @controller.route("/api/workflows", methods=["POST"])
    def create_workflow():
        request_payload = request.get_json()
        workflow_request = WorkflowRequest(**request_payload)
        data = service.create(workflow_request)
        return jsonify(data)

    @controller.route("/api/workflows", methods=["GET"])
    def get_workflows():
        uri = (
            request.args["uri"]
            if "uri" in request.args
            else abort(400, "uri parameter is required")
        )
        rdf_format = (
            request.args["rdf_format"] if "rdf_format" in request.args else None
        )
        data = service.workflows_of_protocol(
            protocol_uri=uri, json=True, rdf_format=rdf_format
        )
        return jsonify(data)

    @controller.route("/api/workflows/<workflow>", methods=["GET"])
    def get_workflow(workflow: str):
        rdf_format = (
            request.args["rdf_format"] if "rdf_format" in request.args else None
        )
        data = service.get_workflow(
            workflow_id=workflow, json=True, rdf_format=rdf_format
        )
        return jsonify(data)

    @controller.route("/api/workflows/<workflow>", methods=["DELETE"])
    def delete(workflow: str):
        data = service.delete(workflow_key=workflow)
        return jsonify(data)

    return controller
