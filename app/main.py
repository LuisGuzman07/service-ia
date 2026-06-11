from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routes.generate import router as generate_router
from app.routes.generate_form import router as generate_form_router
from app.routes.generate_all_forms import router as generate_all_forms_router


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Microservicio de IA para generar flujos de actividades y formularios."
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    # Log to server console
    print("--- Request Validation Error ---")
    print(f"URL: {request.url}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Body: {body}")
    print(f"Errors: {exc.errors()}")
    print("--------------------------------")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "received_body": body.decode(errors='ignore')
        }
    )

app.include_router(generate_router)
app.include_router(generate_form_router)
app.include_router(generate_all_forms_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}

