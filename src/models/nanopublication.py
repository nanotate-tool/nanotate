from mongoengine import (
    StringField,
    ReferenceField,
    CASCADE,
    ListField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    EmbeddedDocument,
    DictField,
)
from .entity_base import EntityBase
from .annotation import Annotation
from .annotation_tag import AnnotationTag
import functools


class OntologyInfo(EmbeddedDocument):
    label = StringField()
    url = StringField()
    term = StringField()
    selector = DictField()

    meta = {"strict": False}


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
    # list with info of selected ontologies
    ontologies_info = EmbeddedDocumentListField(OntologyInfo)
    # contains data of text position of annotation
    text_position = DictField()

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
                        text_position={
                            "start": annotation.start,
                            "end": annotation.end,
                        },
                    ),
                    annotation,
                ),
                # filter only annotations
                filter(lambda arg: type(arg) is Annotation, annotations),
            )
        )
        return components


class PublicationInfo(EmbeddedDocument):
    """
    contiene datos relacionados de la publicacion de la nanopublicacion de forma remota
    """

    nanopub_uri = StringField()
    artifact_code = StringField()

    meta = {"strict": False}


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
    # determina el generate at de la nanopublicacion
    generatedAtTime = StringField()
    # informacion de la publicacion remota de la nanopublicacion
    publication_info = EmbeddedDocumentField(PublicationInfo)
    # associated workflows of this nanopublication (field must be manual loaded)
    workflows = []

    def componentsByTag(self, tag: str) -> list:
        """
        retorna los componentes de la nanopublicacion que tengan la etiqueta pasada
        """
        return list(
            filter(
                (lambda component: tag in component.tags),
                self.components,
            )
        )

    @property
    def permissions(self) -> dict:
        """
        returns the security actions and who can do
        """
        return {
            "read": [self.author, "any"],
            "update": [self.author],
            "delete": [self.author],
        }

    @property
    def title(self):
        step = self.componentsByTag(AnnotationTag.step.value)
        if step != None and len(step) > 0:
            return functools.reduce(
                (lambda a, component: a + component.term + " "), step, ""
            )
        else:
            return "Nanopublication " + self.id

    def to_json_map(self):
        base = super().to_json_map()
        # workflows
        if len(self.workflows) > 0:
            base["workflows"] = list(
                map(
                    (
                        lambda workflow: {
                            "id": workflow.id,
                            "label": workflow.label,
                            "description": workflow.description,
                        }
                    ),
                    self.workflows,
                )
            )
            base["hasWorkflows"] = True

        base["title"] = self.title
        base["permissions"] = self.permissions
        return base
