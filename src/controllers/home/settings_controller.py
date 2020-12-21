from flask import Blueprint, abort, redirect, jsonify, request
from flask_cors import CORS
from dependency_injector.wiring import Provide
from src.injector import Injector
from src.utils.site_metadata_puller import clean_url_with_settings


def home_settings_and_vars_controller(
    env: dict = Provide[Injector.env],
):
    """
    define at controller to settings and var of app
    """
    # flask module
    controller = Blueprint("settings_and_vars_controller", __name__)

    # cors
    CORS(controller, resources={r"/settings/*": {"origins": "*"}, r"/cleanurl/*": {"origins": "*"}})
    # const
    env_settings = env["settings"]
    SETTINGS = {"ontologies": env_settings["ontologies"], "tags": env_settings["tags"]}

    if not env_settings["production"]:
        SETTINGS["test"] = True

    # enpoints def
    @controller.route("/settings", methods=["GET"])
    def get_settings():
        """
        returns settings of api
        """
        return jsonify(SETTINGS)

    @controller.route("/cleanurl", methods=["GET"])
    def clean_url():
        """
        returns clean url
        """
        return jsonify(
            {
                "uri": clean_url_with_settings(
                    url=request.args["uri"], settings=env_settings
                )
            }
        )

    return controller
