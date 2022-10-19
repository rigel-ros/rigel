from rigel.models.builder import ModelBuilder
from typing import Any, Type
from .registries import ECRPlugin, GenericDockerRegistryPlugin


class Plugin:
    """
    A plugin for Rigel to deploy Docker images to Docker registries.
    """

    plugin_type: Type

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Select the proper plugin based on the specified registry.

        :type args: List[string, object]
        :param args: Required arguments for the plugin.
        :type kwargs: Dict[string, object]
        :param kwargs: Positional arguments for the plugin.
        """

        self.args: Any = args
        self.kwargs: Any = kwargs

        registry_name = kwargs.get('registry') or ''  # defaults to DockerHub

        if registry_name == 'ecr':
            self.plugin_type = ECRPlugin
        else:
            self.plugin_type = GenericDockerRegistryPlugin

        # Build an instance of the specified plugin.
        builder = ModelBuilder(self.plugin_type)
        self.plugin = builder.build(self.args, self.kwargs)

    def run(self) -> None:
        """
        Delegate execution to adequate plugin.
        """
        self.plugin.run()

    def stop(self) -> None:
        """
        Delegate resources cleanup to adequate plugin.
        """
        self.plugin.stop()
