from mongoengine import connect, get_connection
from src.db_mongo import MongoDb
import mongomock

class MockMongoDb(MongoDb):
    def __init__(
        self
    ):
        super().__init__("mock")

    def connect(self):
        self.connection = connect('mongoenginetest', host='mongomock://localhost')
        conn = get_connection()
