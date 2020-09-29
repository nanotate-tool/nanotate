from flask import Flask
from src.controllers.api.nanopubs_controller import api_nanopubs_controllers
from src.controllers.api.bioportal_controller import api_bioportal_controllers

# inicialize flask app
app = Flask(__name__)

# registro del controlador de 'registro de annotaciones'
app.register_blueprint(api_nanopubs_controllers)
app.register_blueprint(api_bioportal_controllers)


def dev():
    """DEV entry point of the app."""
    try:
        # logging.basicConfig(filename='error.log',level=logging.DEBUG)
        app.run(host='0.0.0.0', debug=True, port=8080,
                use_reloader=True, threaded=True)
    except Exception as exc:
        print(exc.message)
    finally:
        # get last entry and insert build appended if not completed
        # Do something here
        pass
