from fairworkflows import FairWorkflow, FairStep
from nanopub import NanopubClient
from src.models import Workflow
from src.models.workflow_request import WorkflowRequest
from src.repositories import WorkflowsRepository, NanopublicationRepository
from src.adapters import WorkflowNanopub
from bson.objectid import ObjectId
from src.utils.site_metadata_puller import clean_url_with_settings


class WorkflowsService:
    """
    service specialized for task of workflows
    """

    def __init__(
        self,
        workflows_repository: WorkflowsRepository,
        nanopubs_repository: NanopublicationRepository,
        nanopub_client: NanopubClient,
        settings: dict = None,
    ):
        self.workflows_repository = workflows_repository
        self.nanopubs_repository = nanopubs_repository
        self.settings = settings
        self.nanopub_client = nanopub_client

    def workflows_of_protocol(
        self, protocol_uri: str, json: bool = False, rdf_format: str = "trig"
    ):
        clean_protocol_uri = clean_url_with_settings(
            url=protocol_uri, settings=self.settings
        )
        workflows = self.workflows_repository.get_workflows_of_protocol(
            protocol_uri=clean_protocol_uri
        )
        return list(
            map(
                lambda workflow: self.__export_workflow(
                    workflow=workflow, json=json, rdf_format=rdf_format
                ),
                workflows,
            )
        )

    def get_workflow(
        self, workflow_id: str, json: bool = False, rdf_format: str = "trig"
    ):
        workflow = self.workflows_repository.get_workflow(id=workflow_id)
        return self.__export_workflow(
            workflow=workflow, json=json, rdf_format=rdf_format
        )

    def create(self, workflow: WorkflowRequest):
        """
        makes the process of creation of Workflow from WorkflowRequest passed\n
            params:
                workflow: workflow request to save
        """
        nanopubs = list(
            map(
                lambda nanopub_key: self.nanopubs_repository.getNanopub(id=nanopub_key),
                workflow.nanopubs,
            )
        )
        if len(nanopubs) <= 0:
            return {"status": "error", "cause": "not steps found"}
        # save new workflow
        dbWorflow = Workflow(
            id=str(ObjectId()),
            label=workflow.label,
            description=workflow.description,
            protocol=workflow.protocol,
            author=workflow.author,
            nanopubs=nanopubs,
        )
        # publication and rdf rescue
        dbWorflow.publication_info = self.publish_to_fairworkflow(workflow=dbWorflow)
        dbWorflow.rdf = WorkflowNanopub(
            workflow=dbWorflow, settings=self.settings, npClient=self.nanopub_client
        ).serialize("trig")
        # saving
        dbWorflow = self.workflows_repository.save(dbWorflow)

        return {"status": "ok", "data": dbWorflow.to_json_map()}

    def delete(self, workflow_key: str):
        """
        deletes the workflow associated to key passed\n
            params:
                workflow_key: workflow key
        """
        workflow = self.workflows_repository.get_workflow(id=workflow_key)
        if workflow != None:
            result = self.workflows_repository.delete(workflow)
            if result != None and result["status"] == "ok":
                self.retract_in_fairworkFlow(workflow=workflow)

            return result
        else:
            return {"status": "error", "message": "Workflow not found"}

    def publish_to_fairworkflow(self, workflow: Workflow):
        """
        makes the publication of the workflow in fairworkflows api\n
            params :\n
                workflow: workflow to be published
        """
        in_test_mode = not self.settings["production"]
        fair_workflow = FairWorkflow(
            description=workflow.description, label=workflow.label
        )
        # steps insertion from workflow
        before_fair_step = None
        for step in workflow.nanopubs:
            fair_step = FairStep.from_nanopub(
                uri=step.publication_info.nanopub_uri + "#step",
                use_test_server=in_test_mode,
            )
            if before_fair_step == None:
                fair_workflow.first_step = fair_step
            else:
                fair_workflow.add(fair_step, follows=before_fair_step)
            before_fair_step = fair_step

        # validates
        fair_workflow.validate()
        # publish
        publication_info = fair_workflow.publish_as_nanopub(
            use_test_server=in_test_mode,
            publication_attributed_to=WorkflowNanopub.AUTU[
                WorkflowNanopub.clear_author_name(workflow.author)
            ],
        )
        return publication_info

    def retract_in_fairworkFlow(self, workflow: Workflow = None):
        """
        makes the process of retraction of Workflow passed that was published remotely\n
            params:\n
                workflow: workflow to be retracted
        """
        try:
            if workflow != None and workflow.publication_info != None:
                delete = self.nanopub_client.retract(
                    uri=workflow.publication_info["nanopub_uri"], force=True
                )
            else:
                raise "empty nanopub_uri for retract in workflow passed"
        except Exception as e:
            print("have error on remote retracting", e.__class__, e)
            return None

    def __export_workflow(
        self, workflow: Workflow, json: bool = False, rdf_format: str = None
    ):
        if workflow != None:
            if rdf_format != None and rdf_format != "trig":
                workflow.rdf = WorkflowNanopub(
                    workflow=workflow,
                    settings=self.settings,
                    npClient=self.nanopub_client,
                ).serialize(rdf_format)
            return workflow.to_json_map() if json else workflow
        else:
            return {"error": "not-found"}