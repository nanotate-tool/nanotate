from flask import Flask
from src.injector import Injector
from . import api, home
from .api import (
    bioportal_controller,
    nanopubs_controller,
    protocols_controller,
    stats_controller,
)


def register(app: Flask, injector: Injector) -> Flask:
    """
    Registro de controladores para la app flask pasada
    """
    # root controllers
    injector.wire(modules=[home])
    app.register_blueprint(home.home_nanopubs_controller())
    app.register_blueprint(home.home_settings_and_vars_controller())

    # api controllers
    injector.wire(
        modules=[
            api.bioportal_controller,
            api.nanopubs_controller,
            protocols_controller,
            stats_controller,
        ]
    )
    app.register_blueprint(api.bioportal_controller.api_bioportal_controller())
    app.register_blueprint(api.nanopubs_controller.api_nanopubs_controller())
    app.register_blueprint(api.protocols_controller.api_protocols_controller())
    app.register_blueprint(api.stats_controller.api_stats_controller())
    return app