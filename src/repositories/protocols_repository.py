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

    def getProtocol(self, uri: str, default: Protocol = None) -> Protocol:
        """
        Realiza la consulta del protocolo asociado a los filtros pasados.
        en caso de la consulta no retornar un valor se retornara el default pasado
        """
        dbProtocol = Protocol.objects(uri=uri).first()
        dbProtocol = dbProtocol if dbProtocol != None else default
        return dbProtocol