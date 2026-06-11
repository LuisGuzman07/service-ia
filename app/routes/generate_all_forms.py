from fastapi import APIRouter

from app.models.form_models import GenerateAllFormsRequest, GenerateFormResponse
from app.services.factory import get_generator


router = APIRouter(prefix="/api/v1/ai", tags=["AI Bulk Form Generation"])


@router.post("/generate-all-forms", response_model=dict[str, GenerateFormResponse])
def generate_all_forms(request: GenerateAllFormsRequest) -> dict[str, GenerateFormResponse]:
    generator = get_generator()
    return generator.generate_all_forms(request)

