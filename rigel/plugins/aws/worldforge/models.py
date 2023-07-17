from pydantic import BaseModel, Extra


class PluginModel(BaseModel, extra=Extra.forbid):

    # Required fields
    iam_role: str
    template_arn: str
    s3_bucket: str
    destination: str

    # Optional fields.
    floor_plan_count: int = 1
    interior_count: int = 1
