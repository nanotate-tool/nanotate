from flask import Blueprint, abort, redirect
from flask_cors import CORS
from src.models import Nanopublication
from src.services.nanopub_services import NanoPubServices
from dependency_injector.wiring import Provide
from src.injector import Injector


def home_nanopubs_controller(
    service: NanoPubServices = Provide[Injector.nanopubsService],
):
    """
    Define los controladores de tareas de api para el manejo de las nanopublicaciones
    """
    # flask module
    controller = Blueprint("nanopubs_controllers", __name__)

    # cors
    CORS(controller, resources={r"/np/*": {"origins": "*"}})

    # enpoints def
    @controller.route("/np/<artifact>", methods=["GET"])
    def remote_nanopublication_forward(artifact):
        """redirige los artifacts de nanopublicaciones locales a su publicacion remota"""
        nanopublication = service.nanopubByArtifactCode(artifact_code=artifact)
        print(nanopublication)
        if (
            type(nanopublication) is Nanopublication
            and nanopublication.publication_info != None
        ):
            return redirect(nanopublication.publication_info.canonical_url)
        else:
            return abort(404, "Nanopublication not found")

    return controller
