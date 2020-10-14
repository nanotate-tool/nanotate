from src.models import Nanopublication


class NanopublicationRepository:
    def __init__(self):
        super().__init__()

    def save(self, nanopub: Nanopublication) -> Nanopublication:
        """
        Realiza el almacenado de la nanopublicacion pasada
        """
        if nanopub != None:
            return nanopub.save()
        return None

    def getNanopub(
        self, id: str, protocol=None, default: Nanopublication = None
    ) -> Nanopublication:
        """
        Realiza la consulta de la nanopublicacion asociada a los filtros pasados.
        en caso de la consulta no retornar un valor se retornara el default pasado
        """
        query = {"id": id}
        if protocol != None:
            query["protocol"] = protocol
        dbNanopub = Nanopublication.objects(**query).first()
        dbNanopub = dbNanopub if dbNanopub != None else default
        return dbNanopub

    def getNanopubsByProtocol(self, protocol: str) -> list:
        """
        retorna la lista de nanopublicaciones asociadas a la uri del protocolo pasado
        """
        return Nanopublication.objects(protocol=protocol)
