from src.models.workflow import Workflow, Nanopublication


class WorkflowsRepository:
    def __init__(self):
        super().__init__()

    def save(self, workflow: Workflow) -> Workflow:
        """
        save the workflow passed\n
            params:
                workflow: Workflow to save
        """
        if workflow != None:
            return workflow.save()
        return None

    def get_workflows_of_protocol(self, protocol_uri: str):
        """
        returns workflows associated to protocol_uri passed\n
            params:
                protocol_uri: protocol uri
        """
        return Workflow.objects(protocol=protocol_uri)

    def get_workflow(self, id: str) -> Workflow:
        """
        returns the workflow associated to key passed\n
            params:
                id: key of workflow
        """
        db_workflow = Workflow.objects(id=id).first()
        return db_workflow

    def delete(self, workflow: Workflow):
        """
        deletion of the workflow\n
            params:
                workflow: workflow to delete
        """
        if workflow != None:
            workflow.delete()
            return {"status": "ok"}

        return None

    def get_workflows_of_nanopub(self, nanopub_id: str) -> list:
        """
        returns the list of workflows associated to nanopub_id passed\n
            params:
                nanopub_id: nanopublication identifier
        """
        return Workflow.objects(nanopubs__in=Nanopublication.objects(id=nanopub_id))