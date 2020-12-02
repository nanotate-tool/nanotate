class WorkflowRequest:
    """
    defines the model for creation request of workflow
    """

    id: str = None
    protocol: str
    label: str
    description: str
    nanopubs: list
    author: str

    def __init__(self, *args, **kwargs):
        if kwargs != None:
            self.__dict__.update(kwargs)