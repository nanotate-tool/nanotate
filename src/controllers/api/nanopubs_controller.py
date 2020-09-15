from flask import Blueprint, request, jsonify
from flask_cors import CORS
from src.services.nanopub_services import NanoPubServices
from src.models.annotation import Annotation
"""
    DOCS:
    Define los controladores de tareas de api para el manejo de las nanopublicaciones
    
"""
# flask module
api_nanopubs_controllers = Blueprint(
    'api_nanopubs_controllers', __name__)

#cors
CORS(api_nanopubs_controllers, resources={r"/api/*": {"origins": "*"}})

# central service
service = NanoPubServices()


#enpoints def
@api_nanopubs_controllers.route('/api/nanopub/rgs', methods=['POST'])
def annotations_register():
    """registro de anotaciones para su transformacion a nanopublicaciones"""
    data = request.get_json()
    return jsonify(data)


@api_nanopubs_controllers.route('/api/nanopub/preview', methods=['POST'])
def annotations_preview():
    """realiza la simulacion de las anotaciones enviadas a un formator trig de estas devueltas en un formato json"""
    format = request.args['format'] if 'format' in request.args else None
    data = service.previewAnnotations(
        Annotation.parseJsonArr(request.get_json()), format)
    return jsonify(data)
