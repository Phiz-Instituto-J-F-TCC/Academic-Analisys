"""
Guardrail de Entrada — Validação de Tópico.

Este módulo implementa um guardrail que valida se a mensagem do usuário
está relacionada a meteorologia/climatologia antes de permitir que ela
seja processada pelo pipeline de agentes.

Conceito:
    - Um agente auxiliar (guardrail_agent) classifica a mensagem.
    - A função de guardrail interpreta a classificação.
    - Se o tópico NÃO for meteorológico, o tripwire é acionado e a
      execução é interrompida com InputGuardrailTripwireTriggered.
"""

from pathlib import Path

from pydantic import BaseModel

from agents import Agent, GuardrailFunctionOutput, InputGuardrail, Runner

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# ---------------------------------------------------------------------------
# Modelo de saída estruturada para o agente guardrail
# ---------------------------------------------------------------------------
class GuardrailOutput(BaseModel):
    """Resultado da classificação do guardrail."""
    is_meteorology: bool
    reasoning: str


# ---------------------------------------------------------------------------
# Agente Guardrail — classifica a mensagem do usuário
# ---------------------------------------------------------------------------
guardrail_agent = Agent(
    name="Guardrail",
    instructions=(PROMPTS_DIR / "Guardrail.md").read_text(encoding="utf-8"),
    output_type=GuardrailOutput,
    model="gpt-5-nano",  # Modelo leve para classificação rápida
)


# ---------------------------------------------------------------------------
# Função de guardrail — executada automaticamente pelo SDK
# ---------------------------------------------------------------------------
async def _meteorology_guardrail_fn(ctx, agent, input) -> GuardrailFunctionOutput:
    """
    Função de guardrail que executa o agente classificador e retorna
    se o tripwire deve ser acionado.

    Args:
        ctx: Contexto de execução do SDK.
        agent: Instância do agente sendo protegido.
        input: Entrada do usuário (string ou lista de mensagens).

    Returns:
        GuardrailFunctionOutput com tripwire_triggered=True se o tópico
        não for meteorológico.
    """
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    output: GuardrailOutput = result.final_output

    return GuardrailFunctionOutput(
        output_info={
            "is_meteorology": output.is_meteorology,
            "reasoning": output.reasoning,
        },
        tripwire_triggered=not output.is_meteorology,
    )


# ---------------------------------------------------------------------------
# InputGuardrail pronto para ser anexado a qualquer agente
# ---------------------------------------------------------------------------
meteorology_guardrail = InputGuardrail(
    guardrail_function=_meteorology_guardrail_fn,
)
