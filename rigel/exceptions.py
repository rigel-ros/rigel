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

    def __init__(self, **kwargs):
        Exception.__init__(self, f'[ERROR {self.code}] {self.base.format(**kwargs)}')
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
    base = "A Rigelfile already exists. Use '--new' flag to write over existing Rigelfile."
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

class EmptyRigelfileError(RigelError):
    """
    Raised whenever an empty Rigelfile is found.
    """
    base = "Provided Rigelfile is empty."
    code = 6

class UnsupportedCompilerError(RigelError):
    """
    Raised whenever an attempt is made to use an unsupported compiler.

    :type compiler: string
    :ivar compiler: The name of the unsupported compiler.
    """
    base = "Unsupported compiler '{compiler}'."
    code = 7
