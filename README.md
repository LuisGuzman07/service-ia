# IA Service

Microservicio `FastAPI` para generar borradores de flujo desde lenguaje natural.

## Requisitos

- Python 3.11+
- API key de Gemini

## Configuración

1. Copia `.env.example` a `.env`
2. Define `GEMINI_API_KEY`

## Instalación

```powershell
cd C:\SW1\Workflow\ia-service
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecutar

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## Endpoint principal

- `POST /api/v1/ai/generate-flow`

## Ejemplo de request

```json
{
  "policy_name": "Solicitud de licencia",
  "description": "El usuario presenta una solicitud, recepcion valida documentos, evaluacion revisa requisitos y aprobacion decide si procede.",
  "areas": [
    { "id": "recepcion", "title": "Recepcion" },
    { "id": "evaluacion", "title": "Evaluacion" },
    { "id": "aprobacion", "title": "Aprobacion" }
  ]
}
```

