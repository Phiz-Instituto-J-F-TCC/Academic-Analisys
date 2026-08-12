"""
Agente Orquestrador — Humanização da resposta do especialista.

Este módulo define o orquestrador que recebe a resposta do especialista
(eventualmente estruturada ou gerada por ferramentas) e produz uma
resposta final em linguagem natural para o usuário e para que o juiz avalie.
"""

from pathlib import Path

from agents import Agent

from src.agents.persona import PERSONA_PROMPT

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# ---------------------------------------------------------------------------
# Agente Orquestrador — transforma saída técnica em resposta humanizada
# ---------------------------------------------------------------------------
orchestrator_agent = Agent(
    name="Orquestrador de Resposta",
    instructions=(PROMPTS_DIR / "orchestrator.txt").read_text(encoding="utf-8"),
    model="gpt-4o-mini",
)

ORCHESTRATOR_PERSONA_PROMPT = PERSONA_PROMPT
