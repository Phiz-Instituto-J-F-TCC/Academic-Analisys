"""
Ferramentas (Tools) para o Especialista em Previsão do Tempo.

Estas ferramentas simulam APIs externas de dados meteorológicos em tempo real.
Em produção, você substituiria os dados simulados por chamadas a APIs reais
como OpenWeatherMap, INMET, CPTEC/INPE, etc.
"""

import json
import random
from datetime import datetime, timedelta

from agents import function_tool


@function_tool
def obter_clima_atual(cidade: str) -> str:
    """Obtém as condições climáticas atuais para uma cidade específica.

    Args:
        cidade: Nome da cidade para consultar o clima atual (ex: 'São Paulo', 'Rio de Janeiro').
    """
    condicoes = [
        "Ensolarado ☀️",
        "Parcialmente nublado ⛅",
        "Nublado ☁️",
        "Chuvoso 🌧️",
        "Tempestade ⛈️",
        "Céu limpo 🌤️",
    ]

    dados = {
        "cidade": cidade,
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "temperatura_celsius": round(random.uniform(15, 38), 1),
        "sensacao_termica_celsius": round(random.uniform(13, 42), 1),
        "umidade_percentual": random.randint(30, 95),
        "condicao": random.choice(condicoes),
        "velocidade_vento_kmh": round(random.uniform(5, 60), 1),
        "direcao_vento": random.choice(["N", "NE", "L", "SE", "S", "SO", "O", "NO"]),
        "pressao_atmosferica_hpa": round(random.uniform(1005, 1025), 1),
        "indice_uv": random.randint(1, 11),
        "visibilidade_km": round(random.uniform(2, 20), 1),
        "ponto_orvalho_celsius": round(random.uniform(10, 25), 1),
    }

    return json.dumps(dados, ensure_ascii=False, indent=2)


@function_tool
def obter_previsao_tempo(cidade: str, dias: int) -> str:
    """Obtém a previsão do tempo para uma cidade nos próximos dias.

    Args:
        cidade: Nome da cidade para a previsão.
        dias: Quantidade de dias para previsão (1 a 7).
    """
    dias = max(1, min(7, dias))

    condicoes = [
        "Ensolarado ☀️",
        "Parcialmente nublado ⛅",
        "Nublado ☁️",
        "Chuva leve 🌦️",
        "Chuva forte 🌧️",
        "Tempestade ⛈️",
        "Céu limpo 🌤️",
    ]

    previsoes = []
    for i in range(dias):
        data = datetime.now() + timedelta(days=i + 1)
        temp_min = round(random.uniform(12, 25), 1)
        temp_max = round(random.uniform(temp_min + 3, 40), 1)

        previsoes.append({
            "data": data.strftime("%d/%m/%Y"),
            "dia_semana": data.strftime("%A"),
            "temperatura_min_celsius": temp_min,
            "temperatura_max_celsius": temp_max,
            "condicao": random.choice(condicoes),
            "probabilidade_chuva_pct": random.randint(0, 100),
            "volume_chuva_mm": round(random.uniform(0, 80), 1),
            "umidade_pct": random.randint(30, 95),
            "vento_kmh": round(random.uniform(5, 50), 1),
        })

    resultado = {
        "cidade": cidade,
        "periodo": f"Próximos {dias} dia(s)",
        "previsoes": previsoes,
    }

    return json.dumps(resultado, ensure_ascii=False, indent=2)


@function_tool
def obter_alertas_meteorologicos(regiao: str) -> str:
    """Verifica se existem alertas meteorológicos ativos para uma região ou estado.

    Args:
        regiao: Nome da região, estado ou cidade brasileira (ex: 'São Paulo', 'Sul', 'Minas Gerais').
    """
    tipos_alerta = [
        {
            "tipo": "🔴 Chuva intensa",
            "severidade": "Grande Perigo",
            "descricao": "Previsão de chuvas acima de 100mm/h. Risco de alagamentos e deslizamentos.",
            "recomendacao": "Evite áreas de risco. Não atravesse ruas alagadas.",
        },
        {
            "tipo": "🟠 Vendaval",
            "severidade": "Perigo",
            "descricao": "Rajadas de vento entre 80-100 km/h previstas para as próximas horas.",
            "recomendacao": "Proteja-se em locais seguros. Evite estacionar sob árvores.",
        },
        {
            "tipo": "🔴 Onda de calor",
            "severidade": "Grande Perigo",
            "descricao": "Temperaturas acima de 40°C previstas por 3 ou mais dias consecutivos.",
            "recomendacao": "Hidrate-se constantemente. Evite exposição ao sol entre 10h e 16h.",
        },
        {
            "tipo": "🟡 Geada",
            "severidade": "Perigo Potencial",
            "descricao": "Temperaturas próximas a 0°C previstas durante a madrugada.",
            "recomendacao": "Proteja plantas e animais. Agasalhe-se adequadamente.",
        },
        {
            "tipo": "🟠 Tempestade severa",
            "severidade": "Perigo",
            "descricao": "Previsão de granizo e raios com rajadas de vento superiores a 60 km/h.",
            "recomendacao": "Busque abrigo imediatamente. Desconecte equipamentos eletrônicos.",
        },
    ]

    # Simula presença ou ausência de alertas
    if random.random() > 0.35:
        num_alertas = random.randint(1, 3)
        alertas = random.sample(tipos_alerta, min(num_alertas, len(tipos_alerta)))
        resultado = {
            "regiao": regiao,
            "alertas_ativos": True,
            "quantidade": num_alertas,
            "alertas": alertas,
            "fonte": "INMET - Instituto Nacional de Meteorologia",
            "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    else:
        resultado = {
            "regiao": regiao,
            "alertas_ativos": False,
            "quantidade": 0,
            "alertas": [],
            "mensagem": "✅ Nenhum alerta meteorológico ativo para esta região.",
            "fonte": "INMET - Instituto Nacional de Meteorologia",
            "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    return json.dumps(resultado, ensure_ascii=False, indent=2)
