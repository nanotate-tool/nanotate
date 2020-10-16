from mongoengine import connect


class MongoDb:
    """
    Controladora de la conexion a la base de datos Mongo
    """

    connection = None

    def __init__(
        self, database: str, host: str = "localhost", port: int = 27017, auth=None
    ):
        self.database = database
        self.host = host
        self.port = port
        self.auth = auth

    def connect(self):
        """
        Realiza el proceso de conexion a la base de datos
        """
        if not self.connection:
            settings = {
                "db": self.database,
                "host": self.host,
                "port": self.port,
                "connect": False,
            }
            if self.auth != None and type(self.auth) is dict:
                settings["username"] = self.auth["user"]
                settings["password"] = self.auth["password"]
                pass
            self.connection = connect(**settings)
