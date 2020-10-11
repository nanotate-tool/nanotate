from flask import Blueprint, request, jsonify, abort
from flask_cors import CORS
from src.services.bioportal_service import BioPortalService
from src.models.annotation import Annotation
from src.injector import Injector
from dependency_injector.wiring import Provide


def api_bioportal_controller(
    service: BioPortalService = Provide[Injector.bioportalService],
):
    """
    Define los controladores de tareas de api para operaciones sobre bioportal
    """
    # flask module
    controller = Blueprint("api_bioportal_controllers", __name__)

    # cors
    CORS(controller, resources={r"/api/*": {"origins": "*"}})

    # enpoints def

    @controller.route("/api/bio/annotator", methods=["GET"])
    def annotations():
        """registro de anotaciones para su transformacion a nanopublicaciones"""
        ontologies = (
            request.args.get("ontologies")
            if "ontologies" in request.args
            else abort(400, "ontologies parameter is required")
        )
        ontologies = [ontologies] if type(ontologies) != list else ontologies
        text = (
            request.args["text"]
            if "text" in request.args
            else abort(400, "text parameter is required")
        )
        consulted_annotations = service.annotations(ontologies, text)
        return jsonify(consulted_annotations)

    return controller
