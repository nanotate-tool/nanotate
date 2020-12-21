from mongoengine import StringField, IntField, LazyReferenceField, CASCADE
from .entity_base import EntityBase
from .annotation import Annotation
from src.utils.site_metadata_puller import clean_url_with_settings


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
    # site data
    site_data = {}

    @staticmethod
    def fromAnnotation(annotation: Annotation, settings: dict = None):
        """
        transforma la anotacion (generalmente una anotacionn marcada con 'step') pasada a una un Protocolo
        Annotation -> Protocol
        """
        return Protocol(
            uri=clean_url_with_settings(annotation.url, settings=settings),
            title=annotation.title[0],
        )

    def to_json_map(self):
        base = super().to_json_map()
        base["site_data"] = self.site_data
        return base
