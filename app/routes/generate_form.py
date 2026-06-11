from fastapi import APIRouter

from app.models.form_models import GenerateFormRequest, GenerateFormResponse
from app.services.gemini_service import GeminiFlowGenerator


router = APIRouter(prefix="/api/v1/ai", tags=["AI Form Generation"])


@router.post("/generate-form", response_model=GenerateFormResponse)
def generate_form(request: GenerateFormRequest) -> GenerateFormResponse:
    generator = GeminiFlowGenerator()
    return generator.generate_form(request)
