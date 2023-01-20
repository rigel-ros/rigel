from pathlib import Path
from rigel.loggers import get_logger
from rigel.models.package import Target
from rigel.plugins import Plugin as PluginBase
from typing import List
from .models import PluginModel
from .renderer import Renderer

LOGGER = get_logger()


class Plugin(PluginBase):

    def __init__(self, distro: str, targets: List[Target]) -> None:
        super().__init__(distro, targets)
        self.prepare_targets()

    def prepare_targets(self) -> None:
        self.__targets = [
            (package, package_data, PluginModel(laranjas='sdjkfsjdhfsj', distro=self.distro, package=package_data, **plugin_data))
            for package, package_data, plugin_data in self.targets]

    def setup(self) -> None:
        pass  # do nothing

    def run(self) -> None:

        for package, package_data, plugin_model in self.__targets:

            LOGGER.warning(f"Creating files for package '{package}'")

            Path(package_data.dir).mkdir(parents=True, exist_ok=True)

            renderer = Renderer(plugin_model)

            renderer.render('Dockerfile.j2', f'{package_data.dir}/Dockerfile')
            LOGGER.info(f"Created file {package_data.dir}/Dockerfile")

            renderer.render('entrypoint.j2', f'{package_data.dir}/dockerfile_entrypoint.sh')
            LOGGER.info(f"Created file {package_data.dir}/entrypoint.sh")

            if package_data.ssh:
                renderer.render('config.j2', f'{package_data.dir}/dockerfile_config')
                LOGGER.info(f"Created file {package_data.dir}/config")

    def stop(self) -> None:
        pass  # do nothing
