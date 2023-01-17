from pydantic import BaseModel, Field, validator
from rigel.exceptions import InvalidValueError
from typing import Dict, List, Literal, Optional, Tuple


class VPCConfig(BaseModel):

    # Required fields
    subnets: List[str]
    securityGroups: List[str] = Field(alias='security_groups')

    # Optional fields
    assignPublicIp: bool = Field(alias='assign_public_ip', default=False)


class Credentials(BaseModel):

    # Required fields
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str


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


class RobotApplication(BaseModel):

    # Required fields
    ecr: str
    command: List[str]

    # Optional fields
    environment: List[str] = []
    tools: List[Tool] = []
    requirements: List[str] = []
    ports: List[Tuple[int, int]] = []


class SimulationApplication(RobotApplication):

    # Optional fields
    worldConfigs: List[Dict[Literal["world"], str]] = Field(alias='world_configs', default=[])


class DataSource(BaseModel):
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


class PluginModel(BaseModel):

    # Required fields
    iam_role: str
    credentials: Credentials
    robot_application: RobotApplication
    simulation_application: SimulationApplication

    # Optional fields
    output_location: Optional[str] = None
    simulation_duration: int = 300  # seconds
    vpc_config: Optional[VPCConfig] = None
    data_sources: List[DataSource] = []
