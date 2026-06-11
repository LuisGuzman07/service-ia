from app.core.config import settings


def get_generator():
    if settings.ai_provider == "groq":
        from app.services.groq_service import GroqFlowGenerator
        return GroqFlowGenerator()
    else:
        from app.services.gemini_service import GeminiFlowGenerator
        return GeminiFlowGenerator()
