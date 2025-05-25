# src/config/settings.py

# API SNCF Open Data
SNCF_API_BASE_URL = "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/"
TGVMAX_AVAILABILITY_DATASET = "disponibilite-a-30-jours-de-places-max-jeune-et-max-senior-ouvertes-a-la-reservation"
RECORDS_ENDPOINT = "records"
DEFAULT_API_LIMIT = 100
MAX_API_LIMIT_PER_CALL = 1000 # Limite por chamada para O-D, pode ser ajustado

# Nomes dos campos da API (verificar e ajustar conforme a API)
# Estes são baseados na exploração do dataset:
# https://ressources.data.sncf.com/explore/dataset/disponibilite-a-30-jours-de-places-max-jeune-et-max-senior-ouvertes-a-la-reservation/information/
API_FIELD_ORIGIN_AGG = "origine" # Campo de cidade agregada (ex: "PARIS")
API_FIELD_DESTINATION_AGG = "destination" # Campo de cidade agregada (ex: "LYON")
API_FIELD_DEPARTURE_DATETIME = "date_heure_depart_iso" # Formato ISO 8601 UTC
API_FIELD_ARRIVAL_DATETIME = "date_heure_arrivee_iso" # Formato ISO 8601 UTC
API_FIELD_MAX_JEUNE_AVAILABLE = "max_jeune_accessible" # Booleano
API_FIELD_MAX_SENIOR_AVAILABLE = "max_senior_accessible" # Booleano
API_FIELD_PLACES_MAX_JEUNE = "nb_max_jeune_accessible" # Número de lugares
API_FIELD_PLACES_MAX_SENIOR = "nb_max_senior_accessible" # Número de lugares
# API_FIELD_TRAIN_NUMBER = "num_train" # Verificar se este campo existe e o nome correto (não parece estar neste dataset específico)

# Histórico de Pesquisa
SEARCH_HISTORY_FILE = "search_history.json" # Salvo na pasta raiz do projeto ou em AppData
MAX_SEARCH_HISTORY_ITEMS = 10

# Lógica de Conexões
# Lista de cidades HUB principais para tentar conexões.
# Use nomes agregados como na API (ex: "PARIS", "LYON", "LILLE", "MARSEILLE", "BORDEAUX", "STRASBOURG", "NANTES", "RENNES", "MONTPELLIER", "TOULOUSE", "AVIGNON")
DEFAULT_HUB_CITIES = ["LYON", "LILLE", "MARSEILLE", "BORDEAUX", "STRASBOURG", "AVIGNON", "NANTES", "RENNES", "MONTPELLIER", "TOULOUSE", "MASSY TGV", "AEROPORT CDG2 TGV"]
MIN_TRANSFER_TIME_MINUTES = 30 # Tempo mínimo para uma conexão em minutos
MAX_TRANSFER_TIME_MINUTES = 240 # Tempo máximo para uma conexão (4 horas)