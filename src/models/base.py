from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    """
    Define el modelo base para todas los modelos que se persistiran en la base de datos
    """

    __abstract__ = True
    # fecha de creacion
    created_at = Column(DateTime, default=func.current_timestamp())
    # fecha de ultima actualizacion
    updated_at = Column(
        DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
