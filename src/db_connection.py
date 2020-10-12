from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base


class DbConnection:
    """
    Controladora de la conexion a la base de datos
    """

    def __init__(self, url, verbose: bool = False):
        self.engine = create_engine(url, echo=verbose)
        Base.metadata.create_all(self.engine)

    @property
    def session(self) -> Session:
        Session = sessionmaker()
        Session.configure(bind=self.engine)
        session = Session()
        return session