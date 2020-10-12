from mongoengine import Document, DateTimeField
import datetime
import json


class EntityBase(Document):
    """
    Define el modelo base para los modelos a persistir
    """

    dateTimeFormat = "%Y-%m-%dT%H:%M:%SZ"
    meta = {"abstract": True, "strict": False}

    # fecha de creacion
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    # fecha de ultima actualizacion
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        """ Controladora de almacenamiento"""
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
        return super(EntityBase, self).save(*args, **kwargs)

    def to_json_map(self):
        base_json = json.loads(self.to_json(use_db_field=False))
        base_json["created_at"] = self.created_at.strftime(EntityBase.dateTimeFormat)
        base_json["updated_at"] = self.created_at.strftime(EntityBase.dateTimeFormat)
        if "_id" in base_json:
            base_json.pop("_id")
        return base_json
