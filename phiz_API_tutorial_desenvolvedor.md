# Tutorial: Integração com a Phiz Business API (a partir do bot criado)

> **Pré-requisitos para este tutorial:**
>
> - Conta no Phiz Open Platform
> - Channel criado e vinculado ao seu usuário
> - Bot criado no Channel, em modo **Phiz Business API**, ainda **desabilitado** (não aplicado)

Antes de começar, pegue os três dados que vamos usar em toda a integração:

1. No Open Platform, acesse **"Informações do Canal"** e anote:
   - **`channel_id`**
   - **`AppID`**
   - **`AppSecret`**, vá em **"Configurações de Desenvolvimento"** e solicite/gere o `AppSecret` por lá (AppID também está nessa aba).

Guarde os três valores (`channel_id`, `AppID`, `AppSecret`) — eles são usados em praticamente todas as chamadas abaixo.

---

## Passo 4 — Obter o Access Token

Use o `AppID` e o `AppSecret` do Channel.

**Endpoint (ambiente de teste):**

```http
POST https://api-test.phiz.live/gateway/openapi/auth
Content-Type: application/json
```

**Corpo da requisição:**

```json
{
  "app_id": "YOUR_APP_ID",
  "app_secret": "YOUR_APP_SECRET",
  "description": "e.g: channel bot business api",
  "grant_type": "user_credentials",
  "scope": "channel"
}
```

**Resposta esperada:**

```json
{
  "code": 200,
  "msg": "Success",
  "data": {
    "access_token": "at_xxx",
    "token_type": "Bearer",
    "expires_in": 7199,
    "refresh_token": "rt_xxx",
    "refresh_token_expires_at": "2026-08-06T12:00:00Z"
  },
  "success": true
}
```

Use `Authorization: Bearer {access_token}` em todas as chamadas seguintes (Business API e `set_webhooks`).

**Renovando o token (quando expirar):**

```http
POST https://api-test.phiz.live/gateway/openapi/token/refresh
```

```json
{
  "grant_type": "refresh_token",
  "refresh_token": "rt_xxx"
}
```

> O token é vinculado ao Channel — usar em outro Channel retorna erro de permissão.

---

## Passo 5 — Configurar os dois Webhooks

Antes de enviar qualquer mensagem, é preciso registrar **duas** configurações de webhook (uma chamada por evento):

1. **`robot:statuses`** — status de entrega por destinatário (`SENT` / `FAILED`)
2. **`robot:messages`** — mensagens recebidas de usuários no Channel

> Cada chamada de `set_webhooks` vincula **um** `subscribed_event`. Você pode usar a mesma URL para os dois eventos (diferenciando via `changes[].field` depois) ou usar duas URLs distintas.

**Endpoint:**

```http
POST https://api-test.phiz.live/v4/openapi/oauth/set_webhooks
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Chamada 1 — `robot:statuses`:**

```json
{
  "webhook_url": "https://seu-dominio.com/webhook/receiver",
  "verify_token": "seu_verify_token_para_robot_statuses",
  "subscribed_event": "robot:statuses"
}
```

**Chamada 2 — `robot:messages`:**

```json
{
  "webhook_url": "https://seu-dominio.com/webhook/receiver",
  "verify_token": "seu_verify_token_para_robot_messages",
  "subscribed_event": "robot:messages"
}
```

| Campo              | Descrição                                                                               |
| ------------------ | --------------------------------------------------------------------------------------- |
| `webhook_url`      | Precisa ser HTTPS                                                                       |
| `verify_token`     | Você define (8–100 caracteres); precisa bater com `hub.verify_token` na verificação GET |
| `subscribed_event` | `robot:statuses` ou `robot:messages`                                                    |

**Resposta de sucesso (exemplo):**

```json
{
  "code": 200,
  "data": {
    "id": 1,
    "webhookUrl": "https://seu-dominio.com/webhook/receiver",
    "webhookSecret": "whs_xxx",
    "subscribedEvent": "robot:statuses",
    "status": "PENDING_VERIFICATION"
  },
  "success": true
}
```

> `code = 200` só confirma que a configuração foi aceita — não significa que a verificação já passou. Guarde o `webhookSecret` de **cada** configuração (podem ser diferentes por evento).

---

## Passo 6 — Verificação da URL do Webhook

Depois de salvar a configuração, o Phiz manda, de forma assíncrona, uma requisição GET para o seu `webhook_url` — **uma vez para cada evento configurado**.

```http
GET {webhook_url}?hub.mode=subscribe&hub.challenge={challenge}&hub.verify_token={verify_token}
```

Seu endpoint precisa responder com **HTTP 200** e corpo **exatamente igual** ao `challenge` recebido (texto puro):

```
se hub.mode == "subscribe" e hub.verify_token == SEU_TOKEN_SALVO:
    retorna hub.challenge
