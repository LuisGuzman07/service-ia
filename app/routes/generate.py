from fastapi import APIRouter

from app.core.config import settings
from app.models.flow_models import GenerateFlowRequest, GenerateFlowResponse
from app.services.gemini_service import GeminiFlowGenerator


router = APIRouter(prefix="/api/v1/ai", tags=["AI Flow Generation"])


@router.post("/generate-flow", response_model=GenerateFlowResponse)
def generate_flow(request: GenerateFlowRequest) -> GenerateFlowResponse:
    generator = GeminiFlowGenerator()
    draft, summary = generator.generate_flow(request)
    return GenerateFlowResponse(
        draft=draft,
        summary=summary,
        model=settings.gemini_model
    )
