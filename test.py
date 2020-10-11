from src.models.annotation import Annotation
from src.models.nanopub_request import NanopubRequest
from src.adapters.nanopublication import Nanopublication
from src.adapters.assertion_strategy import BioportalAssertionStrategy
from src.adapters.bioportal_api import BioPortalApi
from src.injector import Injector
import json
import os
import sys
import getopt

injector = Injector()
injector.env.from_yaml("environment/environment_dev.yml")
BIO_PORTAL_API = injector.bioportalApi()
ASSERTION_STRATEGY = BioportalAssertionStrategy(BIO_PORTAL_API)


def help():
    print("uso test.py -i <inputfile> -o <output> -od <outputdir>")
    print(
        "\n       Herramienta de prueba de anotaciones desde un json a una nanpublicacion !!!\n"
    )
    print("ifile    -i      determina el archivo con las anotaciones en formato json")
    print(
        "output   -o      determina el formato de salida `print(pinta en pantalla)` o `file(lo almacena en un archivo)` "
    )
    print(
        "odir     -d     determina el directorio de almacenar las nanopublicaciones, solo si el output es `file`"
    )
    print("\n")


def main(argv):
    inputfile = "test/annotation_hypothesis.json"
    outputFormat = "print"
    outputdir = ""
    try:
        opts, args = getopt.getopt(argv, "hi:o:d:", ["ifile=", "output=", "odir="])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            help()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--output"):
            outputFormat = arg
        elif opt in ("-d", "--odir"):
            outputdir = arg
    test(inputfile, outputFormat, "trig", outputdir)


def test(inputfile, outputFormat="print", rdfFormat="trig", outputdir=None):
    print("making test... from file", inputfile)
    with open(inputfile) as infile:
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
        print(
            "pass 3) -> ",
            ("Almacenando anotaciones en " + outputdir)
            if outputFormat == "file"
            else "Imprimiendo en pantalla anotaciones",
        )
        if (
            outputFormat == "file"
            and outputdir != None
            and not os.path.exists(outputdir)
        ):
            os.makedirs(outputdir)

        for request in requests:
            nanopublication = Nanopublication(request, ASSERTION_STRATEGY)
            filename = "nanopublication-" + request.id + ".trig"
            if outputFormat == "file":
                filepath = outputdir + filename
                text_file = open(filepath, "w")
                print("\t-->", "Almacenando nanopublicacion en", "'" + filepath + "'")
                n = text_file.write(nanopublication.serialize(rdfFormat))
                text_file.close()
            else:
                print(nanopublication.serialize(rdfFormat))


if __name__ == "__main__":
    main(sys.argv[1:])
