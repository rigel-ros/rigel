import boto3
from copy import deepcopy
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.plugins import Plugin as PluginBase
from rigel.providers.aws import AWSProviderOutputModel
from time import sleep
from typing import Any, Dict, List
from .models import PluginModel


LOGGER = get_logger()


class Plugin(PluginBase):

    def __init__(
        self,
        raw_data: PluginRawData,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
        shared_data: Dict[str, Any] = {}  # noqa
    ) -> None:
        super().__init__(
            raw_data,
            global_data,
            application,
            providers_data,
            shared_data
        )

        # Ensure model instance was properly initialized
        self.model = ModelBuilder(PluginModel).build([], self.raw_data)
        assert isinstance(self.model, PluginModel)

        self.__robomaker_client = self.__retrieve_robomaker_client()

    def __retrieve_robomaker_client(self) -> boto3.session.Session.client:

        providers = [provider for _, provider in self.providers_data.items() if isinstance(provider, AWSProviderOutputModel)]

        if not providers:
            raise RigelError(base='No AWS provider were found. This plugin requires a connection to AWS RoboMaker.')
        elif len(providers) > 1:
            raise RigelError(base='Multiple AWS providers was found. Please specify which provider you want to use.')
        else:
            client = providers[0].robomaker_client
            if not client:
                raise RigelError(base='Selected AWS provider is not configured to work with AWS RoboMaker.')
            return client

    def __generate_worlds(self) -> str:

        response = self.__robomaker_client.create_world_generation_job(
            template=self.model.template_arn,
            worldCount={
                'floorplanCount': self.model.floor_plan_count,
                'interiorCountPerFloorplan': self.model.interior_count
            }
        )

        LOGGER.info("Running world generation job")
        generation_job_arn = response["arn"]
        while self.__robomaker_client.describe_world_generation_job(job=generation_job_arn)["status"] != "Completed":
            sleep(0.5)

        LOGGER.info("Finished world generation job")
        return generation_job_arn

    def __get_worlds_information(self, generation_job_arn: str) -> List[str]:

        worlds = self.__robomaker_client.list_worlds()
        world_list = []

        for world in worlds["worldSummaries"]:
            if world["generationJob"] == generation_job_arn:
                world_list.append(world["arn"])

        return world_list

    def __export_worlds(self, worlds: List[str], s3prefix: str) -> List[str]:

        export_job_arns = []

        for world in worlds:
            response = self.__robomaker_client.create_world_export_job(
                worlds=[world],
                outputLocation={
                    's3Bucket': self.model.s3_bucket,
                    's3Prefix': s3prefix
                },
                iamRole=self.model.iam_role
            )

            export_job_arns.append(response["arn"])

        temp_arns = deepcopy(export_job_arns)

        LOGGER.info("Running export job")
        while temp_arns:
            for arn in temp_arns:
                if self.__robomaker_client.describe_world_export_job(job=arn)["status"] == "Completed":
                    temp_arns.remove(arn)
            sleep(0.5)

        LOGGER.info("Finished export job")
        return export_job_arns

    def start(self) -> None:

        generation_job_arn = self.__generate_worlds()
        worlds = self.__get_worlds_information(generation_job_arn)
        export_job_arns = self.__export_worlds(worlds, generation_job_arn)

        exported_jobs = []
        for export_arn in export_job_arns:
            exported_jobs.append({
                "destination": self.model.destination,
                "s3_bucket": self.model.s3_bucket,
                "s3_keys": [f"{generation_job_arn}/aws-robomaker-worldforge-export-{export_arn.split('/export-')[1]}.zip"]
            })

        self.shared_data["worldforge_exported_jobs"] = exported_jobs
