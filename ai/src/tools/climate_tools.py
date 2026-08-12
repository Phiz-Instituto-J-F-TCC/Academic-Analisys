"""
Ferramentas (Tools) para o Especialista em Análise Climática.

Estas ferramentas simulam APIs de dados climáticos históricos e índices.
Em produção, você substituiria por APIs reais como INMET, CPTEC/INPE,
Copernicus Climate Data Store, NOAA, etc.
"""

import json
import random

from agents import function_tool


@function_tool
def obter_historico_climatico(cidade: str, mes: int) -> str:
    """Obtém dados históricos de clima para uma cidade em um mês específico.

    Args:
        cidade: Nome da cidade brasileira (ex: 'São Paulo', 'Manaus').
        mes: Número do mês (1 = Janeiro, 12 = Dezembro).
    """
    meses_nomes = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    ]

    mes = max(1, min(12, mes))
    nome_mes = meses_nomes[mes - 1]

    # Valores simulados com variações realistas por mês
    temp_base = 22 + 5 * (1 - abs(mes - 1) / 6)  # Mais quente no verão
    precip_base = 150 if mes in [1, 2, 3, 10, 11, 12] else 60  # Chuvoso no verão

    dados = {
        "cidade": cidade,
        "mes": nome_mes,
        "numero_mes": mes,
        "media_historica": {
            "temperatura_media_celsius": round(temp_base + random.uniform(-3, 3), 1),
            "temperatura_maxima_media_celsius": round(temp_base + random.uniform(3, 8), 1),
            "temperatura_minima_media_celsius": round(temp_base - random.uniform(5, 10), 1),
            "precipitacao_acumulada_mm": round(precip_base + random.uniform(-40, 80), 1),
            "dias_com_chuva": random.randint(5, 22),
            "umidade_relativa_media_pct": random.randint(45, 85),
            "insolacao_horas_mes": round(random.uniform(100, 250), 1),
        },
        "recordes": {
            "maior_temperatura_registrada": round(temp_base + random.uniform(10, 18), 1),
            "menor_temperatura_registrada": round(temp_base - random.uniform(12, 20), 1),
            "maior_precipitacao_24h_mm": round(random.uniform(50, 200), 1),
        },
        "periodo_referencia": "1991-2020 (Normal Climatológica)",
        "fonte": "INMET - Instituto Nacional de Meteorologia",
    }

    return json.dumps(dados, ensure_ascii=False, indent=2)


@function_tool
def obter_indices_climaticos(indice: str) -> str:
    """Obtém informações atualizadas sobre índices climáticos globais.

    Args:
        indice: Nome do índice climático. Opções válidas:
            'el_nino' - El Niño (aquecimento do Pacífico)
            'la_nina' - La Niña (resfriamento do Pacífico)
            'iod' - Dipolo do Oceano Índico
            'amo' - Oscilação Multidecadal do Atlântico
    """
    indices_info = {
        "el_nino": {
            "nome": "El Niño - Oscilação Sul (ENOS)",
            "descricao": (
                "Aquecimento anômalo das águas superficiais do Oceano Pacífico "
                "equatorial central e oriental."
            ),
            "status_atual": random.choice(["Ativo", "Neutro", "Em formação"]),
            "intensidade": random.choice(["Fraco", "Moderado", "Forte", "Muito Forte"]),
            "indice_oni": round(random.uniform(-0.5, 2.5), 2),
            "regiao_nino_3_4_celsius": round(random.uniform(-0.5, 2.0), 2),
            "impactos_brasil": {
                "norte": "Redução de chuvas, aumento de temperatura, risco de seca",
                "nordeste": "Seca severa, redução significativa de precipitação",
                "centro_oeste": "Alteração no regime de chuvas",
                "sudeste": "Aumento de temperatura, ondas de calor",
                "sul": "Chuvas acima da média, risco de enchentes",
            },
            "tendencia": "Monitoramento contínuo pela NOAA e CPTEC/INPE",
            "fonte": "NOAA Climate Prediction Center / CPTEC-INPE",
        },
        "la_nina": {
            "nome": "La Niña",
            "descricao": (
                "Resfriamento anômalo das águas superficiais do Oceano Pacífico "
                "equatorial, fenômeno oposto ao El Niño."
            ),
            "status_atual": random.choice(["Ativo", "Neutro", "Em formação"]),
            "intensidade": random.choice(["Fraco", "Moderado", "Forte"]),
            "indice_oni": round(random.uniform(-2.5, 0.5), 2),
            "regiao_nino_3_4_celsius": round(random.uniform(-2.0, 0.5), 2),
            "impactos_brasil": {
                "norte": "Chuvas acima da média",
                "nordeste": "Chuvas acima da média, favorável para agricultura",
                "centro_oeste": "Variações no regime de chuvas",
                "sudeste": "Temperaturas ligeiramente mais baixas",
                "sul": "Seca, redução de precipitação, impactos na agricultura",
            },
            "tendencia": "Monitoramento contínuo pela NOAA e CPTEC/INPE",
            "fonte": "NOAA Climate Prediction Center / CPTEC-INPE",
        },
        "iod": {
            "nome": "Dipolo do Oceano Índico (IOD)",
            "descricao": (
                "Diferença de temperatura da superfície do mar entre a porção "
                "ocidental e oriental do Oceano Índico tropical."
            ),
            "status_atual": random.choice(["Positivo", "Neutro", "Negativo"]),
            "indice_dmi": round(random.uniform(-1.5, 1.5), 2),
            "impactos_brasil": (
                "Influência indireta na circulação atmosférica sobre a Amazônia "
                "e no transporte de umidade para o sudeste."
            ),
            "fonte": "Bureau of Meteorology (Austrália) / CPTEC-INPE",
        },
        "amo": {
            "nome": "Oscilação Multidecadal do Atlântico (AMO)",
            "descricao": (
                "Variação de longo prazo na temperatura da superfície do "
                "Oceano Atlântico Norte, com ciclos de 60-80 anos."
            ),
            "status_atual": random.choice(["Fase quente", "Fase fria", "Transição"]),
            "indice_amo": round(random.uniform(-0.5, 0.5), 3),
            "impactos_brasil": (
                "Influência significativa nas chuvas do Nordeste brasileiro "
                "e na atividade de furacões no Atlântico."
            ),
            "fonte": "NOAA Earth System Research Laboratories",
        },
    }

    chave = indice.lower().strip().replace(" ", "_").replace("-", "_")

    if chave in indices_info:
        return json.dumps(indices_info[chave], ensure_ascii=False, indent=2)
    else:
        return json.dumps({
            "erro": f"Índice '{indice}' não encontrado.",
            "indices_disponiveis": list(indices_info.keys()),
            "dica": "Use uma das opções: 'el_nino', 'la_nina', 'iod', 'amo'",
        }, ensure_ascii=False, indent=2)


