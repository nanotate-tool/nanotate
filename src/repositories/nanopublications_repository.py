from src.neo4j_db import Neo4jDB
import rdflib
from neo4j.graph import Graph


class NanoPublicationsRepository:
    """
    """

    def __init__(self, _db: Neo4jDB):
        print("loading repository with", type(_db))
        self.db = _db

    def getAllNanopubs(self):
        result = self.db.rdfPost("MATCH(n)-[r]->(re) return n,r,re ")
        graph = rdflib.ConjunctiveGraph().parse(
            data=result, format="turtle", publicID="ds"
        )
        print(result.decode("utf-8"))
        print(graph.serialize(format="trig").decode("utf-8"))

    def getAllNanopubs2(self):
        result:Graph = self.db.read_transaction(self._getAllNanopubs)

        print(result.relationships.__getitem__("uri"))

        print(result.nodes)
        print(result)

    @staticmethod
    def _getAllNanopubs(tx):
        result = tx.run("MATCH(n)-[r]->(re) return n,r,re")
        return result.graph()
