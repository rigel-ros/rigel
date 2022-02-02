from importlib import import_module
from rigel.files import (
    ImageConfigurationFile,
    EnvironmentVariable,
    SSHKey
)
from rigel.exceptions import (
    IncompleteRigelfileError,
    MissingRequiredFieldError,
    PluginNotFoundError,
    UnknownFieldError
)
from rigel.plugins import RegistryPlugin, SimulationPlugin
from typing import Any, Dict, List, Tuple, Union

Plugin = Union[RegistryPlugin, SimulationPlugin]
YAMLData = Dict[str, Any]


class RigelfileParser:
    """
    A parser of Rigelfiles.

    :type dockerfile: rigel.files.ImageConfigurationFile
    :cvar dockerfile: Information regarding how to containerize the ROS application.
    :type registry_plugins: List[rigel.files.RegistryPlugin]
    :cvar registry_plugins: List of plugins to be used to deploy the containerized ROS application.
    :type simulation_plugins: List[rigel.files.SimulationPlugin]
    :cvar simulation_plugins: List of plugins to be used to run the containerized ROS application.
    """

    dockerfile: ImageConfigurationFile
    registry_plugins: List[RegistryPlugin]
    simulation_plugins: List[SimulationPlugin]

    def __segment_data(self, yaml_data: YAMLData) -> Tuple[YAMLData, List[YAMLData], List[YAMLData]]:
        """
        Segment the data within a Rigelfile into its constituient logic blocks.

        Each Rigelfile contains YAML data that can be broken into three main logic blocks:
        - 'build': holds all data concerning how to containerize the ROS application.
        - 'deploy': holds all data concerning how and where to deploy the containerized ROS application.
        - 'simulate': holds all data concerning how to start executing the containerized ROS application.

        :type yaml_data: Dict[string, Any]
        :param yaml_data: All the data extracted from a Rigelfile.

        :rtype: Tuple[Dict[string, Any], List[Dict[string, Any]], List[Dict[string, Any]]]
        :return: A tuple containing the segmented data and separated according to logic block.
        """
        # The 'build' block is mandatory and its existence must be checked.
        build_data = yaml_data.get('build')
        if build_data is None:
            raise IncompleteRigelfileError(block='build')

        # The 'deploy' and 'simulate' blocks are not mandatory.
        registry_plugins_data = yaml_data.get('deploy') if 'deploy' in yaml_data else []
        simulation_plugins_data = yaml_data.get('simulate') if 'simulate' in yaml_data else []

        return build_data, registry_plugins_data, simulation_plugins_data

    def __build_dockerfile(self, yaml_data: YAMLData) -> ImageConfigurationFile:
        """
        Parse the data contained within the logical block 'build'.

        :type yaml_data: Dict[string, Any]
        :param yaml_data: All data concerning how to containertize the ROS application.

        :rtype: rigel.files.ImageConfigurationFile
        :return: A data aggregator.
        """
        try:

            if 'ssh' in yaml_data:
                yaml_data['ssh'] = [SSHKey(**key) for key in yaml_data['ssh']]

            envs = []
            if 'env' in yaml_data:
                for env in yaml_data['env']:
                    name, value = env.strip().split('=')
                    envs.append(EnvironmentVariable(name, value))
            yaml_data['env'] = envs

        except TypeError as err:

            message = err.args[0]
            field = message.split()[-1].replace("'", '')

            if 'got an unexpected keyword' in err.args[0]:
                raise UnknownFieldError(field=field)

            elif 'missing' in err.args[0]:
                raise MissingRequiredFieldError(field=field)

        return ImageConfigurationFile(**yaml_data)

    def __load_plugins(self, yaml_data: YAMLData) -> List[Plugin]:
        """
        Parse a list of plugins.

        :type yaml_data:
        :param yaml_data: All data concerning which plugins to use.

        :rtype: Union[List[RegistryPlugin], List[SimulationPlugin]]
        :return: A list of data aggregators.
        """
        plugins = []
        for plugin_data in yaml_data:

            try:

                plugin_name = plugin_data.pop('plugin')

            except KeyError:
                raise MissingRequiredFieldError(field='plugin')

            print(f"Loading plugin '{plugin_name}'.")

            try:

                module = import_module(plugin_name)
                cls = getattr(module, 'Plugin')
                plugins.append(cls(**plugin_data))

            except ModuleNotFoundError:
                raise PluginNotFoundError(plugin=plugin_name)

            print(f"Using external registry plugin '{plugin_name}' .")

        return plugins

    def __init__(self, yaml_data: YAMLData) -> None:
        """
        Class constructor.
        Initializes a data aggregator for each of the main sections of the Rigelfile.

        :type yaml_data: Dict[string, Any]
        :param yaml_data: The data extracted from a Rigelfile.
        """

        build_data, registry_plugins_data, simulation_plugins_data = self.__segment_data((yaml_data))

        self.dockerfile = self.__build_dockerfile(build_data)
        self.registry_plugins = self.__load_plugins(registry_plugins_data)
        self.simulation_plugins = self.__load_plugins(simulation_plugins_data)
