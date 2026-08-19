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

from src.tools.aluno_tools import (
    consultar_notas_aluno,
    consultar_presenca_aluno
)

from src.tools.professor_tools import (
    relatorio_materia_professor,
    relatorio_aluno_professor
)

from src.tools.coordenador_tools import (
    relatorio_materia_coordenador,
    relatorio_aluno_coordenador,
    visao_geral_sala_coordenador,
    visao_geral_aluno_coordenador
)


# ---------------------------------------------------------------------------
# Especialista 0: Small Talk / Identidade
# ---------------------------------------------------------------------------
small_talk_specialist = Agent(
    name="Especialista_Small_Talk",
    instructions=(PROMPTS_DIR / "Especialista_Small_Talk.md").read_text(encoding="utf-8"),
    model="gpt-5.1",
)


# ---------------------------------------------------------------------------
# Especialista 1: Aluno
# ---------------------------------------------------------------------------
aluno_specialist = Agent(
    name="Especialista_Aluno",
    instructions=(PROMPTS_DIR / "Especialista_Aluno.md").read_text(encoding="utf-8"),
    tools=[consultar_notas_aluno, consultar_presenca_aluno],
    model="gpt-5.4",
)


# ---------------------------------------------------------------------------
# Especialista 2: Professor
# ---------------------------------------------------------------------------
professor_specialist = Agent(
    name="Especialista_Professor",
    instructions=(PROMPTS_DIR / "Especialista_Professor.md").read_text(encoding="utf-8"),
    tools=[relatorio_materia_professor, relatorio_aluno_professor],
    model="gpt-5.4",
)


# ---------------------------------------------------------------------------
# Especialista 3: Coordenador
# ---------------------------------------------------------------------------
coordenador_specialist = Agent(
    name="Especialista_Coordenador",
    instructions=(PROMPTS_DIR / "Especialista_Coordenador.md").read_text(encoding="utf-8"),
    tools=[relatorio_materia_coordenador, relatorio_aluno_coordenador, visao_geral_sala_coordenador, visao_geral_aluno_coordenador],
    model="gpt-5.4",
)
