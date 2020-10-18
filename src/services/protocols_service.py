from src.repositories import ProtocolsRepository
from src.models import Protocol
from src.utils import site_metadata_puller


class ProtocolsService:
    """
    Servicio para el manejo de los Protocolos
    """

    def __init__(self, protocolsRepo: ProtocolsRepository):
        self.protocolsRepo = protocolsRepo

    def getProtocol(self, uri: str):
        """
        Obtiene los datos del protocolo asociado a la url pasada asi este no
        se encuentre registrado en la plataforma
        """
        protocol = self.protocolsRepo.getProtocol(uri=uri, default=Protocol(uri=uri))
        protocol.site_data = site_metadata_puller.pull_site_metadata(url=uri).to_json()
        return protocol.to_json_map()