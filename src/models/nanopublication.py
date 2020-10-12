from sqlalchemy import Column, CHAR, databases, ForeignKey, ARRAY, String, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class Nanopublication(BaseModel):
    """
    Contiene los datos de las nanopublicaciones
    """

    __tablename__ = "nanopubs"

    id = Column(CHAR(100), primary_key=True, nullable=False)
    protocol_id = Column(CHAR(250), ForeignKey("protocols.uri"), nullable=False)
    protocol = relationship("Protocol", back_populates="nanopubs")
    # tags = Column(ARRAY(String, dimensions=1))
    # ontologies = Column(ARRAY(String, dimensions=1))
    rdf_raw = Column(Text)
