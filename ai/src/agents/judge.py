"""
Agente Juiz — Avaliação de Qualidade de Respostas.

O juiz recebe a pergunta original do usuário e a resposta do especialista,
avaliando a qualidade em múltiplos critérios:
  - Precisão dos dados
  - Completude da resposta
  - Clareza da comunicação

Retorna uma avaliação estruturada com nota, feedback e aprovação.
"""

from pathlib import Path

from pydantic import BaseModel, Field

from agents import Agent

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# ---------------------------------------------------------------------------
# Modelo de saída estruturada para a avaliação do juiz
# ---------------------------------------------------------------------------
class JudgeEvaluation(BaseModel):
    """Resultado estruturado da avaliação do juiz."""

    score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Nota geral de 1 a 10 para a resposta.",
    )
    accuracy: str = Field(
        ...,
        description="Avaliação da precisão e consistência dos dados apresentados.",
    )
    completeness: str = Field(
        ...,
        description="Avaliação de quão completa é a resposta em relação à pergunta.",
    )
    clarity: str = Field(
        ...,
        description="Avaliação da clareza e acessibilidade da linguagem utilizada.",
    )
    suggestions: str = Field(
        ...,
        description="Sugestões construtivas para melhorar a resposta, se houver.",
    )
    approved: bool = Field(
        ...,
        description="True se a resposta atinge o padrão mínimo de qualidade (score >= 7).",
    )


# ---------------------------------------------------------------------------
# Agente Juiz — avalia a qualidade da resposta do especialista
# ---------------------------------------------------------------------------
judge_agent = Agent(
    name="Juiz de Qualidade",
    instructions=(PROMPTS_DIR / "Juiz.md").read_text(encoding="utf-8"),
    output_type=JudgeEvaluation,
    model="gpt-5.4",
)
