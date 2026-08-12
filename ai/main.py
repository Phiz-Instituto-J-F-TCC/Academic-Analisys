"""
🌤️ Chatbot Multi-Agente de Meteorologia
=========================================

Ponto de entrada principal e lógica do pipeline multi-agente.

Arquitetura Multi-Agente:
─────────────────────────
1. GUARDRAIL     → Valida se a pergunta é sobre meteorologia
2. ROTEADOR      → Decide qual especialista deve responder
3. ESPECIALISTA  → Responde usando ferramentas (tools) específicas
   ├─ Previsão do Tempo (3 tools)
   └─ Análise Climática (3 tools)
4. ORQUESTRADOR  → Humaniza a saída técnica do especialista
5. JUIZ          → Avalia a qualidade da resposta humanizada

Fluxo:
    Usuário → [Guardrail] → Roteador → Especialista → Orquestrador → [Juiz] → Resposta

Uso:
    1. Copie .env.example para .env e adicione sua chave OPENAI_API_KEY
    2. pip install -r requirements.txt
    3. python main.py
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROMPTS_DIR = Path(__file__).parent / "src" / "prompts"

# Carrega variáveis de ambiente do .env
load_dotenv()

# SQLite memory helpers
from src.memory.sqlite_memory import (
    init_db,
    get_or_create_user,
    create_session,
    persist_message,
    build_memory_context,
)

# Global DB connection (initialized in main)
DB_CONN = None

# Valida que a chave da API foi configurada
if not os.getenv("OPENAI_API_KEY"):
    print("❌ Erro: OPENAI_API_KEY não encontrada!")
    print("   Crie um arquivo .env com: OPENAI_API_KEY=sk-sua-chave-aqui")
    print("   Ou copie o .env.example: copy .env.example .env")
    sys.exit(1)

from agents import Agent, InputGuardrailTripwireTriggered, Runner

from src.agents import (
    judge_agent,
    meteorology_guardrail,
    orchestrator_agent,
    router_agent,
    small_talk_specialist,
)
from src.agents.persona import PERSONA_PROMPT


# ═══════════════════════════════════════════════════════════════════════════
# OBSERVAÇÃO: O orquestrador recebe a saída técnica do especialista e a humaniza.
# ═══════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE PROCESSAMENTO
# ═══════════════════════════════════════════════════════════════════════════

async def process_query(user_input: str, session_id: str, user_id: str) -> dict:
    """
    Processa uma pergunta do usuário através do pipeline multi-agente completo.

    Pipeline:
        1. Guardrail → Roteador → Especialista → Orquestrador
        2. Juiz avalia a resposta humanizada

    Args:
        user_input: Pergunta do usuário em texto livre.

    Returns:
        Dicionário com a resposta do especialista, avaliação do juiz,
        e metadados sobre qual agente respondeu.
    """
    result = {}

    # Persist the user message (best-effort)
    try:
        if DB_CONN:
            persist_message(DB_CONN, session_id, "user", user_input)
    except Exception:
        pass

    # ── Etapa 1: Pipeline principal (Guardrail → Roteador → Especialista → Orquestrador) ──
    try:
        print("   🔒 Guardrail verificando a mensagem...")
        print("   🔀 Roteando a intenção do usuário...")

        # Build a short memory context (recent messages) and inject into prompts
        memory_text = ""
        try:
            if DB_CONN:
                memory_text = build_memory_context(DB_CONN, user_id, limit=6)
        except Exception:
            memory_text = ""

        router_input = (
            (f"MEMORY:\n{memory_text}\n\n") if memory_text else ""
            + "Use a única fonte de verdade de persona abaixo para decidir se deve encaminhar a solicitação a um especialista.\n"
            "Se a mensagem for small talk ou sobre identidade do assistente, encaminhe para o especialista de small talk.\n"
            "Caso contrário, faça handoff para o especialista adequado.\n\n"
            f"PERSONA:\n{PERSONA_PROMPT}"
        )

        specialist_result = await Runner.run(router_agent, user_input, context=router_input)
        specialist_output = specialist_result.final_output
        result["agent_used"] = specialist_result.last_agent.name

        # Persist specialist raw output (best-effort)
        try:
            if DB_CONN:
                persist_message(DB_CONN, session_id, "specialist", specialist_output)
        except Exception:
            pass

        if specialist_result.last_agent is small_talk_specialist:
            # O especialista de small talk respondeu diretamente.
            print("   🧠 Small talk atendida diretamente pelo especialista de small talk.")
            result["final_response"] = specialist_output
            result["specialist_response"] = specialist_output
            result["specialist_used"] = small_talk_specialist.name
            result["evaluation"] = None

            # Persist assistant reply
            try:
                if DB_CONN:
                    persist_message(DB_CONN, session_id, "assistant", specialist_output)
            except Exception:
                pass

            return result

        result["specialist_used"] = specialist_result.last_agent.name
        result["specialist_response"] = specialist_output

        print("   🧩 Orquestrador humanizando a resposta do especialista...")

        orchestrator_input = (
            (f"MEMORY:\n{memory_text}\n\n") if memory_text else ""
            + "Use a persona consistente com o roteador para humanizar a resposta técnica do especialista.\n"
            f"PERSONA:\n{PERSONA_PROMPT}\n\n"
            "PERGUNTA DO USUÁRIO:\n"
            f"{user_input}\n\n"
            "O texto abaixo é o resultado técnico gerado pelo especialista.\n"
            "Sua tarefa é transformá-lo em uma resposta natural em português brasileiro,\n"
            "clara e acessível, adequada para o usuário final e para avaliação do juiz.\n\n"
            f"RESPOSTA DO ESPECIALISTA:\n{specialist_output}"
        )

        orchestrator_result = await Runner.run(orchestrator_agent, orchestrator_input)
        result["final_response"] = orchestrator_result.final_output

        # Persist humanized assistant output
        try:
            if DB_CONN:
                persist_message(DB_CONN, session_id, "assistant", result["final_response"])
        except Exception:
            pass

    except InputGuardrailTripwireTriggered:
        result["error"] = (
            "⚠️  Desculpe, este chatbot é especializado em **meteorologia e clima**.\n"
            "   Faça perguntas sobre previsão do tempo, condições climáticas,\n"
            "   índices climáticos, mudanças climáticas, etc.\n\n"
            "   Exemplos:\n"
            '   • "Como está o tempo em São Paulo?"\n'
            '   • "Qual a previsão para os próximos 5 dias no Rio?"\n'
            '   • "O que é El Niño e como afeta o Brasil?"\n'
            '   • "Compare o clima de Curitiba entre 2000 e 2024"'
        )
        return result

    # ── Etapa 2: Juiz avalia a qualidade da resposta ──
    try:
        print("   ⚖️  Juiz avaliando a qualidade da resposta...")

        judge_input = (
            f"PERGUNTA DO USUÁRIO: {user_input}\n"
            f"─────────────────────────────────────────\n"
            f"RESPOSTA HUMANIZADA: {result['final_response']}"
        )

        judge_response = await Runner.run(judge_agent, judge_input)
        evaluation = judge_response.final_output

        result["evaluation"] = {
            "score": evaluation.score,
            "accuracy": evaluation.accuracy,
            "completeness": evaluation.completeness,
            "clarity": evaluation.clarity,
            "suggestions": evaluation.suggestions,
            "approved": evaluation.approved,
        }

        # Persist evaluation (best-effort)
        try:
            if DB_CONN:
                persist_message(DB_CONN, session_id, "evaluation", str(result["evaluation"]))
        except Exception:
            pass

    except Exception as e:
        # Se o juiz falhar, não impede a entrega da resposta ao usuário
        result["evaluation"] = None
        result["judge_error"] = str(e)

    return result


# ═══════════════════════════════════════════════════════════════════════════
# LOOP PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

async def main(user_id: str, user_input:str):
    """Loop principal do chatbot interativo."""
    global DB_CONN

    # Initialize DB, ensure user exists, and create a session for this run
    try:
        DB_CONN = init_db()
        get_or_create_user(DB_CONN, user_id)
        session_id = create_session(DB_CONN, user_id)
    except Exception:
        DB_CONN = None
        session_id = "default-session"

    result = await process_query(user_input, session_id, user_id)

    if "error" in result:
        print(result["error"])
    else:
        agent_name = result.get("agent_used", "Especialista")
        print(f"🤖 [{agent_name}]:\n")

        final_response = result["final_response"]

        if result.get("evaluation"):
            judge_evaluation = result["evaluation"]

            if judge_evaluation["approved"]:
                return final_response

            return judge_evaluation["suggestions"]

        elif result.get("judge_error"):
            print(f"\n  ⚠️  Juiz indisponível: {result['judge_error']}")
            return final_response


if __name__ == "__main__":
    uid = "gabriel.ferreira"
    if not uid:
        print("❌ Erro: ID de usuário não pode ser vazio.")
        sys.exit(1)
    asyncio.run(main(uid))
