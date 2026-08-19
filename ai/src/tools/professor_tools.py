import os
import requests
import json
from agents import function_tool

API_BASE_URL = os.environ.get("PHIZLINK_API_URL", "http://localhost:8000")

@function_tool
def relatorio_materia_professor(numero_phiz: str, sala: str, materia: str) -> str:
    """Relatório geral de uma turma em uma matéria específica. Valida se o professor realmente leciona essa matéria nessa sala.
    
    Args:
        numero_phiz: O número PhizLink do professor.
        sala: A sala da turma.
        materia: A matéria lecionada.
    """
    url = f"{API_BASE_URL}/professor/materia"
    params = {"numero_phiz": numero_phiz, "sala": sala, "materia": materia}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)

@function_tool
def relatorio_aluno_professor(numero_phiz: str, sala: str, materia: str, nome_aluno: str) -> str:
    """Relatório detalhado de um aluno específico em uma matéria. Valida se o professor leciona essa matéria e se o aluno pertence à sala.
    
    Args:
        numero_phiz: O número PhizLink do professor.
        sala: A sala da turma.
        materia: A matéria lecionada.
        nome_aluno: O nome do aluno.
    """
    url = f"{API_BASE_URL}/professor/aluno"
    params = {
        "numero_phiz": numero_phiz,
        "sala": sala,
        "materia": materia,
        "nome_aluno": nome_aluno
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)

