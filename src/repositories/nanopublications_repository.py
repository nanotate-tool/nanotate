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
        self, protocol, id: str, default: Nanopublication = None
    ) -> Nanopublication:
        """
        Realiza la consulta de la nanopublicacion asociada a los filtros pasados.
        en caso de la consulta no retornar un valor se retornara el default pasado
        """
        dbNanopub = Nanopublication.objects(protocol=protocol, id=id).first()
        dbNanopub = dbNanopub if dbNanopub != None else default
        return dbNanopub
