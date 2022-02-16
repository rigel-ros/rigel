from typing import Union


class RigelError(Exception):
    """
    The base exception class for all Rigel errors.

    :type base: string
    :var base: The error message.
    :type code: int
    :cvar code: The error code.
    """
    base = 'Undefined Rigel error.'
    code = 1

    def __init__(self, **kwargs: Union[str, int, float]):
        Exception.__init__(self, self.base.format(**kwargs))
        self.kwargs = kwargs


class RigelfileNotFound(RigelError):
    """
    Raised whenever a Rigelfile is required but is not found.
    """
    base = "Rigelfile was not found. Use 'rigel init' to create one."
    code = 2


class RigelfileAlreadyExistsError(RigelError):
    """
    Raised whenever an attempt is made to create a Rigelfile inside a folder
    that already contains a Rigelfile.
    """
    base = "A Rigelfile already exists. Use '--force' flag to write over existing Rigelfile."
    code = 3


class UnformattedRigelfileError(RigelError):
    """
    Raised whenever an attempt is made to use an unformatted Rigelfile.

    :type trace: string
    :ivar trace: A message detailing what format error was found and where.
    """
    base = "Rigelfile is not properly formatted: {trace}."
    code = 4


class IncompleteRigelfileError(RigelError):
    """
    Raised whenever an attempt is made to use an incomplete Rigelfile.

    :type block: string
    :ivar block: The required block that is missing.
    """
    base = "Incomplete Rigelfile. Missing required block '{block}'."
    code = 5


class UndeclaredValueError(RigelError):
    """
    Raised whenever a Rigelfile is declared with undefined values.

    :type path: string
    :ivar path: The value that was left undefined.
    """
    base = "Invalid Rigelfile. Field '{path}' was declared but left undefined."
    code = 6


class EmptyRigelfileError(RigelError):
    """
    Raised whenever an empty Rigelfile is found.
    """
    base = "Provided Rigelfile is empty."
    code = 7


class UnsupportedCompilerError(RigelError):
    """
    Raised whenever an attempt is made to use an unsupported compiler.

    :type compiler: string
    :ivar compiler: The name of the unsupported compiler.
    """
    base = "Unsupported compiler '{compiler}'."
    code = 8


class MissingRequiredFieldError(RigelError):
    """
    Raised whenever an attempt is made to create an entity with insufficient data.

    :type field: string
    :ivar field: Name of the missing field.
    """
    base = "Required field '{field}' is missing."
    code = 9


class UndeclaredGlobalVariable(RigelError):
    """
    Raised whenever an attempt is made to use an undeclared global variable.

    :type var: string
    :ivar var: Name of the undeclared global variable.
    :type field: string
    :ivar field: Path for the field referencing the global varialble.
    """
    base = "Field '{field}' set to have the value of undeclared global variable '{var}'."
    code = 10


class PluginNotFoundError(RigelError):
    """
    Raised whenever an attempt is made to load a plugin that is not installed.

    :type plugin: string
    :ivar plugin: Name of the plugin.
    """
    base = "Unable to load plugin '{plugin}'. Not installed."
    code = 11


class DockerBuildError(RigelError):
    """
    Raised whenever an error occurs while building a Docker image.

    :type msg: string
    :ivar msg: The error message as provided by the Docker API.
    """
    base = "An error occurred while building Docker image: {msg}."
    code = 12


class PluginInstallationError(RigelError):
    """
    Raised whenever an error occurs while installing an external plugin.

    :type repository: string
    :ivar repository: URL for the external plugin's repository.
    """
    base = "An error occurred while installing external plugin from: {repository}."
    code = 13
