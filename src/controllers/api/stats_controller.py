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
        "tags": service.for_tags,
        "terms": service.for_terms,
        "ontologies": service.for_ontologies,
        "nanopubs-by-users": service.stats_of_nanopubs_by_user,
        "nanopubs": service.stats_of_nanopubs,
    }

    @controller.route("/api/stats", methods=["GET"])
    def get_essentials_stats():
        protocol = request.args["protocol"] if "protocol" in request.args else "global"
        users = request.args.getlist("users") if "users" in request.args else []
        tags = request.args.getlist("tags") if "tags" in request.args else []
        data = service.essentials(protocol=protocol, users=users, tags=tags)
        return jsonify(data)

    @controller.route("/api/stats/<filter>", methods=["GET"])
    def get_generic_filter(filter):
        settings = (
            FILTERS[filter] if filter in FILTERS else abort(404, "not found filter")
        )
        protocol = request.args["protocol"] if "protocol" in request.args else "global"
        users = request.args.getlist("users") if "users" in request.args else []
        tags = request.args.getlist("tags") if "tags" in request.args else []
        page = int(request.args["page"]) if "page" in request.args else 1
        data = settings(protocol=protocol, tags=tags, users=users, page=page)
        return jsonify(data)

    return controller
