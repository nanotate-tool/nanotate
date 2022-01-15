from cmath import isnan
from flask import Blueprint, abort, redirect, render_template, request, Response
from flask_cors import CORS
from src.models import Nanopublication
from src.services.nanopub_services import NanoPubServices
from dependency_injector.wiring import Provide
from src.injector import Injector
import math

FORMATS = [('trig','application/x-trig'),('nq','text/x-nquads'),
           ('xml','application/trix'), ('jsonld','application/ld+json'),
           ('trig.txt','text/plain'), ('nq.txt','text/plain'),
           ('xml.txt','text/plain'), ('jsonld.txt','text/plain')]

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
        nanopublication = service.nanopub_by_artifact_code(artifact_code=artifact)
        if (
            type(nanopublication) is Nanopublication
            and nanopublication.publication_info != None
        ):
            return redirect(nanopublication.publication_info.nanopub_uri)
        else:
            return abort(404, "Nanopublication not found")

    @controller.route("/np/nanopubs.html", methods=["GET"])
    def nanopubs_html():
        page = request.args["page"] if "page" in request.args else None
        page = int(page) if not page is None and not isnan(int(page)) else None
        metadata = service.all_nanopubs_metadata(page=page)
        data = service.all_nanopubs(page=metadata['page'], projection_mode='publication')
        args = {
            **metadata,
            'data': enumerate(data['data']),
            'formats': FORMATS
        }
        return render_template("nanopubs.html", **args)
    
    @controller.route("/np/nanopubs.txt", methods=["GET"])
    def nanopubs_text():
        page = request.args["page"] if "page" in request.args else 1
        page = int(page) if not isnan(int(page)) else 1
        data = service.all_nanopubs(page=page, projection_mode='publication')
        str_data = "\n".join([str(nanopub['publication_info']['nanopub_uri']) for nanopub in data['data']])
        return Response(str_data, mimetype='')
    
    return controller
