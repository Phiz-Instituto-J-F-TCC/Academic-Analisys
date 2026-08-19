import os
import requests
import json
from agents import function_tool

API_BASE_URL = os.environ.get("PHIZLINK_API_URL", "http://localhost:8000")

@function_tool
def verificar_tipo_usuario(numero_phiz: str) -> str:
    """Retorna a qual tipo de usuário (aluno, professor ou coordenador) um número do Phiz pertence.
    
    Args:
        numero_phiz: O número PhizLink a ser verificado.
    """
    url = f"{API_BASE_URL}/tipo-usuario/{numero_phiz}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)
