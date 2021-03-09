from flask import Blueprint, request, jsonify, abort
from flask_cors import CORS
from src.services.protocols_service import ProtocolsService
from src.models.annotation import Annotation
from dependency_injector.wiring import Provide
from src.injector import Injector


def api_protocols_controller(
    service: ProtocolsService = Provide[Injector.protocolsService],
):
    """
    Define los controladores de tareas de api para el manejo de las protocolos(sitios)
    """
    # flask module
    controller = Blueprint("api_protocols_controllers", __name__)

    # cors
    CORS(controller, resources={r"/api/*": {"origins": "*"}})

    # enpoints def
    @controller.route("/api/protocols", methods=["GET"])
    def get_protocol_data():
        """registro de anotaciones para su transformacion a nanopublicaciones"""
        protocol = (
            request.args["uri"]
            if "uri" in request.args
            else abort(400, "uri parameter is required")
        )
        data = service.get_protocol(protocol)
        return jsonify(data)

    return controller
