from flask import Flask
from flask_compress import Compress
from src.injector import Injector
from . import controllers

compress = Compress()


def application(
    dev: bool = True,
    config_path: str = "environment/environment_dev.yml",
    injector: Injector = None,
) -> Flask:
    """
    realiza la creacion de la aplicacion flask
    """
    # inicialize app env
    if injector is None:
        injector = Injector()
        injector.env.from_yaml(config_path)
        # manual database connection
        injector.mongoDb().connect()

    # inicialize flask app
    app = Flask(__name__)
    # compress init
    compress.init_app(app)
    app.injector = injector
    # regiter controllers
    controllers.register(app, injector)

    if dev:
        runDev(app)

    return app


def runDev(app: Flask):
    """Run Flask App in DEV settings."""
    try:
        # logging.basicConfig(filename='error.log',level=logging.DEBUG)
        app.run(host="0.0.0.0", debug=True, port=8080, use_reloader=True, threaded=True)
    except Exception as exc:
        print(exc.message)
    finally:
        # get last entry and insert build appended if not completed
        # Do something here
        pass
