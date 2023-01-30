from pydantic import BaseModel, Extra
from typing import List, Dict, Union
from .application import Application
from .data import ComplexDataModel, SimpleDataModel
from .provider import ProviderDataModel

RigelfileGlobalData = Dict[str, Union[ComplexDataModel, SimpleDataModel]]


class Rigelfile(BaseModel, extra=Extra.forbid):
    """A placeholder for information regarding a set of ROS packages.

    Each set may contain multiple ROS packages
    supporting the execution of individual jobs and job sequences.

    :type applications: Dict[str, Application]
    :cvar applications: The set of relevant ROS applications.
    :type sequences: Dict[str, List[str]]
    :cvar sequences: The supported sequence of jobs.
    :type providers: Dict[str, ProviderDataModel]
    :cvar providers: A list of required providers.
    :type vars: Dict[str, Any]
    :cvar vars: Section containing the values of global variables.
    """

    # Required fields.
    applications: Dict[str, Application]

    # Optional fields.
    providers: Dict[str, ProviderDataModel] = {}
    sequences: Dict[str, List[str]] = {}
    vars: RigelfileGlobalData = {}
