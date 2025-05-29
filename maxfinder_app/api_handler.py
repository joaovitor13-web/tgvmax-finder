import requests
import json

class MaxFinderAPI:

    BASE_URL = "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/tgvmax/records"


    def __init__(self):
        # Parâmetros de busca
        self.limite = 100
        self.origem_busca = None
        self.destino_busca = None
        self.data_busca = None # Ex: "AAAA/MM/DD"
        
        # Atributos internos
        self.data_response_json = None
        self.last_url_requested = None # Variável para armazenar a última URL requisitada
        self.session = requests.Session() # Usar uma sessão requests
        self.session.headers.update({"User-Agent": "MaxFinderApp"})

    # Setters para os parâmetros de busca
    def setLimite(self, limite):
        self.limite = limite

    def setOrigemBusca(self, origem):
        self.origem_busca = origem  

    def setDestinoBusca(self, destino):
        self.destino_busca = destino    

    def setDataBusca(self, data):
        self.data_busca = data

    # Funções restantes
    def createParams(self):
        params = {"limit": self.limite}

        params["where"] = "od_happy_card='OUI'"  # Filtro crucial para trens TGV Max (indica que há disponibilidade)
        params["order_by"] = "date"  # Ordenar por data

        if self.origem_busca:
            params["where"] += f" AND origine like '{self.origem_busca}'"
        if self.destino_busca:
            params["where"] += f" AND destination like '{self.destino_busca}'"
        if self.data_busca:
            params["where"] += f" AND date=date'{self.data_busca}'"
             
        return params

    def getParams(self):
        return self.createParams()
    
    def requestResponse(self):
        params = self.createParams()

        try:
            response = self.session.get(self.BASE_URL, params=params)
            self.last_URL = response.url  # Captura a URL completa da requisição
            response.raise_for_status()  # Lança uma exceção para respostas com erro (4xx ou 5xx)
            self.data_response_json = response.json()
                
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

    def printResponse(self):
        print("Resposta da API TGV Max:")
        print(json.dumps(self.data_response_json, indent=4, ensure_ascii=False)) # ensure_ascii=False para caracteres acentuados   


# Exemplo de uso
""" tgvmax = MaxFinderAPI()

tgvmax.setLimite(1)
tgvmax.setOrigemBusca("grenoble")
tgvmax.requestResponse()
tgvmax.printResponse()
print(tgvmax.getParams()) """