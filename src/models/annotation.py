from __future__ import annotations
from datetime import datetime
import json


class Annotation(object):
    """ Annotation class docs\n

        contiene los datos de una anotacion necesaria para convertir en una nanoplublicacion valida
    """

    def __init__(self, id: str, authority: str, url: str, created: datetime, updated: datetime, title: str, refs: list, isReply: bool, isPagenote: bool,
                 user: str, displayName: str, text: str, prefix: str, exact: str, suffix: str, start: int, end: int, tags: list, group: str,
                 settings: object = None, ontologies: list = [], *args, **kwargs):
        self.id = id  # : "lB7Z3rbsEeqZMm96UVPfMg"
        self.authority = authority  # ": "hypothes.is",
        self.url = url  # : "https:#protocolexchange.researchsquare.com/article/pex-838/v1",
        self.created = created  # : "2020-06-25T14:03:00",
        self.updated = updated  # : "2020-06-25T14:03:00",
        self.title = title  # : "Brain and blood extraction for immunostaining, protein, and RNA # measurements after long-term two photon imaging in mice﻿.",
        self.refs = refs  # ": [],
        self.isReply = isReply  # : false,
        self.isPagenote = isPagenote  # ": false,
        self.user = user  # ": "iannotate",
        self.displayName = displayName  # ": null,
        self.text = text  # ": "",
        self.prefix = prefix  # ": "ProcedureSTEP 1: EuthanasiaWhen ",
        self.exact = exact  # ": "mice",
        self.suffix = suffix  # ": " have reached their endpoint, eu",
        self.start = start  # ": 4219,
        self.end = end  # ": 4223,
        self.tags = tags  # : [ "sample" ],
        self.group = group  # ": "__world__",
        self.ontologies = ontologies
        self.settings = settings

    def var(self, var_key: str) -> list:
        """ retorna el array de valores asociado a la variable pasada en el settings del annotation request """
        return self.settings[var_key] if self.settings else None

    def varIncludes(self, var_key: str, value: str):
        """ true si el valor buscado se encuentra en el array de valores del var_key en el settings del annotation request
            false de lo contrario
        """
        _var = self.var(var_key)
        return _var == None or value in _var

    @staticmethod
    def parseJson(data) -> Annotation:
        """ parsea el contenido json pasado a una instancia de Annotation Valida"""
        return Annotation(**data)

    @staticmethod
    def parseJsonArr(data) -> list:
        """ parsea el array con los json para construir una instancia valida de Annotation @see #parseJson"""
        annotations = []
        for entry in data:
            annotations.append(Annotation.parseJson(entry))
        return annotations
