"""
Phiz Business API — FastAPI Webhook Server
============================================
Recebe mensagens do Phiz via webhook e responde automaticamente "Funcionou".

Fluxo:
  1. Phiz envia POST /webhook/receiver  (robot:messages)
  2. Servidor valida assinatura HMAC-SHA256
  3. Extrai remetente e envia "Funcionou" de volta via Business API
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query, Request, Response

# ── Configuração ────────────────────────────────────────────
load_dotenv()  # carrega .env se existir

PHIZ_APP_ID = os.getenv("PHIZ_APP_ID", "")
PHIZ_APP_SECRET = os.getenv("PHIZ_APP_SECRET", "")
PHIZ_CHANNEL_ID = os.getenv("PHIZ_CHANNEL_ID", "")
PHIZ_API_BASE = os.getenv("PHIZ_API_BASE", "https://api-test.phiz.live")

VERIFY_TOKEN_STATUSES = os.getenv("VERIFY_TOKEN_STATUSES", "")
VERIFY_TOKEN_MESSAGES = os.getenv("VERIFY_TOKEN_MESSAGES", "")

WEBHOOK_SECRET_STATUSES = os.getenv("WEBHOOK_SECRET_STATUSES", "")
WEBHOOK_SECRET_MESSAGES = os.getenv("WEBHOOK_SECRET_MESSAGES", "")

# ── Logging ─────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger("phiz_webhook")


# ═══════════════════════════════════════════════════════════
#  Gerenciamento de Token (Access Token + Auto-Refresh)
# ═══════════════════════════════════════════════════════════

class TokenManager:
    """Gerencia o access_token do Phiz com renovação automática."""

    def __init__(self) -> None:
        self.access_token: str = ""
        self.refresh_token: str = ""
        self.expires_at: float = 0.0  # timestamp unix

    async def ensure_valid_token(self, client: httpx.AsyncClient) -> str:
        """Retorna um token válido, renovando se necessário."""
        if self.access_token and time.time() < self.expires_at - 60:
            return self.access_token

        if self.refresh_token:
            try:
                return await self._refresh(client)
            except Exception:
                logger.warning("Falha ao renovar token, tentando autenticar novamente...")

        return await self._authenticate(client)

    async def _authenticate(self, client: httpx.AsyncClient) -> str:
        """Obtém um novo access_token via credenciais."""
        url = f"{PHIZ_API_BASE}/gateway/openapi/auth"
        payload = {
            "app_id": PHIZ_APP_ID,
            "app_secret": PHIZ_APP_SECRET,
            "description": "Academic-Analysis Bot",
            "grant_type": "user_credentials",
            "scope": "channel",
        }

        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("success"):
            raise RuntimeError(f"Falha na autenticação: {data}")

        token_data = data["data"]
        self.access_token = token_data["access_token"]
        self.refresh_token = token_data["refresh_token"]
        self.expires_at = time.time() + token_data["expires_in"]

        logger.info("✅ Access token obtido com sucesso (expira em %ds)", token_data["expires_in"])
        return self.access_token

    async def _refresh(self, client: httpx.AsyncClient) -> str:
        """Renova o access_token usando o refresh_token."""
        url = f"{PHIZ_API_BASE}/gateway/openapi/token/refresh"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("success"):
            raise RuntimeError(f"Falha ao renovar token: {data}")

        token_data = data["data"]
        self.access_token = token_data["access_token"]
        self.refresh_token = token_data.get("refresh_token", self.refresh_token)
        self.expires_at = time.time() + token_data["expires_in"]

        logger.info("🔄 Token renovado com sucesso")
        return self.access_token


# Instância global
token_manager = TokenManager()

# HTTP client global (reutilizado entre requests)
http_client: httpx.AsyncClient | None = None


# ═══════════════════════════════════════════════════════════
#  Ciclo de vida da aplicação
# ═══════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    global http_client
    http_client = httpx.AsyncClient(timeout=30.0)

    logger.info("🚀 Servidor Phiz Webhook iniciado")

    # Tenta obter o token inicial
    if PHIZ_APP_ID and PHIZ_APP_SECRET:
        try:
            await token_manager.ensure_valid_token(http_client)
        except Exception as e:
            logger.warning("⚠️  Não foi possível obter token inicial: %s", e)
            logger.info("   O token será obtido na primeira mensagem recebida.")
    else:
        logger.warning("⚠️  Credenciais do Phiz não configuradas. Preencha o .env")

    yield

    await http_client.aclose()
    logger.info("🛑 Servidor encerrado")


# ═══════════════════════════════════════════════════════════
#  Aplicação FastAPI
# ═══════════════════════════════════════════════════════════

app = FastAPI(
    title="Phiz Webhook Server",
    description="Recebe mensagens do Phiz e responde 'Funcionou'",
    version="1.0.0",
    lifespan=lifespan,
)


# ═══════════════════════════════════════════════════════════
#  Funções auxiliares
# ═══════════════════════════════════════════════════════════

def verify_signature(body: bytes, signature_header: str | None, secret: str) -> bool:
    """
    Valida a assinatura HMAC-SHA256 do webhook.
    O header X-Phiz-Signature vem no formato: sha256=<hmac_hex>
    """
    if not signature_header:
        return False

    if not signature_header.startswith("sha256="):
        return False

    received_hash = signature_header[len("sha256="):]
    expected_hash = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(received_hash, expected_hash)


async def send_message(to: str, text: str) -> dict[str, Any]:
    """
    Envia uma mensagem de texto via Phiz Business API.

    Args:
        to: Número do destinatário (formato do Phiz, ex: "8613999999999")
        text: Corpo da mensagem
    """
    assert http_client is not None, "HTTP client não inicializado"

    token = await token_manager.ensure_valid_token(http_client)

    url = (
        f"{PHIZ_API_BASE}/v4/openapi/oauth/channel/robot/business"
        f"/{PHIZ_CHANNEL_ID}/messages"
    )

    payload = {
        "messaging_product": "phiz",
        "recipient_type": "individual",
        "to": [to],
        "type": "text",
        "text": {"body": text},
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    resp = await http_client.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        logger.error("❌ Erro ao enviar mensagem: %s — %s", resp.status_code, resp.text)
        resp.raise_for_status()

    result = resp.json()
    logger.info("📤 Mensagem enviada para %s | status: %s", to, result)
    return result


# ═══════════════════════════════════════════════════════════
#  Processamento dos eventos do webhook
# ═══════════════════════════════════════════════════════════

# Conjunto para idempotência — evita processar a mesma mensagem duas vezes
processed_message_ids: set[str] = set()


async def handle_incoming_message(message: dict[str, Any]) -> None:
    """Processa uma mensagem recebida e responde 'Funcionou'."""
    msg_id = message.get("id", "")
    sender = message.get("from", "")
    msg_type = message.get("type", "unknown")
    content = message.get("content", {})
    body = content.get("body", "") if isinstance(content, dict) else str(content)

    # Idempotência
    if msg_id in processed_message_ids:
        logger.info("⏭️  Mensagem %s já processada, ignorando", msg_id)
        return

    processed_message_ids.add(msg_id)

    # Limpa mensagens antigas para não crescer indefinidamente
    if len(processed_message_ids) > 10_000:
        processed_message_ids.clear()

    logger.info(
        "📩 Mensagem recebida | de: %s | tipo: %s | conteúdo: %s",
        sender, msg_type, body[:100],
    )

    # ── Responde "Funcionou" ────────────────────────────────
    try:
        await send_message(to=sender, text="Funcionou")
        logger.info("✅ Resposta 'Funcionou' enviada para %s", sender)
    except Exception as e:
        logger.error("❌ Falha ao responder para %s: %s", sender, e)


def handle_status_update(status: dict[str, Any]) -> None:
    """Processa atualizações de status de entrega."""
    msg_id = status.get("id", "")
    delivery_status = status.get("status", "")
    recipient = status.get("recipient_id", "")

    logger.info(
        "📊 Status de entrega | msg: %s | status: %s | destinatário: %s",
        msg_id, delivery_status, recipient,
    )


# ═══════════════════════════════════════════════════════════
#  Endpoints
# ═══════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Health check."""
    return {
        "status": "online",
        "service": "Phiz Webhook Server",
        "version": "1.0.0",
    }


