import json
from fastapi import HTTPException
from groq import Groq

from app.core.config import settings
from app.models.flow_models import GenerateFlowRequest, SwimlaneDiagramState
from app.models.form_models import GenerateFormRequest, GenerateFormResponse, GenerateAllFormsRequest
from app.services.gemini_service import PROMPT_TEMPLATE, PROMPT_FORM_TEMPLATE, PROMPT_ALL_FORMS_TEMPLATE


class GroqFlowGenerator:
    def __init__(self) -> None:
        if not settings.groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY no configurada en ia-service")
        self.client = Groq(api_key=settings.groq_api_key)
        self.model_name = settings.groq_model

    def generate_flow(self, request: GenerateFlowRequest) -> tuple[SwimlaneDiagramState, str]:
        prompt = PROMPT_TEMPLATE.format(
            policy_name=request.policy_name,
            description=request.description,
            areas=json.dumps([area.model_dump() for area in request.areas], ensure_ascii=False),
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            raw_text = completion.choices[0].message.content
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Error consultando Groq: {exc}") from exc

        raw_text = (raw_text or "").strip()
        try:
            payload = json.loads(raw_text)
            draft = SwimlaneDiagramState.model_validate(payload)
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Groq devolvio una respuesta no valida para el diagrama: {exc}. Contenido: {raw_text}"
            ) from exc

        summary = self._build_summary(draft)
        return draft, summary

    @staticmethod
    def _build_summary(draft: SwimlaneDiagramState) -> str:
        return (
            f"Se generaron {len(draft.lanes)} carriles, "
            f"{len(draft.nodes)} nodos y {len(draft.flows)} transiciones."
        )

    def generate_form(self, request: GenerateFormRequest) -> GenerateFormResponse:
        prompt = PROMPT_FORM_TEMPLATE.format(
            node_id=request.node_id,
            node_label=request.node_label,
            node_type=request.node_type,
            lane_title=request.lane_title,
            policy_name=request.policy_name,
            policy_description=request.policy_description
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            raw_text = completion.choices[0].message.content
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Error consultando Groq: {exc}") from exc

        raw_text = (raw_text or "").strip()
        try:
            payload = json.loads(raw_text)
            form_res = GenerateFormResponse.model_validate(payload)
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Groq devolvio una respuesta no valida para el formulario: {exc}. Contenido: {raw_text}"
            ) from exc

        return form_res

    def generate_all_forms(self, request: GenerateAllFormsRequest) -> dict[str, GenerateFormResponse]:
        tasks_data = []
        for t in request.tasks:
            tasks_data.append({
                "id": t.id,
                "label": t.label,
                "laneTitle": t.laneTitle
            })
        
        prompt = PROMPT_ALL_FORMS_TEMPLATE.format(
            policy_name=request.policyName,
            policy_description=request.policyDescription,
            tasks=json.dumps(tasks_data, ensure_ascii=False, indent=2)
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            raw_text = completion.choices[0].message.content
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Error consultando Groq en lote: {exc}") from exc

        raw_text = (raw_text or "").strip()
        try:
            payload = json.loads(raw_text)
            results = {}
            for k, v in payload.items():
                results[k] = GenerateFormResponse.model_validate(v)
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Groq devolvio una respuesta no valida para la generacion masiva: {exc}. Contenido: {raw_text}"
            ) from exc

        return results
