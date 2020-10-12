from mongoengine import (
    StringField,
    ReferenceField,
    CASCADE,
    ListField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    EmbeddedDocument,
)
from .entity_base import EntityBase
from .annotation import Annotation


class NanopublicationComponent(EmbeddedDocument):
    """
    Contiene los datos de los componentes que contiene una nanopublicacion
    """

    id = StringField()
    # termino relacionado al componente
    term = StringField()
    # lista de tags de la nanopublicacion
    tags = ListField(StringField(max_length=25))
    # lista de ontologias
    ontologies = ListField(StringField(max_length=25))
    # lista de annotaciones relacionadas a la ontologia
    rel_uris = ListField(StringField(max_length=350))

    @staticmethod
    def fromAnnotations(annotations: list, iterator=None) -> list:
        """
        transforma las anotaciones pasada a una lista de componentes parauna nanopublicacion
        Annotation list -> NanopublicationComponent list
        """

        def empty_iterator(nc, an):
            return nc

        iterator = iterator if callable(iterator) else empty_iterator
        components = []
        components = list(
            map(
                lambda annotation: iterator(
                    NanopublicationComponent(
                        id=annotation.id,
                        term=annotation.exact,
                        tags=annotation.tags,
                        ontologies=annotation.ontologies,
                    ),
                    annotation,
                ),
                # filter only annotations
                filter(lambda arg: type(arg) is Annotation, annotations),
            )
        )
        return components


class Nanopublication(EntityBase):
    """
    Contiene los datos de las nanopublicaciones
    """

    meta = {"collection": "nanopublications"}
    # identificador de la nanopublicacion
    id = StringField(primary_key=True)
    # nombre del autor de la nanopublicacion
    author = StringField(required=True, max_length=120)
    # protocolo al que pertenece
    protocol = ReferenceField("Protocol")
    # componentes de la nanopublicacion
    components = EmbeddedDocumentListField(NanopublicationComponent)
    # raw del rdf en formato trig
    rdf_raw = StringField(required=True)
