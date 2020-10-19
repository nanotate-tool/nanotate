from flask import Blueprint, request, jsonify, abort
from flask_cors import CORS
from src.services.stats_service import StatsService
from dependency_injector.wiring import Provide
from src.injector import Injector


def api_stats_controller(
    service: StatsService = Provide[Injector.statsService],
):
    """
    Define los controladores de metodos de estadistica
    """
    # flask module
    controller = Blueprint("api_stats_controllers", __name__)

    # cors
    CORS(controller, resources={r"/api/*": {"origins": "*"}})

    # enpoints def

    FILTERS = {
        "tags": service.forTags,
        "terms": service.forTerms,
        "ontologies": service.forOntologies,
    }

    @controller.route("/api/stats", methods=["GET"])
    def get_essentials_stats():
        protocol = (
            request.args["uri"]
            if "uri" in request.args
            else abort(400, "uri parameter is required")
        )
        data = service.essentials(protocol=protocol)
        return jsonify(data)

    @controller.route("/api/stats/<filter>", methods=["GET"])
    def get_generic_filter(filter):
        settings = (
            FILTERS[filter] if filter in FILTERS else abort(404, "not found filter")
        )
        protocol = (
            request.args["uri"]
            if "uri" in request.args
            else abort(400, "uri parameter is required")
        )
        data = settings(protocol=protocol)
        return jsonify(data)

    return controller
