import os
import yaml
from rigel.config import SettingsManager
from rigel.exceptions import RigelError
from rigel.models.rigelfile import Workspace
from rigel.loggers import get_logger
from typing import Dict

LOGGER = get_logger()


class WorkspaceManager:

    workspaces: Dict[str, Workspace] = {}

    def __init__(self, settings: SettingsManager) -> None:

        self.__file = settings.get_setting('workspaces.file')
        self.__root = settings.get_setting('workspaces.root')

        if not os.path.exists(self.__root):
            os.makedirs(self.__root)

        self.load_workspaces()

    def load_workspaces(self) -> None:
        """Load existing Rigel-ROS workspaces.
        """
        dirs = [d.path for d in os.scandir(self.__root) if d.is_dir()]
        for dir in dirs:
            configuration_file_path = f'{dir}/{self.__file}'
            if os.path.isfile(configuration_file_path):
                with open(configuration_file_path, 'r') as configuration_file:
                    workspace_data = yaml.safe_load(configuration_file)
                workspace = Workspace(**workspace_data)
                self.workspaces[workspace.name] = workspace
                LOGGER.debug(f"Loaded workspace {workspace.name}")

    def generate_ws(self, distro: str, name: str) -> None:
        """Generate a new Rigel-ROS workspace.

        :param distro: Desired ROS distribution.
        :type distro: str
        :param name: Unique Rigel-ROS workspace name.
        :type name: str
        """
        if name in self.workspaces:
            raise RigelError(msg=f"A Rigel-ROS workspace already exists with name '{name}'")

        workspace_root = f'{self.__root}/{name}'
        os.makedirs(f'{workspace_root}/src')  # automatically create a 'src' folder

        workspace = Workspace(name=name, distro=distro)
        with open(f'{workspace_root}/{self.__file}', 'w+') as workspace_file:
            workspace_file.writelines(yaml.dump(workspace.dict()))

        self.workspaces[name] = workspace

        LOGGER.info(f"Created new Rigel-ROS workspace '{name}'")

    def get_ws(self, name: str) -> Workspace:
        """Retrieve a Rigel-ROS workspace.

        :param name: Unique Rigel-ROS workspace name.
        :type name: str
        :return: The Rigel-ROS workspace.
        :rtype: Workspace
        """
        try:
            return self.workspaces[name]
        except KeyError:
            raise RigelError(msg=f"No Rigel-ROS workspace was found with name '{name}'")

    def list(self) -> None:
        """ List all existing Rigel-ROS workspaces.
        """
        LOGGER.info('WORKSPACE\t\t\tDISTRO')
        for name, workspace in self.workspaces.items():
            print(f'{name}\t\t\t{workspace.distro}')

    def info(self, name: str) -> None:
        """Retrieve information about a Rigel-ROS workspace.

        :param name: Unique Rigel-ROS workspace name.
        :type name: str
        """
        workspace = self.get_ws(name)
        LOGGER.info(workspace)

    def path(self, name: str) -> str:
        """Retrieve the system path of a Rigel-ROS workspace.

        :param name: The unique Rigel-ROS workspace identifier.
        :type name: str
        :return: The system path for the Rigel-ROS workspace.
        :rtype: str
        """
        self.get_ws(name)
        return f'{self.__root}/{name}'
