from .nanopublication import Nanopublication


class Neo4jNanopublication(Nanopublication):
    """
    Representa una nanopublicacion generada desde la base de datos de Neo4j
    """

    def __init__(self, npNamespace, rdf_base=None):
        super().__init__(npNamespace, rdf_base=rdf_base)