import requests
import json

base_url = "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/tgvmax/records"

# --- Defina seus critérios de busca aqui ---
origem_busca = "grenoble" # Será usado "like" na consulta
    
params = {
    "limit": 5,  # Limita a resposta aos primeiros 5 trens
    "where": f"origine like '{origem_busca}'",
}

try:
    response = requests.get(base_url, params=params)
    URL = response.url  # Captura a URL completa da requisição
    print(f"URL da requisição: {URL}")

    response.raise_for_status()  # Lança uma exceção para respostas com erro (4xx ou 5xx)

    data = response.json()

    # Exibindo os dados de forma legível
    print("Resposta da API TGV Max:")
    print(json.dumps(data, indent=4, ensure_ascii=False)) # ensure_ascii=False para caracteres acentuados
        
        

except requests.exceptions.HTTPError as http_err:
    print(f"Erro HTTP: {http_err}")
except requests.exceptions.ConnectionError as conn_err:
    print(f"Erro de Conexão: {conn_err}")
except requests.exceptions.Timeout as timeout_err:
    print(f"Erro de Timeout: {timeout_err}")
except requests.exceptions.RequestException as req_err:
    print(f"Erro na Requisição: {req_err}")
except json.JSONDecodeError:
    print("Erro ao decodificar a resposta JSON.")