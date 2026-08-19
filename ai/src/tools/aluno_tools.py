import os
import requests
import json
from agents import function_tool

API_BASE_URL = os.environ.get("PHIZLINK_API_URL", "http://localhost:8000")

@function_tool
def consultar_notas_aluno(numero_phiz: str) -> str:
    """Consulta as notas de um aluno na sua sala atual agrupadas por matéria, com relatório contendo média geral e por matéria.
    
    Args:
        numero_phiz: O número PhizLink do aluno.
    """
    url = f"{API_BASE_URL}/aluno/notas"
    params = {"numero_phiz": numero_phiz}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)

@function_tool
def consultar_presenca_aluno(numero_phiz: str) -> str:
    """Consulta todas as aulas que o aluno deveria participar, quais teve presença e quais faltou, com relatório de porcentagem.
    
    Args:
        numero_phiz: O número PhizLink do aluno.
    """
    url = f"{API_BASE_URL}/aluno/presenca"
    params = {"numero_phiz": numero_phiz}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)
