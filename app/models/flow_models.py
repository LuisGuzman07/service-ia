from typing import Literal

from pydantic import AliasChoices, BaseModel, Field


DiagramNodeType = Literal["task", "gateway", "event", "start", "end", "fork", "join"]


class AreaInput(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)


class DiagramLane(BaseModel):
    id: str
    title: str


class DiagramNode(BaseModel):
    id: str
    type: DiagramNodeType
    laneId: str
    row: int = 1
    label: str
    subLabel: str | None = None
    x: float | None = None
    y: float | None = None
    width: float | None = None
    height: float | None = None


class DiagramFlow(BaseModel):
    id: str
    from_: str = Field(alias="from")
    to: str
    label: str | None = None

    model_config = {"populate_by_name": True}


class SwimlaneDiagramState(BaseModel):
    lanes: list[DiagramLane]
    nodes: list[DiagramNode]
    flows: list[DiagramFlow]


class GenerateFlowRequest(BaseModel):
    policy_name: str = Field(
        min_length=3,
        max_length=150,
        validation_alias=AliasChoices("policy_name", "policyName"),
    )
    description: str = Field(min_length=10, max_length=4000)
    areas: list[AreaInput] = Field(default_factory=list)


class GenerateFlowResponse(BaseModel):
    draft: SwimlaneDiagramState
    summary: str
    model: str
