from sqlalchemy import Column, CHAR, String, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel


class Protocol(BaseModel):
    """
    Contiene la informacion del protocolo al cual se le realizaran las nanopublicaciones
    """

    __tablename__ = "protocols"
    # uri de identificacion del protocolo
    uri = Column(CHAR(250), nullable=False, primary_key=True)
    # titulo del protocolo
    title = Column(String(250), nullable=False)
    # numero maximo de nanopublicaciones para el protocolo
    max_nanopubs = Column(Integer, default=10)
    # nanopublicaciones
    nanopubs = relationship("Nanopublication", back_populates="protocol")

    def __repr__(self):
        return "<Protocol(uri='%s', title='%s', max_nanopubs='%s')>" % (
            self.uri,
            self.title,
            self.max_nanopubs,
        )