from pydantic import BaseModel, Extra, Field, validator
from rigel.exceptions import InvalidValueError
from typing import Dict, List, Literal, Optional, Tuple

DEFAULT_ROBOT_APPLICATION_NAME: str = 'rigel_robomaker_robot_application'
DEFAULT_SIMULATION_APPLICATION_NAME: str = 'rigel_robomaker_simulation_application'


class VPCConfig(BaseModel, extra=Extra.forbid):

    # Required fields
    subnets: List[str]
    securityGroups: List[str] = Field(alias='security_groups')

    # Optional fields
    assignPublicIp: bool = Field(alias='assign_public_ip', default=False)


class Tool(BaseModel):

    """Information about tools configured for the robot application.
    :param command: Command-line arguments for the tool. It must include the tool executable name.
    :type command: str
    :param exit_behavior: Exit behavior determines what happens when your tool quits running.
        RESTART will cause your tool to be restarted.
        FAIL will cause your job to exit. The default is RESTART .
    :type exit_behavior: bool
    :type name: bool
    :param name: The name of the tool.
    :type name: str
    :param streamOutputToCloudWatch: Boolean indicating whether logs will be recorded in CloudWatch for the tool.
        The default is False.
    :type streamOutputToCloudWatch: bool
    :param streamUI: Boolean indicating whether a streaming session will be configured for the tool.
        If True, AWS RoboMaker will configure a connection so you can interact with the tool as it is running in the simulation.
        It must have a graphical user interface. The default is False.
    :type streamUI: bool
    """

    class Config:
        allow_population_by_field_name = True
        extra = Extra.forbid

    # Required fields
    name: str
    command: str

    # Optional fields.
    exitBehavior: str = Field(alias='exit_behaviour', default='RESTART')
    streamOutputToCloudWatch: bool = Field(alias='stream_output_to_cloud_watch', default=False)
    streamUI: bool = Field(alias='stream_ui', default=False)

    @validator('exitBehavior')
    def validate_exit_behavior(cls, exitBehavior: str) -> str:
        """
        Ensure that field 'exitBehavior' is valid.
        """
        if exitBehavior not in ['FAIL', 'RESTART']:
            raise InvalidValueError(field='exitBehavior', value=exitBehavior)
        return exitBehavior


class RobotApplication(BaseModel, extra=Extra.forbid):

    # Required fields
    ecr: str
    command: List[str]

    # Optional fields
    name: str = DEFAULT_ROBOT_APPLICATION_NAME
    environment: List[str] = []
    ports: List[Tuple[int, int]] = []
    streamUI: bool = Field(alias='stream_ui', default=False)
    tools: List[Tool] = []


class SimulationApplication(RobotApplication):

    # Optional fields
    name: str = DEFAULT_SIMULATION_APPLICATION_NAME
    worldConfigs: List[Dict[Literal["world"], str]] = Field(alias='world_configs', default=[])


class DataSource(BaseModel, extra=Extra.forbid):
    """A data source consists of read-only files from S3
    used into RoboMaker simulations.
    """

    # Required field
    name: str
    s3Bucket: str = Field(alias='s3_bucket')
    s3Keys: List[str] = Field(alias='s3_keys')

    # Optional fields:
    type: str = 'File'
    destination: str

    @validator('type')
    def validate_data_source_type(cls, ds_type: str) -> str:
        """
        Ensure that field 'type' is valid.
        """
        if ds_type not in ['Prefix', 'Archive', 'File']:
            raise InvalidValueError(field='type', value=ds_type)
        return ds_type

    # TODO: add validator to ensure that field 'destination'
    # is set according to the value of field 'type'


class PluginModel(BaseModel, extra=Extra.forbid):

    # Required fields
    iam_role: str
    robot_application: RobotApplication
    simulation_application: SimulationApplication

    # Optional fields
    output_location: Optional[str] = None
    simulation_duration: int = 300  # seconds
    simulation_ignore: int = 0  # seconds
    vpc_config: Optional[VPCConfig] = None
    data_sources: List[DataSource] = []
