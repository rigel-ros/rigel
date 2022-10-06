import os
import yaml
from rigel.clients import DockerClient
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from typing import Any

ROS_WORKSPACE_FILE = '.rigel_workspace'
ROS_WORKSPACE_PATH = f"{os.environ.get('HOME')}/.rigel"

LOGGER = get_logger()


class ROSWorkspace:

    @staticmethod
    def new(distro: str, identifier: str) -> None:
        """Generate a new Rigel-ROS workspace.

        :param distro: the desired ROS distribution.
        :type distro: str
        :param identifier: the unique Rigel-ROS workspace identifier.
        :type identifier: str
        """

        path = f'{ROS_WORKSPACE_PATH}/{identifier}'

        try:
            os.makedirs(path)
        except FileExistsError:
            raise RigelError(msg=f"A Rigel-ROS workspace already exists with identifier '{identifier}'")

        docker = DockerClient()
        try:
            # TODO: include code to pull the image
            docker.image.tag(f'rigel-ros:{distro}', f'rigel-ros:{identifier}')
            LOGGER.info(f"Created Docker image 'rigel-ros:{identifier}'")
        except RigelError as err:
            raise err

        # TODO: Include all data inside a proper Rigelfile.
        with open(f'{path}/{ROS_WORKSPACE_FILE}', 'w+') as workspace_file:
            workspace_data = {'ros_workspace': {'distro': distro, 'identifier': identifier}}
            workspace_file.writelines(yaml.dump(workspace_data))

        LOGGER.info(f"Rigel-ROS workspace '{identifier}' created with success ({path}).")

    @staticmethod
    def list() -> None:
        """ List all existing ROS workspaces.
        """

        if not os.path.exists(ROS_WORKSPACE_PATH):
            os.makedirs(ROS_WORKSPACE_PATH)

        LOGGER.info('WORKSPACE\t\t\tDISTRO')
        for path in os.listdir(ROS_WORKSPACE_PATH):

            # TODO: Read workspace data from within Rigelfile.
            workspace_file_path = f'{ROS_WORKSPACE_PATH}/{path}/{ROS_WORKSPACE_FILE}'
            if os.path.isfile(workspace_file_path):
                with open(workspace_file_path) as workspace_file:
                    workspace_data = yaml.safe_load(workspace_file)['ros_workspace']
                    print(f"{workspace_data['identifier']}\t\t\t{workspace_data['distro']}")

    @staticmethod
    def tty(identifier: str) -> None:
        """Open a terminal inside a Rigel-ROS workspace.

        :param identifier: the unique Rigel-ROS workspace identifier.
        :type identifier: str
        """

        path = f'{ROS_WORKSPACE_PATH}/{identifier}'

        # Ensure that the workspace exists
        if not os.path.exists(path):
            raise RigelError(msg=f"Workspace '{identifier}' was not found")

        docker = DockerClient()
        docker.run_container(
            identifier,
            f'rigel-ros:{identifier}',
            command=['/bin/bash'],
            hostname=identifier,
            interactive=True,
            tty=True,
            volumes=[(path, "/home/rigel/ros_workspace/")]
        )

    @staticmethod
    def info(identifier: str) -> Any:
        """Retrieve information about a Rigel-ROS workspace.

        :param identifier: the unique Rigel-ROS workspace identifier.
        :type identifier: str
        :return: ROS workspace information.
        :rtype: Dict[str, str]
        """
        workspace_path = f'{ROS_WORKSPACE_PATH}/{identifier}'
        if not os.path.isdir(workspace_path):
            raise RigelError(msg=f"No Rigel-ROS workspace '{identifier}' was found.")

        workspace_file_path = f'{workspace_path}/{ROS_WORKSPACE_FILE}'
        if not os.path.isfile(workspace_file_path):
            raise RigelError(msg=f"Directory '{workspace_path}' is not a valid Rigel-ROS workspace.")

        with open(workspace_file_path) as workspace_file:
            workspace_data = yaml.safe_load(workspace_file)

        return workspace_data
