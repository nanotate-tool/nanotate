from .graph_nanopub import GraphNanopub
from src.models import Workflow
from nanopub import Publication, NanopubClient
import rdflib


class WorkflowNanopub(GraphNanopub):
    """
    represent a graphNanopub builded from Workflow passed
    """

    def __init__(
        self,
        workflow: Workflow,
        settings: dict = None,
        np_client: NanopubClient = None,
    ):
        self.workflow = workflow
        worflow_nanopub = None
        if self.workflow.rdf != None:
            workflow_nanopub_rdf = rdflib.ConjunctiveGraph()
            workflow_nanopub_rdf.parse(data=self.workflow.rdf, format="trig")
            worflow_nanopub = Publication(rdf=workflow_nanopub_rdf)
        elif np_client != None:
            worflow_nanopub = np_client.fetch(
                uri=self.workflow.publication_info["nanopub_uri"]
            )
        else:
            raise "Can't build rdf from workflow passed"

        worflow_nanopub.rdf.bind(
            "", rdflib.Namespace(self.workflow.publication_info["nanopub_uri"] + "#")
        )

        super().__init__(
            author=self.workflow.author, derived_from=[], nanopub=worflow_nanopub
        )
