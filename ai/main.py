"""
Chatbot Multi-Agente de Acompanhamento Acadêmico
================================================

Ponto de entrada principal e lógica do pipeline multi-agente.

Arquitetura Multi-Agente:
─────────────────────────
1. GUARDRAIL     → Valida se a pergunta é sobre o contexto acadêmico
2. ROTEADOR      → Decide qual especialista deve responder
3. ESPECIALISTA  → Responde usando ferramentas (tools) específicas
    ├─ Aluno (notas e frequência)
    ├─ Professor (relatórios acadêmicos)
    └─ Coordenador (visões gerais acadêmicas)
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
import re
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
    academic_guardrail,
    orchestrator_agent,
    router_agent,
    small_talk_specialist,
)
from src.agents.persona import PERSONA_PROMPT


# ═══════════════════════════════════════════════════════════════════════════
# UTILITÁRIO: remove markdown da resposta final
# ═══════════════════════════════════════════════════════════════════════════

def strip_markdown(text: str) -> str:
    """Remove marcações markdown comuns da string, retornando texto puro."""
    # Blocos de código (```...```)
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Código inline (`...`)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    # Cabeçalhos (# ## ###)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Negrito e itálico (*** ** * ___  __ _)
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    # Linha horizontal (--- *** ___)
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Links [texto](url) → texto
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    # Imagens ![alt](url) → ''
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    # Linhas em branco extras (>2 seguidas)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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

    # ── Etapa 1: Pipeline principal (Guardrail → Roteador → Especialista → Orquestrador) ──
    try:
        print("   🔒 Guardrail verificando a mensagem...")
        print("   🔀 Roteando a intenção do usuário...")

        # Constrói o histórico da conversa com mensagens passadas ANTES de persistir a mensagem atual
        memory_text = ""
        try:
            if DB_CONN:
                memory_text = build_memory_context(DB_CONN, user_id, limit=30)
        except Exception:
            memory_text = ""

        # Persist the current user message (best-effort)
        try:
            if DB_CONN:
                persist_message(DB_CONN, session_id, "user", user_input)
        except Exception:
            pass

        router_context = (
            f"O numero_phiz do usuário atual é: {user_id}\n\n"
            "Dê alta relevância ao histórico de mensagens anteriores fornecido no input.\n"
            "Use a única fonte de verdade de persona abaixo para decidir se deve encaminhar a solicitação a um especialista.\n"
            "Se a mensagem for small talk ou sobre identidade do assistente, encaminhe para o especialista de small talk.\n"
            "Caso contrário, faça handoff para o especialista adequado com base no tipo de usuário e na intenção expressa.\n\n"
            f"PERSONA:\n{PERSONA_PROMPT}"
        )

        router_message = f"IDENTIFICADOR DO USUÁRIO AUTENTICADO (numero_phiz): {user_id}\n\n"
        if memory_text:
            router_message += (
                "═══════════════════════════════════════════════════════════════════\n"
                "HISTÓRICO DE MENSAGENS ANTERIORES DA CONVERSA:\n"
                "Dê alta relevância e prioridade ao histórico abaixo. Use-o ativamente para entender o contexto, referências a matérias ou dados citados, pronomes, anáforas e perguntas contínuas (como 'quantas matérias eu preciso melhorar?', 'e em frequência?', 'qual foi minha pior nota?').\n"
                "═══════════════════════════════════════════════════════════════════\n"
                f"{memory_text}\n"
                "═══════════════════════════════════════════════════════════════════\n\n"
            )
        router_message += (
            "PERGUNTA ATUAL DO USUÁRIO:\n"
            f"{user_input}"
        )

        specialist_result = await Runner.run(router_agent, router_message, context=router_context)
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
            result["final_response"] = strip_markdown(specialist_output)
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

        print("   ⚙️ Especialista utilizado:", result["specialist_used"])
        print("   🧩 Orquestrador humanizando a resposta do especialista...")

        orchestrator_input = (
            f"IDENTIFICADOR DO USUÁRIO: {user_id}\n\n"
        )
        if memory_text:
            orchestrator_input += (
                "═══════════════════════════════════════════════════════════════════\n"
                "HISTÓRICO RECENTE DE MENSAGENS DA CONVERSA:\n"
                f"{memory_text}\n"
                "═══════════════════════════════════════════════════════════════════\n\n"
            )
        orchestrator_input += (
            "DIRETRIZES DO ORQUESTRADOR:\n"
            "- Dê alta relevância ao histórico da conversa acima para manter total coerência, responder follow-ups com fluidez e conectar a resposta atual ao que já foi discutido.\n"
            "- Se a pergunta for sobre quantidade (ex.: 'quantas matérias preciso melhorar?', 'quantos alunos?'), responda com o número exato em destaque logo no início de maneira clara e objetiva.\n"
            "- Use a persona consistente abaixo para humanizar a resposta técnica do especialista em português brasileiro acolhedor, claro e acessível.\n"
            "- Jamais revele nomes ou detalhes de arquitetura de agentes, nem tools internas do sistema.\n"
            "- Preserve os limites de segurança da persona: não preveja aprovação/reprovação nem emita julgamentos institucionais.\n\n"
            f"PERSONA:\n{PERSONA_PROMPT}\n\n"
            "PERGUNTA ATUAL DO USUÁRIO:\n"
            f"{user_input}\n\n"
            "O texto abaixo é o resultado técnico gerado pelo especialista.\n"
            f"RESPOSTA DO ESPECIALISTA:\n{specialist_output}"
        )

        orchestrator_result = await Runner.run(orchestrator_agent, orchestrator_input)
        result["final_response"] = strip_markdown(orchestrator_result.final_output)

        # Persist humanized assistant output
        try:
            if DB_CONN:
                persist_message(DB_CONN, session_id, "assistant", result["final_response"])
        except Exception:
            pass

    except InputGuardrailTripwireTriggered:
        result["error"] = (
            "⚠️  Desculpe, este chatbot é especializado em acompanhamento acadêmico.\n"
            "   Faça perguntas sobre notas, desempenho, frequência, avaliações,\n"
            "   quantidades de matérias ou alunos, e relatórios acadêmicos.\n\n"
            "   Exemplos:\n"
            '   • "Quais são minhas notas e minha média por matéria?"\n'
            '   • "Quantas matérias eu preciso melhorar?"\n'
            '   • "Quantos alunos eu possuo na turma?"\n'
            '   • "Qual é minha porcentagem de frequência?"\n'
            '   • "Como está o desempenho de um aluno em uma matéria?"'
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

async def ai_response(user_id: str, user_input:str):
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
        return result["error"]
    else:
        agent_name = result.get("agent_used", "Especialista")
        print(f"🤖 [{agent_name}]:")
        final_response = result["final_response"]
        print(final_response)


        if result.get("evaluation"):
            judge_evaluation = result["evaluation"]

            if judge_evaluation["approved"]:
                return final_response

            return final_response

        elif result.get("judge_error"):
            print(f"\n  ⚠️  Juiz indisponível: {result['judge_error']}")
            return final_response

        # Fallback para casos como small_talk que não tem avaliação
        return final_response


if __name__ == "__main__":
    uid = "+5511972721701"
    if not uid:
        print("❌ Erro: ID de usuário não pode ser vazio.")
        sys.exit(1)
    asyncio.run(ai_response(uid, "Melhor nota da turma"))
