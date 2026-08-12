# 🌤️ Chatbot Multi-Agente de Meteorologia

Chatbot inteligente sobre meteorologia e climatologia construído com o **OpenAI Agents SDK**, demonstrando uma arquitetura multi-agente com 6 componentes especializados.

## 🏗️ Arquitetura

```
                         ┌─────────────────┐
                         │    Usuário       │
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │   🔒 GUARDRAIL           │
                    │   Valida se é meteorologia│
                    └────────────┬─────────────┘
                                 │ (se válido)
                                 ▼
                    ┌──────────────────────────┐
                    │   🔀 ROTEADOR            │
                    │   Decide small talk,     │
                    │   identidade ou especialista  │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   🌦️ ESPECIALISTA        │
                    │   Usa ferramentas para   │
                    │   gerar resposta técnica │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   🎯 ORQUESTRADOR        │
                    │   Humaniza a resposta    │
                    └──────┬─────────────┘
                           │           │
                    ┌──────▼──┐   ┌────▼───────┐
                    │ 🌦️ Prev.│   │ 📊 Análise │
                    │ do Tempo│   │  Climática  │
                    │ (3 tools)│  │  (3 tools)  │
                    └──────┬──┘   └────┬───────┘
                           │           │
                           └─────┬─────┘
                                 ▼
                    ┌──────────────────────────┐
                    │   ⚖️ JUIZ                │
                    │   Avalia a qualidade     │
                    └──────────────────────────┘
```

## 📦 Componentes

| Componente        | Arquivo                      | Descrição                                       |
| ----------------- | ---------------------------- | ----------------------------------------------- |
| **Guardrail**     | `src/agents/guardrail.py`    | Valida se a entrada é sobre meteorologia        |
| **Orquestrador**  | `src/agents/orchestrator.py` | Humaniza a saída técnica do especialista        |
| **Entry point**   | `main.py`                    | Inicia e coordena o pipeline de execução        |
| **Roteador**      | `src/agents/router.py`       | Roteia para o especialista adequado via handoff |
| **Esp. Previsão** | `src/agents/specialists.py`  | Previsão do tempo com 3 ferramentas             |
| **Esp. Clima**    | `src/agents/specialists.py`  | Análise climática com 3 ferramentas             |
| **Juiz**          | `src/agents/judge.py`        | Avalia qualidade da resposta (1-10)             |

## 🔧 Ferramentas (Tools)

### Especialista em Previsão do Tempo

| Ferramenta                             | Descrição                       |
| -------------------------------------- | ------------------------------- |
| `obter_clima_atual(cidade)`            | Condições meteorológicas atuais |
| `obter_previsao_tempo(cidade, dias)`   | Previsão para os próximos dias  |
| `obter_alertas_meteorologicos(regiao)` | Alertas do INMET ativos         |

### Especialista em Análise Climática

| Ferramenta                                             | Descrição                  |
| ------------------------------------------------------ | -------------------------- |
| `obter_historico_climatico(cidade, mes)`               | Dados históricos de clima  |
| `obter_indices_climaticos(indice)`                     | El Niño, La Niña, IOD, AMO |
| `comparar_clima_periodos(cidade, ano_inicio, ano_fim)` | Tendências entre períodos  |

> **Nota:** As ferramentas retornam dados simulados para demonstração. Em produção, substitua por APIs reais (OpenWeatherMap, INMET, CPTEC/INPE, etc.).

## 🚀 Como Usar

### 1. Pré-requisitos

- Python 3.10+
- Chave de API da OpenAI

### 2. Instalação

```bash
# Clone ou acesse o diretório do projeto
cd TEMPLATE_BOM

# Crie e ative um ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração

```bash
# Copie o arquivo de exemplo e adicione sua chave
copy .env.example .env

# Edite o .env e coloque sua chave:
# OPENAI_API_KEY=sk-sua-chave-aqui
```

### 4. Execução

```bash
python main.py
```

## 💬 Exemplos de Uso

```
🧑 Você: Como está o tempo em São Paulo?
   → Roteado para: Especialista em Previsão do Tempo
   → Tools usadas: obter_clima_atual, obter_alertas_meteorologicos

🧑 Você: Qual a previsão para os próximos 5 dias no Rio de Janeiro?
   → Roteado para: Especialista em Previsão do Tempo
   → Tools usadas: obter_previsao_tempo

🧑 Você: O que é El Niño e como afeta o Brasil?
   → Roteado para: Especialista em Análise Climática
   → Tools usadas: obter_indices_climaticos

🧑 Você: Compare o clima de Curitiba entre 2000 e 2024
   → Roteado para: Especialista em Análise Climática
   → Tools usadas: comparar_clima_periodos

🧑 Você: Me dê uma receita de bolo
   → Guardrail acionado! ⚠️ Tópico fora do escopo
```

## 📁 Estrutura do Projeto

```
TEMPLATE_BOM/
├── .env.example          # Template para variáveis de ambiente
├── requirements.txt      # Dependências Python
├── README.md             # Documentação (este arquivo)
├── main.py               # Entry point do pipeline
└── src/
    ├── __init__.py
    ├── tools/
    │   ├── __init__.py
    │   ├── weather_tools.py   # 3 tools de previsão do tempo
    │   └── climate_tools.py   # 3 tools de análise climática
    └── agents/
        ├── __init__.py
        ├── guardrail.py       # Guardrail de validação de tópico
        ├── specialists.py     # 2 agentes especialistas com tools
        ├── router.py          # Roteador com handoffs
        └── judge.py           # Juiz de qualidade
```

## 🔑 Conceitos Demonstrados

- **Multi-Agent Systems**: Múltiplos agentes colaborando em pipeline
- **Guardrails**: Validação de entrada com tripwire para segurança
- **Handoffs**: Delegação de tarefas entre agentes especializados
- **Function Tools**: Ferramentas que agentes chamam autonomamente
- **Structured Output**: Saída estruturada com Pydantic (Guardrail e Juiz)
- **Orchestration**: Coordenação do fluxo completo via código Python

## 📄 Licença

Projeto educacional para TCC — uso livre para fins acadêmicos.
