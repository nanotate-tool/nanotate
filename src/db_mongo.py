from mongoengine import connect


class MongoDb:
    """
    Controladora de la conexion a la base de datos Mongo
    """

    connection = None

    def __init__(self, database: str, host: str = "localhost", port: int = 27017):
        self.database = database
        self.host = host
        self.port = port

    def connect(self):
        """
        Realiza el proceso de conexion a la base de datos
        """
        if not self.connection:
            self.connection = connect(db=self.database, host=self.host, port=self.port)
