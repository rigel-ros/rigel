import os
from pydantic import (
    BaseModel
)

RIGEL_FOLDER = f"{os.environ.get('HOME', '')}/.rigel"


class WorkspaceSettings(BaseModel):
    root: str = f'{RIGEL_FOLDER}/workspaces'


# TODO:
# - add mechanism to ensure that values are valid
# - consider using BaseSettings and support substitutions based on environment variables.
class Settings(BaseModel):

    workspaces: WorkspaceSettings = WorkspaceSettings()

    def __str__(self) -> str:
        return f"""workspaces.root = {self.workspaces.root}"""
