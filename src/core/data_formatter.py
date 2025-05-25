# src/core/data_formatter.py
import logging
from src.models.journey_models import Journey, Leg
from datetime import timedelta, datetime
from typing import Optional

logger = logging.getLogger(__name__)

def format_timedelta(td: Optional[timedelta]) -> str:
    if td is None:
        return "N/A"
    total_seconds = int(td.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0: # Mostrar horas se houver dias, mesmo que seja 0h
        parts.append(f"{hours}h")
    parts.append(f"{minutes:02d}m")
    return " ".join(parts) if parts else "0m"


def format_datetime_for_display(dt: Optional[datetime]) -> str:
    if dt is None:
        return "N/A"
    # Converte para o fuso horário local se a informação de fuso estiver presente
    # e se for diferente do local. Por enquanto, apenas formata.
    # Se a data da API é UTC (como indicado por 'Z'), e queremos mostrar em hora local:
    # dt_local = dt.astimezone(None) # Converte para fuso local do sistema
    # return dt_local.strftime('%d/%m %H:%M')
    return dt.strftime('%d/%m %H:%M') # Mantém UTC ou fuso original por enquanto


def format_leg_details(leg: Leg) -> str:
    departure_time_str = format_datetime_for_display(leg.departure_time)
    arrival_time_str = format_datetime_for_display(leg.arrival_time)
    duration_str = format_timedelta(leg.duration)
    
    max_info_parts = []
    if leg.is_max_jeune:
        max_info_parts.append(f"MAX Jeune ({leg.places_max_jeune if leg.places_max_jeune is not None else '?'})")
    if leg.is_max_senior:
        max_info_parts.append(f"MAX Senior ({leg.places_max_senior if leg.places_max_senior is not None else '?'})")
    
    max_str = " & ".join(max_info_parts) if max_info_parts else "Nenhum MAX"
    if not leg.is_max_jeune and not leg.is_max_senior: # Se por acaso um trecho sem MAX for incluído
        max_str = "Disponibilidade MAX não confirmada"


    return (
        f"    De: {leg.origin_station} ({departure_time_str})\n"
        f"    Para: {leg.destination_station} ({arrival_time_str})\n"
        f"    Duração Trecho: {duration_str} | {max_str}"
    )

def format_journey_for_display(journey: Journey) -> str:
    if not journey.legs:
        return "Viagem inválida ou vazia."

    header = (
        f"Origem: {journey.overall_origin} | Destino: {journey.overall_destination}\n"
        f"Partida Geral: {format_datetime_for_display(journey.overall_departure_time)}\n"
        f"Chegada Geral: {format_datetime_for_display(journey.overall_arrival_time)}\n"
        f"Duração Total Viagem: {format_timedelta(journey.total_duration)}\n"
        f"Conexões: {journey.number_of_connections}\n"
    )
    
    legs_details_parts = []
    for i, leg in enumerate(journey.legs):
        legs_details_parts.append(f"  Trecho {i+1}:\n{format_leg_details(leg)}")
        if i < len(journey.legs) - 1: # Se não for o último trecho, mostrar tempo de conexão
            connection_station = leg.destination_station # Estação de conexão
            wait_time = journey.legs[i+1].departure_time - leg.arrival_time
            legs_details_parts.append(f"    -> Conexão em: {connection_station} (Espera: {format_timedelta(wait_time)})")
    
    return header + "\n".join(legs_details_parts) + "\n" + "-"*60