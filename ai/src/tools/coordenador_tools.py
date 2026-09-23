import os
import requests
import json
from agents import function_tool

API_BASE_URL = os.environ.get("PHIZLINK_API_URL", "http://localhost:8000")

@function_tool
def relatorio_materia_coordenador(numero_phiz: str, sala: str, materia: str) -> str:
    """Relatório geral de uma turma em uma matéria. Sem verificação de vínculo.
    
    Args:
        numero_phiz: O número PhizLink do coordenador.
        sala: A sala da turma.
        materia: A matéria.
    """
    url = f"{API_BASE_URL}/coordenador/materia"
    params = {"numero_phiz": numero_phiz, "sala": sala, "materia": materia}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)

@function_tool
def relatorio_aluno_coordenador(numero_phiz: str, sala: str, materia: str, nome_aluno: str) -> str:
    """Relatório detalhado de um aluno em uma matéria. Sem verificação de vínculo.
    
    Args:
        numero_phiz: O número PhizLink do coordenador.
        sala: A sala da turma.
        materia: A matéria.
        nome_aluno: O nome do aluno.
    """
    url = f"{API_BASE_URL}/coordenador/aluno"
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


@function_tool
def visao_geral_sala_coordenador(numero_phiz: str, id_sala: int) -> str:
    """Visão geral de uma sala com todas as matérias.
    
    Args:
        numero_phiz: O número PhizLink do coordenador.
        id_sala: O ID da sala.
    """
    url = f"{API_BASE_URL}/coordenador/sala"
    params = {"numero_phiz": numero_phiz, "id_sala": id_sala}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)

@function_tool
def visao_geral_aluno_coordenador(numero_phiz: str, nome_aluno: str) -> str:
    """Visão geral completa de um aluno: todas matérias, notas e presença.
    
    Args:
        numero_phiz: O número PhizLink do coordenador.
        nome_aluno: O nome do aluno.
    """
    url = f"{API_BASE_URL}/coordenador/aluno/geral"
    params = {"numero_phiz": numero_phiz, "nome_aluno": nome_aluno}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)


@function_tool
def visao_geral_alunos_coordenador(numero_phiz: str) -> str:
    """Analisa todos os alunos em suas salas atuais.

    Args:
        numero_phiz: O número PhizLink do coordenador.
    """
    url = f"{API_BASE_URL}/coordenador/alunos/geral"
    params = {"numero_phiz": numero_phiz}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)


@function_tool
def visao_geral_serie_coordenador(numero_phiz: str, ano: int) -> str:
    """Analisa todas as salas e alunos de uma série atual.

    Args:
        numero_phiz: O número PhizLink do coordenador.
        ano: O ano da série.
    """
    url = f"{API_BASE_URL}/coordenador/serie/geral"
    params = {"numero_phiz": numero_phiz, "ano": ano}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)

