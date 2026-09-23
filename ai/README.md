# Chatbot Multi-Agente de Acompanhamento Acadêmico

Chatbot acadêmico construído com o **OpenAI Agents SDK**, demonstrando uma arquitetura multi-agente para acompanhamento de alunos, professores e coordenadores.

## 🏗️ Arquitetura

```
                         ┌─────────────────┐
                         │    Usuário       │
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │   🔒 GUARDRAIL           │
                    │ Valida o contexto acadêmico│
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
                    │   🧩 ESPECIALISTAS       │
                    │   Usam ferramentas para  │
                    │   gerar dados acadêmicos  │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   🎯 ORQUESTRADOR        │
                    │   Humaniza a resposta    │
                    └──────┬─────────────┘
                           │           │
                    ┌──────▼──┐   ┌────▼───────┐
                    │ 👨‍🎓 Aluno│   │ 👨‍🏫 Professor│
                    │ (2 tools)│   │  (2 tools)  │
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

| Componente           | Arquivo                      | Descrição                                       |
| -------------------- | ---------------------------- | ----------------------------------------------- |
| **Guardrail**        | `src/agents/guardrail.py`    | Valida se a entrada é acadêmica                 |
| **Orquestrador**     | `src/agents/orchestrator.py` | Humaniza a saída técnica do especialista        |
| **Entry point**      | `main.py`                    | Inicia e coordena o pipeline de execução        |
| **Roteador**         | `src/agents/router.py`       | Roteia para o especialista adequado via handoff |
| **Esp. Aluno**       | `src/agents/specialists.py`  | Notas e frequência do aluno                     |
| **Esp. Professor**   | `src/agents/specialists.py`  | Relatórios de matérias e alunos                 |
| **Esp. Coordenador** | `src/agents/specialists.py`  | Relatórios e visões gerais acadêmicas           |
| **Juiz**             | `src/agents/judge.py`        | Avalia qualidade da resposta (1-10)             |

## 🔧 Ferramentas (Tools)

### Especialista em Aluno

| Ferramenta                              | Descrição                                    |
| --------------------------------------- | -------------------------------------------- |
| `consultar_notas_aluno(numero_phiz)`    | Notas e médias gerais e por matéria          |
| `consultar_presenca_aluno(numero_phiz)` | Presenças, faltas e percentual de frequência |

### Especialista em Professor

| Ferramenta                                                          | Descrição                            |
| ------------------------------------------------------------------- | ------------------------------------ |
| `relatorio_materia_professor(numero_phiz, sala, materia)`           | Relatório da turma em uma matéria    |
| `relatorio_aluno_professor(numero_phiz, sala, materia, nome_aluno)` | Relatório de um aluno em uma matéria |

### Especialista em Coordenador

| Ferramenta                                                            | Descrição                                  |
| --------------------------------------------------------------------- | ------------------------------------------ |
| `relatorio_materia_coordenador(numero_phiz, sala, materia)`           | Relatório da turma em uma matéria          |
| `relatorio_aluno_coordenador(numero_phiz, sala, materia, nome_aluno)` | Relatório de um aluno em uma matéria       |
| `visao_geral_sala_coordenador(numero_phiz, id_sala)`                  | Visão geral da sala em todas as matérias   |
| `visao_geral_aluno_coordenador(numero_phiz, nome_aluno)`              | Visão geral do aluno, com notas e presença |
| `visao_geral_alunos_coordenador(numero_phiz)`                         | Análise geral de todos os alunos           |
| `visao_geral_serie_coordenador(numero_phiz, ano)`                     | Análise geral de uma série                 |

As ferramentas consultam a API definida por `PHIZLINK_API_URL`, cujo padrão é `http://localhost:8000`.

## 🚀 Como Usar

### 1. Pré-requisitos

- Python 3.10+
- Chave de API da OpenAI

### 2. Instalação

```bash
# Clone ou acesse o diretório do projeto
cd ai

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
🧑 Você: Quais são minhas notas e minha média por matéria?
   → Roteado para: Especialista Aluno
   → Tools usadas: consultar_notas_aluno

🧑 Você: Qual é minha porcentagem de frequência?
   → Roteado para: Especialista Aluno
   → Tools usadas: consultar_presenca_aluno

🧑 Você: Mostre o relatório da turma em Matemática.
   → Roteado para: Especialista Professor ou Coordenador
   → Tools usadas: relatorio_materia_professor ou relatorio_materia_coordenador

🧑 Você: Mostre a visão geral da sala.
   → Roteado para: Especialista Coordenador
   → Tools usadas: visao_geral_sala_coordenador

🧑 Você: Me dê uma receita de bolo
   → Guardrail acionado! ⚠️ Tópico fora do escopo
```

## 📁 Estrutura do Projeto

```
ai/
├── .env.example          # Template para variáveis de ambiente
├── requirements.txt      # Dependências Python
├── README.md             # Documentação (este arquivo)
├── main.py               # Entry point do pipeline
└── src/
    ├── __init__.py
    ├── tools/
    │   ├── __init__.py
   │   ├── aluno_tools.py       # Notas e frequência
   │   ├── professor_tools.py   # Relatórios do professor
   │   ├── coordenador_tools.py # Relatórios do coordenador
   │   └── geral_tools.py
    └── agents/
        ├── __init__.py
        ├── guardrail.py       # Guardrail de validação de tópico
        ├── specialists.py     # 2 agentes especialistas com tools
        ├── router.py          # Roteador com handoffs
        └── judge.py           # Juiz de qualidade
```

## 🔑 Conceitos Demonstrados

- **Multi-Agent Systems**: Agentes especializados por perfil acadêmico
- **Guardrails**: Validação de entrada com tripwire para segurança
- **Handoffs**: Delegação de tarefas entre agentes especializados
- **Function Tools**: Ferramentas que agentes chamam autonomamente
- **Structured Output**: Saída estruturada com Pydantic (Guardrail e Juiz)
- **Orchestration**: Coordenação do fluxo completo via código Python

## 📄 Licença

Projeto educacional para TCC — uso livre para fins acadêmicos.
