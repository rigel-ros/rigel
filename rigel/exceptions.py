from pydantic.error_wrappers import ValidationError


class RigelError(Exception):
    """
    The base exception class for all Rigel errors.

    :type base: string
    :var base: The error message.
    :type code: int
    :cvar code: The error code.
    """
    base: str

    def __init__(self, base: str = 'Generic Rigel error.'):
        self.base = base

    def __str__(self) -> str:
        return self.base


class DockerAPIError(RigelError):
    """
    Raised whenever an exception is thrown while making a call to the Docker API.

    :type exception: Exception
    :ivar exception: The exception thrown by the Docker API.
    """
    def __init__(self, exception: Exception) -> None:
        super().__init__(f"An error occured while calling the Docker API: {exception}")
        self.exception = exception


class PydanticValidationError(RigelError):
    """
    Raised whenever a ValidationError is thrown
    while creating instances of pydantic.BaseModel.

    :type exception: pydantic.error_wrappers.ValidationError
    :ivar exception: The exception thrown.
    """
    def __init__(self, exception: ValidationError) -> None:
        super().__init__(f"An error occurred while validating Pydantic model: {exception}.")
        self.exception = exception


class UndeclaredEnvironmentVariableError(RigelError):
    """
    Raised whenever an attempt is made to use the value of an undeclared environment variable.

    :type env: string
    :ivar env: The undeclared environment variable.
    """
    def __init__(self, env: str) -> None:
        super().__init__(f"Environment variable {env} is not declared.")
        self.env = env


class UndeclaredGlobalVariableError(RigelError):
    """
    Raised whenever an undeclared global variable is referenced.

    :type field: string
    :ivar field: Path for the field referencing the global varialble.
    :type var: string
    :ivar var: Global variable identifier.
    """
    def __init__(self, field: str, var: str) -> None:
        super().__init__(f"Field '{field}' set to have the value of undeclared global variable '{var}'.")
        self.field = field
        self.var = var


class RigelfileNotFoundError(RigelError):
    """
    Raised whenever a Rigelfile is required but is not found.
    """
    def __init__(self) -> None:
        super().__init__("Rigelfile was not found. Use 'rigel init' to create one.")


class UnformattedRigelfileError(RigelError):
    """
    Raised whenever an attempt is made to use an unformatted Rigelfile.

    :type trace: string
    :ivar trace: A message detailing what format error was found and where.
    """
    def __init__(self, trace: str) -> None:
        super().__init__(f"Rigelfile is not properly formatted: {trace}.")
        self.trace = trace


class EmptyRigelfileError(RigelError):
    """
    Raised whenever an empty Rigelfile is found.
    """
    def __init__(self) -> None:
        super().__init__("Provided Rigelfile is empty.")


class UnsupportedCompilerError(RigelError):
    """
    Raised whenever an attempt is made to use an unsupported compiler.

    :type compiler: string
    :ivar compiler: The name of the unsupported compiler.
    """
    def __init__(self, compiler: str) -> None:
        super().__init__(f"Unsupported compiler '{compiler}'.")
        self.compiler = compiler


class UnsupportedPlatformError(RigelError):
    """
    Raised whenever an attempt is build an image for an unsupported platform.

    :type compiler: platform
    :ivar compiler: The unsupported platform.
    """
    def __init__(self, platform: str) -> None:
        super().__init__(f"Unsupported platform '{platform}'.")
        self.platform = platform


class PluginNotFoundError(RigelError):
    """
    Raised whenever an attempt is made to load a plugin that is not installed.

    :type plugin: string
    :ivar plugin: Name of the plugin.
    """
    def __init__(self, plugin: str) -> None:
        base = (f"Unable to load plugin '{plugin}'. Make sure plugin is installed in your system.\n"
                "For more information on plugin installation run command 'rigel install --help'.")
        super().__init__(base)
        self.plugin = plugin


class PluginNotCompliantError(RigelError):
    """
    Raised whenever an plugin is loaded that is not compliant with
    the rigel.plugins.Protocol class.

    :type plugin: string
    :ivar plugin: Name of the plugin
    :type cause: string
    :ivar cause: Reason why plugin is not compliant.
    """
    def __init__(self, plugin: str, cause: str) -> None:
        super().__init__(f"Plugin '{plugin}' does not comply with Rigel plugin protocol: {cause}")
        self.plugin = plugin
        self.cause = cause
