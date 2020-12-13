from mongoengine.fields import (
    StringField,
    DBRef,
    ListField,
    ObjectIdField,
    ReferenceField,
    DictField,
    BooleanField,
)
from .nanopublication import Nanopublication
from .entity_base import EntityBase


class Workflow(EntityBase):
    meta = {"collection": "workflows"}

    # identify
    id = StringField(required=True, primary_key=True)
    # protocol uri
    protocol = StringField(required=True)
    # label
    label = StringField(required=True, max_length=250)
    # description
    description = StringField(required=True, max_length=1000)
    # list of nanoPublications with which it was built
    nanopubs = ListField(ReferenceField(Nanopublication, dbref=True))
    # author of workflow
    author = StringField(required=True, max_length=120)
    # info about fairworkflows publication
    publication_info = DictField()
    # local rdf
    rdf = StringField(required=True)

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

    def to_json_map(self):
        base = super().to_json_map()
        try:
            base["nanopubs"] = list(
                map((lambda nanopub: nanopub.to_json_map()), self.nanopubs)
            )
        except Exception as e:
            base["nanopubs"] = []

        base["permissions"] = self.permissions
        return base
