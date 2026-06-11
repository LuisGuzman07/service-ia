import json

from fastapi import HTTPException
from google import genai

from app.core.config import settings
from app.models.flow_models import GenerateFlowRequest, SwimlaneDiagramState
from app.models.form_models import GenerateFormRequest, GenerateFormResponse, GenerateAllFormsRequest


PROMPT_ALL_FORMS_TEMPLATE = """
Eres un asistente experto en diseño de interfaces de usuario y diseño de formularios para flujos de trabajo en sistemas BPM.

Tu tarea es generar la configuración de formularios en formato JSON válido para múltiples actividades (tareas) de una política de negocio específica.

Detalles de la Política/Proceso:
- Nombre de la Política: {policy_name}
- Descripción del Proceso: {policy_description}

Actividades a las que debes diseñar un formulario (Lista de Tareas):
{tasks}

Reglas para la respuesta:
- Responde ÚNICAMENTE con un objeto JSON válido.
- Usa exactamente la siguiente estructura raíz, donde las claves son exactamente los identificadores de cada actividad provistos en la lista (ej: "node_1", "node_2", etc.):
  {{
    "node_id_de_actividad_1": {{
      "formName": "Formulario [Título descriptivo para la actividad]",
      "fields": [
        {{
          "id": "campo_1",
          "type": "text|textarea|number|date|select|radio|checkbox|file|email|phone|matrix",
          "label": "Etiqueta visible del campo",
          "placeholder": "Texto de ayuda/ejemplo",
          "required": true|false,
          "options": ["opcion1", "opcion2"], // Solo si type es select, radio o checkbox. Omitir si no aplica.
          "matrixRows": ["fila1", "fila2"], // Solo si type es matrix. Omitir si no aplica.
          "matrixColumns": ["columna1", "columna2"] // Solo si type es matrix. Omitir si no aplica.
        }}
      ]
    }},
    "node_id_de_actividad_2": {{
      ...
    }}
  }}
- El campo "type" debe ser exactamente uno de los siguientes: "text", "textarea", "number", "date", "select", "radio", "checkbox", "file", "email", "phone", "matrix". No uses otros tipos.
- Diseña campos lógicos, coherentes y específicos para lo que se requiere registrar en cada actividad en base a su nombre y el área (laneTitle) donde se ejecuta.
- Asegúrate de que cada campo tenga un "id" único.
- No uses placeholders o comentarios dentro del JSON devuelto.
- No agregues texto explicativo ni formato de bloques de código markdown aparte del JSON.
""".strip()


PROMPT_FORM_TEMPLATE = """
Eres un asistente experto en diseño de interfaces de usuario y diseño de formularios para flujos de trabajo en sistemas BPM.

Tu tarea es generar la configuración de un formulario en formato JSON válido para un nodo específico dentro de un proceso.

Detalles de la Tarea/Nodo:
- Identificador del Nodo: {node_id}
- Nombre del Nodo: {node_label}
- Tipo de Nodo: {node_type}
- Área/Carril que participa: {lane_title}

Detalles de la Política/Proceso:
- Nombre de la Política: {policy_name}
- Descripción del Proceso: {policy_description}

Reglas para la respuesta:
- Responde ÚNICAMENTE con un objeto JSON válido.
- Usa exactamente la siguiente estructura raíz:
  {{
    "formName": "Formulario [Título descriptivo según el nodo]",
    "fields": [
      {{
        "id": "campo_1",
        "type": "text|textarea|number|date|select|radio|checkbox|file|email|phone|matrix",
        "label": "Etiqueta visible del campo",
        "placeholder": "Texto de ayuda/ejemplo",
        "required": true|false,
        "options": ["opcion1", "opcion2"], // Solo si type es select, radio o checkbox. Omitir si no aplica.
        "matrixRows": ["fila1", "fila2"], // Solo si type es matrix. Omitir si no aplica.
        "matrixColumns": ["columna1", "columna2"] // Solo si type es matrix. Omitir si no aplica.
      }}
    ]
  }}
- El campo "type" debe ser exactamente uno de los siguientes: "text", "textarea", "number", "date", "select", "radio", "checkbox", "file", "email", "phone", "matrix". No uses otros tipos.
- Diseña campos lógicos, coherentes y específicos para lo que se requiere registrar en esta etapa del proceso.
- Asegúrate de que cada campo tenga un "id" único.
- No uses placeholders o comentarios dentro del JSON devuelto.
- No agregues texto explicativo ni formato de bloques de código markdown aparte del JSON.
""".strip()


