from flask import Blueprint, abort, redirect, jsonify
from flask_cors import CORS
from dependency_injector.wiring import Provide
from src.injector import Injector


def home_settings_and_vars_controller(
    env: dict = Provide[Injector.env],
):
    """
    define at controller to settings and var of app
    """
    # flask module
    controller = Blueprint("settings_and_vars_controller", __name__)

    # cors
    CORS(controller, resources={r"/settings/*": {"origins": "*"}})
    # const
    env_settings = env["settings"]
    SETTINGS = {"ontologies": env_settings["ontologies"], "tags": env_settings["tags"]}

    if not env_settings["production"]:
        SETTINGS["test"] = True

    # enpoints def
    @controller.route("/settings", methods=["GET"])
    def remote_nanopublication_forward():
        """
        returns settings of api
        """
        return jsonify(SETTINGS)

    return controller
