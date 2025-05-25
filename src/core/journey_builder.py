# src/core/journey_builder.py
import logging
from typing import List, Optional, Dict, Tuple
from datetime import timedelta, datetime
from src.models.journey_models import Journey, Leg, SearchQuery
from src.api import sncf_api
from src.config import settings

logger = logging.getLogger(__name__)

# Cache de segmentos simples para a duração de uma chamada a find_journeys
# Chave: (origin_city_upper, destination_city_upper, departure_date_str_or_None)
# Valor: List[Leg]
_segment_cache: Dict[Tuple[str, str, Optional[str]], List[Leg]] = {}

def _get_segments_from_api_or_cache(origin: str, destination: str, date_str: Optional[str]) -> List[Leg]:
    cache_key = (origin.upper(), destination.upper(), date_str)
    if cache_key in _segment_cache:
        logger.debug(f"Cache HIT for segments: {origin}->{destination} on {date_str}")
        return _segment_cache[cache_key]
    
    logger.debug(f"Cache MISS for segments: {origin}->{destination} on {date_str}. Fetching from API.")
    segments = sncf_api.fetch_tgvmax_segments(origin, destination, date_str)
    _segment_cache[cache_key] = segments
    return segments

def find_journeys(query: SearchQuery) -> List[Journey]:
    """
    Encontra viagens (diretas ou com conexões) com base nos critérios da pesquisa.
    """
    _segment_cache.clear() # Limpar cache no início de cada nova busca principal
    journeys: List[Journey] = []
    origin = query.origin.upper()
    destination = query.destination.upper()
    # departure_date = query.departure_date # Usar se/quando implementado

    # 1. Viagens Diretas (0 conexões)
    logger.info(f"Buscando viagens diretas para {origin} -> {destination}")
    # direct_legs = sncf_api.fetch_tgvmax_segments(origin, destination, departure_date)
    direct_legs = _get_segments_from_api_or_cache(origin, destination, None) # Passar departure_date aqui se for usar
    for leg in direct_legs:
        journeys.append(Journey(legs=[leg]))
    logger.info(f"Encontradas {len(direct_legs)} viagens diretas.")

    # 2. Viagens com 1 Conexão (se solicitado e max_connections >= 1)
    if query.max_connections >= 1:
        logger.info(f"Buscando viagens com 1 conexão para {origin} -> {destination}")
        possible_hubs = [h.upper() for h in settings.DEFAULT_HUB_CITIES if h.upper() not in [origin, destination]]
        
        min_transfer_td = timedelta(minutes=settings.MIN_TRANSFER_TIME_MINUTES)
        max_transfer_td = timedelta(minutes=settings.MAX_TRANSFER_TIME_MINUTES)

        for hub_city in possible_hubs:
            logger.debug(f"Tentando hub: {hub_city} para {origin} -> {hub_city} -> {destination}")
            
            # legs_origin_to_hub = sncf_api.fetch_tgvmax_segments(origin, hub_city, departure_date)
            legs_origin_to_hub = _get_segments_from_api_or_cache(origin, hub_city, None) # Passar departure_date
            if not legs_origin_to_hub:
                logger.debug(f"Nenhum trecho encontrado para {origin} -> {hub_city}")
                continue

            # legs_hub_to_destination = sncf_api.fetch_tgvmax_segments(hub_city, destination, departure_date)
            legs_hub_to_destination = _get_segments_from_api_or_cache(hub_city, destination, None) # Passar departure_date
            if not legs_hub_to_destination:
                logger.debug(f"Nenhum trecho encontrado para {hub_city} -> {destination}")
                continue
            
            logger.debug(f"Para hub {hub_city}: {len(legs_origin_to_hub)} trechos O->H, {len(legs_hub_to_destination)} trechos H->D")

            for leg1 in legs_origin_to_hub:
                # Se departure_date foi especificado, e leg1 já passou dessa data, não faz sentido continuar com este leg1
                # (Esta verificação pode ser mais complexa dependendo da flexibilidade de datas)

                for leg2 in legs_hub_to_destination:
                    # Garantir que o segundo trecho não comece antes ou no mesmo dia do primeiro, se houver filtro de data
                    # if departure_date and leg2.departure_time.date() < leg1.departure_time.date():
                    #    continue
                    
                    transfer_duration = leg2.departure_time - leg1.arrival_time
                    if min_transfer_td <= transfer_duration <= max_transfer_td:
                        # Se houver filtro de data, garantir que a viagem toda ainda faz sentido para a data
                        # ex: se a conexão joga para o dia seguinte, isso é aceitável?
                        journeys.append(Journey(legs=[leg1, leg2]))
                        logger.debug(f"Conexão válida encontrada: {leg1.destination_station} ({format_timedelta(transfer_duration)}) para {leg2.origin_station}")
        
    # TODO: Implementar lógica para 2+ conexões se query.max_connections >= 2.
    # Isso exigiria uma abordagem recursiva ou iterativa mais complexa,
    # potencialmente com busca em largura (BFS) ou profundidade (DFS) no grafo de conexões.

    # Ordenar jornadas (ex: pela hora de partida geral, depois por número de conexões)
    journeys.sort(key=lambda j: (j.overall_departure_time if j.overall_departure_time else datetime.max, j.number_of_connections))
    
    _segment_cache.clear() # Limpar cache após a busca principal ser concluída
    logger.info(f"Total de {len(journeys)} viagens encontradas e processadas.")
    return journeys