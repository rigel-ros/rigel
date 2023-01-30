from pydantic import BaseModel, Extra, root_validator
from rigel.exceptions import RigelError
from typing import List, Optional


#
# INPUT MODELS
#

class SSHKeyGroup(BaseModel, extra=Extra.forbid):

    # Required fields
    hostname: str
    env: Optional[str] = None
    path: Optional[str] = None

    @root_validator(allow_reuse=True)
    def check_mutually_exclusive_fields(cls, values):
        env = values.get('env')
        path = values.get('path')
        if env and path:
            raise RigelError("Both mutually excusive fields 'env' and 'path' were declared for a same SSH key")
        if not env and not path:
            raise RigelError("SSH key found with neither field 'env' nor 'path' declared")
        return values


class SSHProviderModel(BaseModel, extra=Extra.forbid):

    # Required fields
    keys: List[SSHKeyGroup]


#
# OUTPUT MODELS
#

class SSHKeyGroup(BaseModel, extra=Extra.forbid):

    # Required fields
    hostname: str
    env: Optional[str] = None
    path: Optional[str] = None

    @root_validator
    def check_mutually_exclusive_fields(cls, values):
        env = values.get('env')
        path = values.get('path')
        if env and path:
            raise RigelError("Both mutually excusive fields 'env' and 'path' were declared for a same SSH key")
        if not env and not path:
            raise RigelError("SSH key found with neither field 'env' nor 'path' declared")
        return values


class SSHProviderOutputModel(SSHProviderModel):
    pass  # inherit all the the same fields
