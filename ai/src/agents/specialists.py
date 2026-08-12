"""
Agentes Especialistas — Previsão do Tempo e Análise Climática.

Este módulo define dois agentes especialistas, cada um equipado com
ferramentas (tools) específicas para seu domínio:

1. Especialista em Previsão do Tempo:
   - obter_clima_atual
   - obter_previsao_tempo
   - obter_alertas_meteorologicos

2. Especialista em Análise Climática:
   - obter_historico_climatico
   - obter_indices_climaticos
   - comparar_clima_periodos
"""

from pathlib import Path

from agents import Agent

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

from src.tools.weather_tools import (
    obter_alertas_meteorologicos,
    obter_clima_atual,
    obter_previsao_tempo,
)
from src.tools.climate_tools import (
    comparar_clima_periodos,
    obter_historico_climatico,
    obter_indices_climaticos,
)


# ---------------------------------------------------------------------------
# Especialista 0: Small Talk / Identidade
# ---------------------------------------------------------------------------
small_talk_specialist = Agent(
    name="Especialista_Small_Talk",
    instructions=(PROMPTS_DIR / "small_talk_specialist.txt").read_text(encoding="utf-8"),
    model="gpt-4o-mini",
)


# ---------------------------------------------------------------------------
# Especialista 1: Previsão do Tempo
# ---------------------------------------------------------------------------
forecast_specialist = Agent(
    name="Especialista_Previsao_do_Tempo",
    instructions=(PROMPTS_DIR / "forecast_specialist.txt").read_text(encoding="utf-8"),
    tools=[obter_clima_atual, obter_previsao_tempo, obter_alertas_meteorologicos],
    model="gpt-4o-mini",
)


# ---------------------------------------------------------------------------
# Especialista 2: Análise Climática
# ---------------------------------------------------------------------------
climate_specialist = Agent(
    name="Especialista_Analise_Climatica",
    instructions=(PROMPTS_DIR / "climate_specialist.txt").read_text(encoding="utf-8"),
    tools=[obter_historico_climatico, obter_indices_climaticos, comparar_clima_periodos],
    model="gpt-4o-mini",
)
