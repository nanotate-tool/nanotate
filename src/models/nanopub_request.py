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
        """ retorna la anotacion asociada al tag 'step' """
        stepAnnotations = self.annotationsOf(AnnotationTag.step)
        return stepAnnotations[0] if len(stepAnnotations) > 0 else None

    def annotationsOf(self, tag: AnnotationTag) -> list:
        """ retorna las annotaciones relacionada al tag pasado """
        filtered = list(
            filter((lambda annotation: self.tagInAnnotation(
                tag, annotation)), self.annotations)
        )
        return filtered

    @staticmethod
    def tagInAnnotation(tag: AnnotationTag, annotation: Annotation):
        """
            realiza el proceso de verificacion de si el tag pasado se encuentra presente en
            las tags de la anotacion
        """
        try:
            return annotation.tags and annotation.tags.index(tag.value) >= 0
        except:
            pass
        return False

    @staticmethod
    def splitAnnotations(args: list) -> list:
        """ realiza el proceso de divicion de la lista de anotaciones pasadas a una lista NanopubRequest validas"""
        request = []
        for annotation in args:
            try:
                if NanopubRequest.tagInAnnotation(AnnotationTag.step, annotation):
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