senão:
    rejeita
```

Se falhar, o status fica em `PENDING_VERIFICATION` — corrija seu endpoint e chame `set_webhooks` de novo.

---

## Passo 7 — Habilitar o bot

Só agora, com os dois webhooks configurados **e** verificados, faça isso:

1. Confirme que as duas configurações de webhook mostram verificação bem-sucedida.
2. Abra as configurações do bot do Channel no Phiz Open Platform.
3. **Habilite (apply)** o bot em modo Phiz Business API.

Antes disso, envio e recebimento de webhooks não funcionam de forma confiável.

---

## Passo 8 — Enviar uma mensagem (outbound)

**Endpoint:**

```http
POST https://api-test.phiz.live/v4/openapi/oauth/channel/robot/business/{channel_id}/messages
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Exemplo — mensagem de texto:**

```json
{
  "messaging_product": "phiz",
  "recipient_type": "individual",
  "to": ["+8613760284200"],
  "type": "text",
  "text": { "body": "Olá via Phiz Business API" }
}
```

Outros tipos suportados: `richtext` (título + corpo), `image`, `audio`, `video`, `document` — todos usam links HTTPS para a mídia.

**Resposta síncrona (aceite, não entrega):**

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "contacts": [{ "input": "+8613760284200", "message_status": "QUEUED" }],
    "message": { "id": "phmid.d3fb0a67-e453-4156-bd9e-6fb2272fd7f9" }
  },
  "success": true
}
```

`message_status` na resposta síncrona só pode ser `QUEUED` (aceito) ou `FAILED` (rejeitado na hora). **`SENT` nunca aparece aqui** — só chega depois pelo webhook `robot:statuses`.

> Se precisar garantir a ordem de recebimento entre várias mensagens, espere o `SENT` da mensagem atual (via webhook) antes de mandar a próxima — a ordem de entrega não é garantida pela ordem das chamadas.

---

## Passo 9 — Receber os callbacks (dois tipos de payload)

Todo evento chega envelopado no mesmo formato; o campo `changes[0].field` diz qual é:

```json
{
  "object": "phiz_channel",
  "entry": [
    {
      "id": "579",
      "changes": [
        {
          "field": "robot:statuses | robot:messages",
          "value": {}
        }
      ]
    }
  ]
}
```

**`robot:statuses`** — status de entrega das mensagens que você mandou:

```json
{
  "statuses": [
    {
      "id": "phmid.d3fb0a67-e453-4156-bd9e-6fb2272fd7f9",
      "status": "SENT",
      "timestamp": "1778253796",
      "recipient_id": "+8613760284200"
    }
  ]
}
```

**`robot:messages`** — mensagem recebida de um usuário:

```json
{
  "messages": [
    {
      "from": "8613999999999",
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "type": "text",
      "content": { "body": "Olá vindo do usuário" }
    }
  ]
}
```

---

## Passo 10 — Verificar a assinatura do webhook

Todo POST vem com o header `X-Phiz-Signature: sha256=<hmac_hex>`. Para validar:

1. Leia o corpo **bruto** do JSON (antes de fazer parse).
2. Calcule HMAC-SHA256 usando o `webhookSecret` daquela configuração específica.
3. Compare com o valor do header, removendo o prefixo `sha256=`.

```
esperado = HMAC_SHA256_HEX(corpo_bruto, webhook_secret)
válido = (header == "sha256=" + esperado)
```

Use `statuses[].id` + `recipient_id` (ou `messages[].id`) como chave de idempotência, para não processar o mesmo evento duas vezes.

---

## Checklist rápido de solução de problemas

| Sintoma                                     | Causa provável                                                                                            |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Webhook fica em `PENDING_VERIFICATION`      | Endpoint não devolveu o `challenge` exato, ou `verify_token` não bate                                     |
| `QUEUED` na resposta mas mensagem não chega | Normal — espere o `robot:statuses`; confirme que o bot está habilitado                                    |
| Nenhum webhook chega                        | Nome do evento errado (`robot:statuses`, não `statuses`); assinatura falhando silenciosamente do seu lado |
| Erro "bot not applied"                      | Falta habilitar o bot — só faça isso depois dos dois webhooks verificados (Passo 7)                       |

---

## Resumo do fluxo completo

1. ~~Registrar usuário → merchant → Channel → bot em modo Business API (desabilitado)~~ ✅ já feito
2. `POST /gateway/openapi/auth` → `access_token`
3. `set_webhooks` com `robot:statuses`
4. `set_webhooks` com `robot:messages`
5. Verificar os dois via GET
6. Habilitar (apply) o bot
7. `POST .../channel/robot/business/{channel_id}/messages` para enviar
8. Receber `robot:statuses` (status) e `robot:messages` (mensagens recebidas) via webhook
