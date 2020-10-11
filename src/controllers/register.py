from flask import Flask
from src.injector import Injector
from . import api
from .api import bioportal_controller, nanopubs_controller


def register(app: Flask, injector: Injector) -> Flask:
    """
    Registro de controladores para la app flask pasada
    """
    # api controllers
    injector.wire(modules=[api.bioportal_controller, api.nanopubs_controller])
    app.register_blueprint(api.bioportal_controller.api_bioportal_controller())
    app.register_blueprint(api.nanopubs_controller.api_nanopubs_controller())
    return app