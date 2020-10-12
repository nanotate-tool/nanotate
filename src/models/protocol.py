from mongoengine import StringField, IntField, LazyReferenceField, CASCADE
from .entity_base import EntityBase
from .annotation import Annotation


class Protocol(EntityBase):
    """
    Contiene la informacion del protocolo al cual se le realizaran las nanopublicaciones
    """

    meta = {"collection": "protocols", "strict": False}

    # uri de identificacion del protocolo
    uri = StringField(primary_key=True)
    # titulo del protocolo
    title = StringField(required=True, max_length=250)
    # numero maximo de nanopublicaciones para el protocolo
    max_nanopubs = IntField(default=10)
    # nanopublicationes
    nanopublications = LazyReferenceField(
        "Nanopublication", reverse_delete_rule=CASCADE
    )

    @staticmethod
    def fromAnnotation(annotation: Annotation):
        """
        transforma la anotacion (generalmente una anotacionn marcada con 'step') pasada a una un Protocolo
        Annotation -> Protocol
        """
        return Protocol(uri=annotation.url, title=annotation.title[0])

    def to_json_map(self):
        base = super().to_json_map()
        return base
