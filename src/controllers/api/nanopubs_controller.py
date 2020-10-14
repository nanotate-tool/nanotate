from flask import Blueprint, request, jsonify, abort
from flask_cors import CORS
from src.services.nanopub_services import NanoPubServices
from src.models.annotation import Annotation
from dependency_injector.wiring import Provide
from src.injector import Injector


def api_nanopubs_controller(
    service: NanoPubServices = Provide[Injector.nanopubsService],
):
    """
    Define los controladores de tareas de api para el manejo de las nanopublicaciones
    """
    # flask module
    controller = Blueprint("api_nanopubs_controllers", __name__)

    # cors
    CORS(controller, resources={r"/api/*": {"origins": "*"}})

    # enpoints def
    @controller.route("/api/nanopub/rgs", methods=["POST"])
    def annotations_register():
        """registro de anotaciones para su transformacion a nanopublicaciones"""
        data = service.registerFromAnnotations(
            Annotation.parseJsonArr(request.get_json())
        )
        return jsonify(data)

    @controller.route("/api/nanopub/preview", methods=["POST"])
    def annotations_preview():
        """realiza la simulacion de las anotaciones enviadas a un formator trig de estas devueltas en un formato json"""
        format = request.args["format"] if "format" in request.args else None
        data = service.previewAnnotations(
            Annotation.parseJsonArr(request.get_json()), format
        )
        return jsonify(data)

    @controller.route("/api/nanopub", methods=["GET"])
    def nanopubs():
        protocol = (
            request.args["uri"]
            if "uri" in request.args
            else abort(400, "uri parameter is required")
        )
        rdf_format = (
            request.args["rdf_format"] if "rdf_format" in request.args else None
        )
        """ visualizacion de las nanopublicaciones para una uri"""
        data = service.nanopubsByProtocol(
            protocol=protocol, json=True, rdf_format=rdf_format
        )
        return jsonify(data)

    @controller.route("/api/nanopub/<nanopub>", methods=["GET"])
    def nanopub(nanopub: str):
        rdf_format = (
            request.args["rdf_format"] if "rdf_format" in request.args else None
        )
        data = service.nanopubById(id=nanopub, json=True, rdf_format=rdf_format)
        return jsonify(data)

    return controller
