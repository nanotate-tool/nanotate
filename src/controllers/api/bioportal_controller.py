from flask import Blueprint, request, jsonify, abort
from flask_cors import CORS
from src.services.bioportal_service import BioPortalService
from src.models.annotation import Annotation
"""
    DOCS:
    Define los controladores de tareas de api para operaciones sobre bioportal
    
"""
# flask module
api_bioportal_controllers = Blueprint(
    'api_bioportal_controllers', __name__)

# cors
CORS(api_bioportal_controllers, resources={r"/api/*": {"origins": "*"}})

service = BioPortalService()

# enpoints def


@api_bioportal_controllers.route('/api/bio/annotator', methods=['GET'])
def annotations():
    """registro de anotaciones para su transformacion a nanopublicaciones"""
    ontologies = request.args.get('ontologies') if 'ontologies' in request.args else abort(
        400, "ontologies parameter is required")
    ontologies = [ontologies] if type(ontologies) != list else ontologies
    text = request.args['text'] if 'text' in request.args else abort(
        400, "text parameter is required")
    consulted_annotations = service.annotations(ontologies, text)
    return jsonify(consulted_annotations)
