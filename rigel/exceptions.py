from typing import Any


class RigelError(Exception):
    """
    The base exception class for all Rigel errors.

    :type base: string
    :var base: The error message.
    :type code: int
    :cvar code: The error code.
    """
    base: str = 'Generic Rigel error.'
    code: int = 1

    def __init__(self, **kwargs: Any):
        Exception.__init__(self, self.base.format(**kwargs))
        self.kwargs = kwargs

    def __str__(self) -> str:
        return f'({self.code}) {self.base}'


class DockerAPIError(RigelError):
    """
    Raised whenever an exception is thrown while making a call to the Docker API.

    :type exception: docker.errors.DockerException
    :ivar exception: The exception thrown by the Docker API.
    """
    base = "An error occured while calling the Docker API: {exception}"
    code = 2


class InvalidDockerClientInstanceError(RigelError):
    """
    Raised whenever an invalid Docker client instance is provided.
    """
    base = "An invalid instance of python_on_whales.docker_client.DockerClient was provided."
    code = 4


class PydanticValidationError(RigelError):
    """
    Raised whenever a ValidationError is thrown
    while creating instances of pydantic.BaseModel.

    :type exception: pydantic.error_wrappers.ValidationError
    :ivar exception: The exception thrown.
    """
    base = "An error occurred while validating Pydantic model: {exception}."
    code = 6


class UndeclaredEnvironmentVariableError(RigelError):
    """
    Raised whenever an attempt is made to use the value of an undeclared environment variable.

    :type env: string
    :ivar env: The undeclared environment variable.
    """
    base = "Environment variable {env} is not declared."
    code = 7


class UndeclaredGlobalVariableError(RigelError):
    """
    Raised whenever an undeclared global variable is referenced.

    :type field: string
    :ivar field: Path for the field referencing the global varialble.
    :type var: string
    :ivar var: Global variable identifier.
    """
    base = "Field '{field}' set to have the value of undeclared global variable '{var}'."
    code = 8


class RigelfileNotFoundError(RigelError):
    """
    Raised whenever a Rigelfile is required but is not found.
    """
    base = "Rigelfile was not found. Use 'rigel init' to create one."
    code = 6


class RigelfileAlreadyExistsError(RigelError):
    """
    Raised whenever an attempt is made to create a Rigelfile inside a folder
    that already contains a Rigelfile.
    """
    base = "A Rigelfile already exists. Use '--force' flag to write over existing Rigelfile."
    code = 7


class UnformattedRigelfileError(RigelError):
    """
    Raised whenever an attempt is made to use an unformatted Rigelfile.

    :type trace: string
    :ivar trace: A message detailing what format error was found and where.
    """
    base = "Rigelfile is not properly formatted: {trace}."
    code = 8


class IncompleteRigelfileError(RigelError):
    """
    Raised whenever an attempt is made to use an incomplete Rigelfile.

    :type block: string
    :ivar block: The required block that is missing.
    """
    base = "Incomplete Rigelfile. Missing required block '{block}'."
    code = 9


class EmptyRigelfileError(RigelError):
    """
    Raised whenever an empty Rigelfile is found.
    """
    base = "Provided Rigelfile is empty."
    code = 12


class UnsupportedCompilerError(RigelError):
    """
    Raised whenever an attempt is made to use an unsupported compiler.

    :type compiler: string
    :ivar compiler: The name of the unsupported compiler.
    """
    base = "Unsupported compiler '{compiler}'."
    code = 13


class UnsupportedPlatformError(RigelError):
    """
    Raised whenever an attempt is build an image for an unsupported platform.

    :type compiler: platform
    :ivar compiler: The unsupported platform.
    """
    base = "Unsupported platform '{platform}'."
    code = 14


class InvalidPlatformError(RigelError):
    """
    Raised whenever an attemp to use an invalid platform is made.

    :param RigelError: platform
    :type RigelError: The invalid platform.
    """
    base = "An invalid platform was used: '{platform}'."
    code = 15


class PluginNotFoundError(RigelError):
    """
    Raised whenever an attempt is made to load a plugin that is not installed.

    :type plugin: string
    :ivar plugin: Name of the plugin.
    """
    base = ("Unable to load plugin '{plugin}'. Make sure plugin is installed in your system.\n"
            "For more information on plugin installation run command 'rigel install --help'.")
    code = 17


class PluginInstallationError(RigelError):
    """
    Raised whenever an error occurs while installing an plugin.

    :type plugin: string
    :ivar plugin: Name of the plugin to be installed.
    """
    base = "An error occurred while installing plugin {plugin}."
    code = 18


class PluginNotCompliantError(RigelError):
    """
    Raised whenever an plugin is loaded that is not compliant with
    the rigel.plugins.Protocol class.

    :type plugin: string
    :ivar plugin: Name of the plugin
    :type cause: string
    :ivar cause: Reason why plugin is not compliant.
    """
    base = "Plugin '{plugin}' does not comply with Rigel plugin protocol: {cause}"
    code = 19


class InvalidPluginNameError(RigelError):
    """
    Raised whenever an invalid plugin name is passed.

    :type plugin: string
    :ivar plugin: The invalid plugin name.
    """
    base = "Invalid plugin name '{plugin}'."
    code = 20


class UnknownROSPackagesError(RigelError):
    """
    Raised whenever unlisted ROS package are referenced.

    :type packages: List[string]
    :ivar packages: List of unknown ROS packages.
    """
    base = "The following packages were not declared in the Rigelfile: {packages}."
    code = 21
