from flask import Flask
from src.injector import Injector
from . import controllers


def application(
    dev: bool = True, config_path: str = "environment/environment_dev.yml"
) -> Flask:
    """
    realiza la creacion de la aplicacion flask
    """
    # inicialize app env
    injector = Injector()
    injector.env.from_yaml(config_path)

    # inicialize flask app
    app = Flask(__name__)
    app.injector = injector
    # manual database connection
    injector.mongoDb().connect()
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
