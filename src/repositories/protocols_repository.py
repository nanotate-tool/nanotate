from src.models import Protocol


class ProtocolsRepository:
    def __init__(self):
        super().__init__()

    def save(self, protocol: Protocol) -> Protocol:
        """
        Realiza el almacenado del protocolo pasado
        """
        if protocol != None:
            return protocol.save()
        return None

    def get_protocol(self, uri: str, default: Protocol = None) -> Protocol:
        """
        Realiza la consulta del protocolo asociado a los filtros pasados.
        en caso de la consulta no retornar un valor se retornara el default pasado
        """
        db_protocol = Protocol.objects(uri=uri).first()
        db_protocol = db_protocol if db_protocol != None else default
        return db_protocol