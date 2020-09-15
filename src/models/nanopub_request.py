from __future__ import annotations
from .annotation import Annotation
from .annotation_tag import AnnotationTag


class NanopubRequest:
    """ Annotation class docs\n

        contiene las Anotaciones necesarias para solicitar la generacion de una nanopublicacion
    """

    def __init__(self, annotations: list):
        self.annotations = annotations

    @property
    def id(self) -> str:
        """ identificador de la anotacion anotada con 'step' """
        return self.step.id

    @property
    def user(self) -> str:
        """ usuario de la anotacion anotada con 'step' """
        return self.step.user

    @property
    def url(self) -> str:
        """ determina la url de origen de la anotacion anotada con 'step' """
        return self.step.url

    @property
    def step(self) -> Annotation:
        """ anotacion asociada al tag 'step' """
        return self.annotationOf(AnnotationTag.step)

    def annotationOf(self, tag: AnnotationTag) -> Annotation:
        """ retorna la annotacion relacionada al tag pasado """
        for annotation in self.annotations:
            try:
                if annotation.tags and annotation.tags.index(tag.value) >= 0:
                    return annotation
            except:
                pass
        return None

    @staticmethod
    def splitAnnotations(args: list) -> list:
        """ realiza el proceso de divicion de la lista de anotaciones pasadas a una lista NanopubRequest validas"""
        request = []
        for annotation in args:
            try:
                if annotation.tags.index(AnnotationTag.step.value) >= 0:
                    request.append(NanopubRequest.splitDeep(annotation, args))
            except:
                pass
        return request

    @staticmethod
    def splitDeep(step: Annotation, annotations: list) -> NanopubRequest:
        """ construye una NanopubRequest para el step base pasado \n
            y las anotaciones que se encuentre en el rango de este ('step.start'|'step.end')
        """
        request_annotations = [step]
        for annotation in annotations:
            if step.id != annotation.id and annotation.start >= step.start and annotation.end <= step.end:
                request_annotations.append(annotation)
        return NanopubRequest(request_annotations)
