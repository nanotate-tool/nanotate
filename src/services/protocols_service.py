from src.repositories import ProtocolsRepository
from src.models import Protocol
from src.utils import site_metadata_puller
from src.utils.site_metadata_puller import clean_url_with_settings


class ProtocolsService:
    """
    Servicio para el manejo de los Protocolos
    """

    def __init__(self, protocols_repo: ProtocolsRepository, settings: dict):
        self.protocols_repo = protocols_repo
        self.settings = settings

    def get_protocol(self, uri: str):
        """
        returns data of protocol related to passed url even if it is not registered\n
            params:
                url:url of protocol
        """
        clean_url = clean_url_with_settings(url=uri, settings=self.settings)
        protocol = self.protocols_repo.get_protocol(uri=clean_url, default=Protocol(uri=clean_url))
        protocol.site_data = site_metadata_puller.pull_site_metadata(url=uri, settings=self.settings).to_json()
        return protocol.to_json_map()