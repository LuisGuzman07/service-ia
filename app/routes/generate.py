from fastapi import APIRouter

from app.models.flow_models import GenerateFlowRequest, GenerateFlowResponse
from app.services.factory import get_generator


router = APIRouter(prefix="/api/v1/ai", tags=["AI Flow Generation"])


@router.post("/generate-flow", response_model=GenerateFlowResponse)
def generate_flow(request: GenerateFlowRequest) -> GenerateFlowResponse:
    generator = get_generator()
    draft, summary = generator.generate_flow(request)
    return GenerateFlowResponse(
        draft=draft,
        summary=summary,
        model=generator.model_name
    )

