from pydantic import AliasChoices, BaseModel, Field


class GenerateFormRequest(BaseModel):
    node_id: str = Field(alias=AliasChoices("node_id", "nodeId"))
    node_label: str = Field(alias=AliasChoices("node_label", "nodeLabel"))
    node_type: str = Field(alias=AliasChoices("node_type", "nodeType"))
    lane_title: str = Field(alias=AliasChoices("lane_title", "laneTitle"))
    policy_name: str = Field(alias=AliasChoices("policy_name", "policyName"))
    policy_description: str = Field(alias=AliasChoices("policy_description", "policyDescription"), default="")

    model_config = {"populate_by_name": True}


class FormField(BaseModel):
    id: str
    type: str
    label: str
    placeholder: str | None = None
    required: bool = False
    options: list[str] | None = None
    matrixRows: list[str] | None = None
    matrixColumns: list[str] | None = None


class GenerateFormResponse(BaseModel):
    formName: str = Field(alias=AliasChoices("formName", "form_name"))
    fields: list[FormField]

    model_config = {"populate_by_name": True}


class TaskInput(BaseModel):
    id: str
    label: str
    laneTitle: str = Field(alias=AliasChoices("laneTitle", "lane_title"))

    model_config = {"populate_by_name": True}


class GenerateAllFormsRequest(BaseModel):
    policyName: str = Field(alias=AliasChoices("policyName", "policy_name"))
    policyDescription: str = Field(alias=AliasChoices("policyDescription", "policy_description"), default="")
    tasks: list[TaskInput]

    model_config = {"populate_by_name": True}