PROMPT_TEMPLATE = """
Eres un asistente experto en modelado de procesos y diagramas de actividades UML 2.5.

Tu tarea es generar un borrador de flujo en JSON valido para un editor swimlane.

Reglas:
- Responde SOLO con JSON valido.
- Usa exactamente esta estructura raiz:
  {{
    "lanes": [{{ "id": "string", "title": "string" }}],
    "nodes": [
      {{
        "id": "node_1",
        "type": "start|end|task|gateway|event|fork|join",
        "laneId": "string",
        "row": 1,
        "label": "string",
        "subLabel": "string opcional"
      }}
    ],
    "flows": [
      {{
        "id": "flow_1",
        "from": "node_x",
        "to": "node_y",
        "label": "string opcional"
      }}
    ]
  }}
- Debe existir al menos un nodo de inicio y uno de fin.
- Usa preferentemente type "task" para actividades.
- Usa "gateway" para decisiones.
- Los laneId deben existir en lanes.
- Los flows deben conectar ids de nodos existentes.
- Si el usuario proporciona areas disponibles:
  1. Utiliza **exactamente** el valor del "id" provisto en el listado para el campo "id" en "lanes" y "laneId" en "nodes". No inventes IDs simplificados (como "recepcion") si el área tiene un ID específico.
  2. Incluye en "lanes" **únicamente** las áreas que tengan al menos un nodo asignado (que participen activamente). No agregues carriles vacíos en la respuesta.
- Si faltan areas, puedes inferir carriles razonables con IDs descriptivos y sencillos.
- No agregues campos extra.

Nombre de la politica:
{policy_name}

Areas disponibles:
{areas}

Descripcion del proceso:
{description}
""".strip()


class GeminiFlowGenerator:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY no configurada en ia-service")
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def generate_flow(self, request: GenerateFlowRequest) -> tuple[SwimlaneDiagramState, str]:
        prompt = PROMPT_TEMPLATE.format(
            policy_name=request.policy_name,
            description=request.description,
            areas=json.dumps([area.model_dump() for area in request.areas], ensure_ascii=False),
        )

        try:
            response = self.client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Error consultando Gemini: {exc}") from exc

        raw_text = (response.text or "").strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            raw_text = raw_text.replace("json", "", 1).strip()

        try:
            payload = json.loads(raw_text)
            draft = SwimlaneDiagramState.model_validate(payload)
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Gemini devolvio una respuesta no valida para el diagrama: {exc}"
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
            response = self.client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Error consultando Gemini: {exc}") from exc

        raw_text = (response.text or "").strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            raw_text = raw_text.replace("json", "", 1).strip()

        try:
            payload = json.loads(raw_text)
            form_res = GenerateFormResponse.model_validate(payload)
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Gemini devolvio una respuesta no valida para el formulario: {exc}. Contenido: {raw_text}"
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
            response = self.client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Error consultando Gemini en lote: {exc}") from exc

        raw_text = (response.text or "").strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            raw_text = raw_text.replace("json", "", 1).strip()

        try:
            payload = json.loads(raw_text)
            results = {}
            for k, v in payload.items():
                results[k] = GenerateFormResponse.model_validate(v)
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Gemini devolvio una respuesta no valida para la generacion masiva: {exc}. Contenido: {raw_text}"
            ) from exc

        return results
