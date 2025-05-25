# src/api/sncf_api.py
import requests
from src.config import settings
from src.models.journey_models import Leg
from datetime import datetime
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

def parse_datetime_from_api(datetime_str: Optional[str]) -> Optional[datetime]:
    if not datetime_str:
        return None
    try:
        # A API retorna strings como "2024-05-25T10:00:00Z"
        # O 'Z' (Zulu time) indica UTC. fromisoformat lida com isso.
        # Python 3.7+ lida com 'Z' diretamente em fromisoformat.
        # Para maior robustez se 'Z' não for tratado (improvável com Python moderno):
        # if datetime_str.endswith("Z"):
        #      dt_obj = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        # else:
        dt_obj = datetime.fromisoformat(datetime_str)
        return dt_obj
    except ValueError as e:
        logger.warning(f"Could not parse datetime string: {datetime_str}. Error: {e}")
        return None

def fetch_tgvmax_segments(origin_city: str, destination_city: str, departure_date_str: Optional[str] = None) -> List[Leg]:
    """
    Busca segmentos de TGV Max disponíveis para um par Origem-Destino específico.
    Filtra por disponibilidade MAX Jeune ou MAX Senior.

    Args:
        origin_city (str): Nome da cidade de origem (ex: "PARIS").
        destination_city (str): Nome da cidade de destino (ex: "LYON").
        departure_date_str (Optional[str]): Data de partida no formato "YYYY-MM-DD" para filtrar. (Não implementado na query da API ainda)

    Returns:
        List[Leg]: Uma lista de objetos Leg representando segmentos de trem disponíveis.
                   Retorna lista vazia em caso de erro ou se nada for encontrado.
    """
    base_url = f"{settings.SNCF_API_BASE_URL}{settings.TGVMAX_AVAILABILITY_DATASET}/{settings.RECORDS_ENDPOINT}"
    
    params = {
        "limit": settings.MAX_API_LIMIT_PER_CALL,
        "refine": [
            f"{settings.API_FIELD_ORIGIN_AGG}:{origin_city.upper()}",
            f"{settings.API_FIELD_DESTINATION_AGG}:{destination_city.upper()}"
        ],
        "where": f"({settings.API_FIELD_MAX_JEUNE_AVAILABLE}=true OR {settings.API_FIELD_MAX_SENIOR_AVAILABLE}=true)",
        "timezone": "Europe/Paris", # Para consistência, embora as datas ISO já sejam UTC
        "order_by": f"{settings.API_FIELD_DEPARTURE_DATETIME} ASC" # Ordenar pela data de partida
    }

    # Lógica para filtro de data (se departure_date_str for fornecido)
    # A API Explore da SNCF permite filtros no campo 'where' para datas.
    # Ex: "date_field >= date'YYYY-MM-DD' AND date_field < date'YYYY-MM-(DD+1)'"
    if departure_date_str:
        # Esta é uma forma de filtrar. A API pode ter sintaxe específica.
        # params["where"] += f" AND date_trunc('day', {settings.API_FIELD_DEPARTURE_DATETIME}) = date'{departure_date_str}'"
        # Por enquanto, a busca por data específica não está ativada na query para simplificar.
        # A filtragem de data pode ser feita após receber os resultados, se necessário.
        logger.info(f"Busca para {origin_city}->{destination_city}. Filtro de data {departure_date_str} não aplicado na query da API nesta versão.")
        pass


    parsed_legs: List[Leg] = []
    try:
        logger.info(f"Fetching TGV Max segments for {origin_city.upper()} -> {destination_city.upper()} with params: {params}")
        response = requests.get(base_url, params=params, timeout=30) # Timeout aumentado
        response.raise_for_status()
        data = response.json()
        records = data.get("results", [])
        
        for record in records:
            dep_time = parse_datetime_from_api(record.get(settings.API_FIELD_DEPARTURE_DATETIME))
            arr_time = parse_datetime_from_api(record.get(settings.API_FIELD_ARRIVAL_DATETIME))

            if not dep_time or not arr_time:
                logger.warning(f"Skipping record due to invalid date/time: {record}")
                continue
            
            # Se houver um filtro de data, aplicar aqui se não foi feito na API
            if departure_date_str:
                target_date = datetime.strptime(departure_date_str, "%Y-%m-%d").date()
                if dep_time.date() != target_date:
                    continue # Pula registros que não são da data desejada

            parsed_legs.append(
                Leg(
                    origin_station=record.get(settings.API_FIELD_ORIGIN_AGG, "N/A"),
                    destination_station=record.get(settings.API_FIELD_DESTINATION_AGG, "N/A"),
                    departure_time=dep_time,
                    arrival_time=arr_time,
                    is_max_jeune=record.get(settings.API_FIELD_MAX_JEUNE_AVAILABLE, False),
                    is_max_senior=record.get(settings.API_FIELD_MAX_SENIOR_AVAILABLE, False),
                    places_max_jeune=record.get(settings.API_FIELD_PLACES_MAX_JEUNE),
                    places_max_senior=record.get(settings.API_FIELD_PLACES_MAX_SENIOR),
                    api_record=record
                )
            )
        logger.info(f"Fetched and parsed {len(parsed_legs)} segments for {origin_city.upper()} -> {destination_city.upper()}")
        return parsed_legs

    except requests.exceptions.Timeout:
        logger.error(f"API Timeout fetching data for {origin_city.upper()}->{destination_city.upper()}")
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request Error fetching data for {origin_city.upper()}->{destination_city.upper()}: {e}")
    except ValueError as e: # Para JSONDecodeError
        logger.error(f"API JSON Decode Error for {origin_city.upper()}->{destination_city.upper()}: {e}")
    return []