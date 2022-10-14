import os
from pydantic import BaseModel

RIGEL_FOLDER = f"{os.environ.get('HOME', '')}/.rigel"


class DockerSettings(BaseModel):
    base: str = 'ros-s6'


class WorkspaceSettings(BaseModel):
    file: str = '.rigel_workspace'
    root: str = f'{RIGEL_FOLDER}/workspaces'


# TODO:
# - add mechanism to ensure that values are valid
# - consider using BaseSettings and support substitutions based on environment variables.
class Settings(BaseModel):

    docker: DockerSettings = DockerSettings()
    workspaces: WorkspaceSettings = WorkspaceSettings()

    def __str__(self) -> str:
        return f"""
        docker.base = {self.docker.base}
        workspaces.file = {self.workspaces.file}
        workspaces.root = {self.workspaces.root}
        """
