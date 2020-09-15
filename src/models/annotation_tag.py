from enum import Enum


class AnnotationTag(Enum):
    """ Annotation Tag docs\n

        determina los tipos de tags disponibles en las Annotations
    """
    step = "step"
    sample = "sample"
    reagent = "reagent"
    equipment = "equipment"
    input = "input"
    output = "output"
    software = "software"