@app.get("/webhook/receiver")
async def webhook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    Passo 6 — Verificação da URL do Webhook.

    O Phiz envia um GET com hub.mode, hub.challenge e hub.verify_token.
    Precisamos retornar o challenge exato se o verify_token bater.
    """
    logger.info(
        "🔑 Verificação de webhook recebida | mode: %s | token: %s",
        hub_mode, hub_verify_token,
    )

    if hub_mode != "subscribe":
        raise HTTPException(status_code=403, detail="Modo inválido")

    # Verifica contra os dois tokens possíveis
    valid_tokens = {VERIFY_TOKEN_STATUSES, VERIFY_TOKEN_MESSAGES}

    if hub_verify_token not in valid_tokens:
        logger.warning("❌ Verify token inválido: %s", hub_verify_token)
        raise HTTPException(status_code=403, detail="Token de verificação inválido")

    logger.info("✅ Webhook verificado com sucesso!")

    # Retorna o challenge como texto puro
    return Response(content=hub_challenge, media_type="text/plain")


@app.post("/webhook/receiver")
async def webhook_receive(
    request: Request,
    x_phiz_signature: str | None = Header(None, alias="X-Phiz-Signature"),
):
    """
    Passo 9 — Recebe callbacks do Phiz (robot:messages e robot:statuses).

    Valida a assinatura HMAC-SHA256 e processa os eventos.
    """
    raw_body = await request.body()

    # ── Validação da assinatura ─────────────────────────────
    signature_valid = (
        verify_signature(raw_body, x_phiz_signature, WEBHOOK_SECRET_MESSAGES)
        or verify_signature(raw_body, x_phiz_signature, WEBHOOK_SECRET_STATUSES)
    )

    if not signature_valid:
        logger.warning("⚠️  Assinatura inválida no webhook")
        # Em produção, descomente a linha abaixo:
        # raise HTTPException(status_code=403, detail="Assinatura inválida")
        logger.info("   (assinatura ignorada em modo desenvolvimento)")

    # ── Parse do payload ────────────────────────────────────
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    logger.info("📨 Webhook recebido: %s", payload)

    # ── Processa cada entry/change ──────────────────────────
    entries = payload.get("entry", [])

    for entry in entries:
        changes = entry.get("changes", [])

        for change in changes:
            field = change.get("field", "")
            value = change.get("value", {})

            if field == "robot:messages":
                messages = value.get("messages", [])
                for message in messages:
                    await handle_incoming_message(message)

            elif field == "robot:statuses":
                statuses = value.get("statuses", [])
                for status in statuses:
                    handle_status_update(status)

            else:
                logger.warning("⚠️  Campo desconhecido no webhook: %s", field)

    return {"status": "ok"}


# ═══════════════════════════════════════════════════════════
#  Setup dos Webhooks (utilitário para configuração inicial)
# ═══════════════════════════════════════════════════════════

@app.post("/setup/webhooks")
async def setup_webhooks(webhook_url: str):
    """
    Utilitário para configurar os webhooks no Phiz.
    Chame este endpoint passando a URL pública do seu servidor.

    Exemplo:
        POST /setup/webhooks?webhook_url=https://seu-dominio.com/webhook/receiver
    """
    assert http_client is not None

    token = await token_manager.ensure_valid_token(http_client)
    url = f"{PHIZ_API_BASE}/v4/openapi/oauth/set_webhooks"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    results = {}

    # Webhook 1: robot:statuses
    resp1 = await http_client.post(url, json={
        "webhook_url": webhook_url,
        "verify_token": VERIFY_TOKEN_STATUSES,
        "subscribed_event": "robot:statuses",
    }, headers=headers)
    results["robot:statuses"] = resp1.json()
    logger.info("📡 Webhook robot:statuses configurado: %s", resp1.json())

    # Webhook 2: robot:messages
    resp2 = await http_client.post(url, json={
        "webhook_url": webhook_url,
        "verify_token": VERIFY_TOKEN_MESSAGES,
        "subscribed_event": "robot:messages",
    }, headers=headers)
    results["robot:messages"] = resp2.json()
    logger.info("📡 Webhook robot:messages configurado: %s", resp2.json())

    return {
        "status": "webhooks configurados",
        "results": results,
        "next_steps": [
            "Aguarde o Phiz enviar GET para verificação",
            "Confirme que ambos ficaram com status verificado",
            "Habilite o bot no Phiz Open Platform",
        ],
    }


# ═══════════════════════════════════════════════════════════
#  Execução direta
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
