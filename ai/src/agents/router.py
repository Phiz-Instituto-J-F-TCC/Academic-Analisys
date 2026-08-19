"""
Agente Roteador — Decisão de Encaminhamento.

O roteador analisa a intenção do usuário e decide qual especialista
é mais adequado para responder, usando o mecanismo de handoff do SDK.

Fluxo:
    Mensagem do Usuário → Roteador → Handoff → Especialista adequado
"""

from pathlib import Path

from agents import Agent

from src.agents.guardrail import meteorology_guardrail
from src.agents.persona import PERSONA_PROMPT
from src.agents.specialists import aluno_specialist, professor_specialist, coordenador_specialist,small_talk_specialist
from src.tools.geral_tools import verificar_tipo_usuario

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# ---------------------------------------------------------------------------
# Agente Roteador — direciona para o especialista correto ou responde small talk
# ---------------------------------------------------------------------------
router_agent = Agent(
    name="Roteador",
    instructions=(PROMPTS_DIR / "Roteador.md").read_text(encoding="utf-8"),
    handoffs=[small_talk_specialist,aluno_specialist, professor_specialist, coordenador_specialist],
    tools=[verificar_tipo_usuario],
    input_guardrails=[meteorology_guardrail],
    model="gpt-5-nano",
)

ROUTER_PERSONA_PROMPT = PERSONA_PROMPT