@function_tool
def comparar_clima_periodos(cidade: str, ano_inicio: int, ano_fim: int) -> str:
    """Compara dados climáticos médios entre dois anos para identificar tendências.

    Args:
        cidade: Nome da cidade brasileira.
        ano_inicio: Ano inicial do período de comparação (ex: 2000).
        ano_fim: Ano final do período de comparação (ex: 2024).
    """
    anos_diff = abs(ano_fim - ano_inicio)
    fator = anos_diff / 30  # Normaliza para 30 anos

    diff_temp = round(random.uniform(0.3, 1.8) * fator, 2)
    diff_chuva = round(random.uniform(-20, 15) * fator, 1)
    diff_extremos = round(random.uniform(5, 40) * fator, 1)

    dados = {
        "cidade": cidade,
        "periodo_comparacao": f"{ano_inicio} — {ano_fim}",
        "duracao_anos": anos_diff,
        "variacoes": {
            "temperatura_media": {
                "variacao": f"+{diff_temp}°C",
                "tendencia": "📈 Aquecimento" if diff_temp > 0 else "📉 Resfriamento",
                "taxa_por_decada": f"+{round(diff_temp / (anos_diff / 10), 3)}°C/década",
            },
            "precipitacao": {
                "variacao": f"{'+' if diff_chuva > 0 else ''}{diff_chuva}%",
                "tendencia": "📈 Aumento" if diff_chuva > 0 else "📉 Redução",
            },
            "eventos_extremos": {
                "variacao_frequencia": f"+{diff_extremos}%",
                "ondas_calor": random.choice(["Aumento significativo", "Aumento moderado", "Estável"]),
                "secas_prolongadas": random.choice(["Aumento", "Estável", "Redução leve"]),
                "chuvas_intensas": random.choice(["Aumento significativo", "Aumento", "Estável"]),
                "geadas": random.choice(["Redução significativa", "Redução", "Estável"]),
            },
        },
        "contexto": (
            f"A variação de {diff_temp}°C em {anos_diff} anos está "
            f"{'acima' if diff_temp > 1.0 else 'dentro'} da média global de aquecimento "
            f"reportada pelo IPCC (1.1°C desde a era pré-industrial)."
        ),
        "fontes": [
            "IPCC AR6 - Sexto Relatório de Avaliação",
            "INMET - Normais Climatológicas",
            "PBMC - Painel Brasileiro de Mudanças Climáticas",
        ],
    }

    return json.dumps(dados, ensure_ascii=False, indent=2)
