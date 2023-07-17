from pydantic import BaseModel, Extra
from typing import Dict, Union
from .application import Application
from .data import ComplexDataModel, SimpleDataModel
from .plugin import PluginDataModel
from .provider import ProviderDataModel
from .sequence import Sequence

RigelfileGlobalData = Dict[str, Union[ComplexDataModel, SimpleDataModel]]


class Rigelfile(BaseModel, extra=Extra.forbid):
    """A placeholder for information regarding jobs of a ROS application.

    :type application: Application
    :cvar application: General information about the ROS application.
    :type jobs: Dict[str, PluginDataModel]
    :cvar jobs: The jobs supported by the package.
    :type sequences: Dict[str, Sequence]
    :cvar sequences: The supported sequence of jobs.
    :type providers: Dict[str, ProviderDataModel]
    :cvar providers: A list of required providers.
    :type vars: Dict[str, Any]
    :cvar vars: Section containing the values of global variables.
    """

    # Required fields.
    application: Application
    jobs: Dict[str, PluginDataModel]

    # Optional fields.
    providers: Dict[str, ProviderDataModel] = {}
    sequences: Dict[str, Sequence] = {}
    vars: RigelfileGlobalData = {}
