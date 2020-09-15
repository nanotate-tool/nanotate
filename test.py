from src.models.annotation import Annotation
from src.models.nanopub_request import NanopubRequest
from src.adapters.nanopublication import Nanopublication
from src.adapters.assertion_strategy import BioportalAssertionStrategy
from src.adapters.bioportal_api import BioPortalApi
import json

BIO_PORTAL_API = BioPortalApi("8b5b7825-538d-40e0-9e9e-5ab9274a9aeb")
ASSERTION_STRATEGY = BioportalAssertionStrategy(BIO_PORTAL_API)

print("making testing...")
with open('test/annotation_hypothesis.json') as infile:
    # paso 1 parseo
    print("pass 1) -> parseando las anotaciones desde un archivo")
    data = json.load(infile)
    annotations = Annotation.parseJsonArr(data)
    print("\t-->", len(annotations), "annotaciones encontradas desde el archivo")
    print("\t-->", "presentando datos basicos de la anotaciones")
    for annotation in annotations:
        print("\t-->", type(annotation), annotation.id, "tags:", annotation.tags)
    # paso 2 split
    print("pass 2) -> dividiendo en nanopubRequest")
    requests = NanopubRequest.splitAnnotations(annotations)
    print("\t-->", len(requests), "annotation steps encontrados")
    for request in requests:
        print("\t-->", type(request), request.step.id)
    print("pass 3) -> Almacenando anotaciones en '.dist/'")
    for request in requests:
        nanopublication = Nanopublication(request, ASSERTION_STRATEGY)
        filename = "nanopublication-" + request.id + ".trig"
        text_file = open("dist/"+filename, "w")
        print("\t-->", "Almacenando nanopublicacion en", "'"+filename + "'")
        n = text_file.write(nanopublication.serialize('trig'))
        text_file.close()
