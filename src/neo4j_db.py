from neo4j import GraphDatabase, api
import urllib.request
import urllib.parse
import json
import base64


class Neo4jDB:
    """
    Conector a la base de datos de Neo4jDB
    """

    def __init__(self, http_url: str, uri: str, db: str, user: str, password: str):
        self.database = db
        self.http_url = http_url
        self.uri = uri
        self.auth = (user, password)
        self.driver = GraphDatabase.driver(uri, auth=self.auth)

    def close(self):
        self.driver.close()

    def read_transaction(self, query_fn, *args, **kwargs):
        with self.driver.session(database=self.database) as session:
            dataset = session.read_transaction(query_fn, *args, **kwargs)
        return dataset

    def write_transaction(self, query_fn, *args, **kwargs):
        with self.driver.session(database=self.database) as session:
            dataset = session.write_transaction(query_fn, *args, **kwargs)
        return dataset

    def __withSession(self):
        pass

    def rdfPost(self, query: str):
        opener = urllib.request.build_opener()
        opener.addheaders = [self.__basicHttpAuthorizationHeader()]
        return opener.open(
            self.__httpUrl("rdf/" + self.database + "/cypher"),
            json.dumps({"cypher": query, "format": "Turtle"}).encode("utf-8"),
        ).read()

    def __httpUrl(self, post: str):
        """ self.http_url + post pasado """
        return self.http_url + "/" + post

    def __basicHttpAuthorizationHeader(self):
        """
        Cabezera de authenticacion http construido a partir de las creadenciales de la instancia
        """
        basic = self.auth[0] + ":" + self.auth[1]
        encoded = str(base64.b64encode(basic.encode("utf-8")), "utf-8")
        return ("Authorization", "Basic " + encoded)
