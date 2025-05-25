# src/models/journey_models.py
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List

@dataclass
class Leg:
    """Representa um trecho individual de uma viagem de trem."""
    origin_station: str # Idealmente o nome da estação específica se disponível, senão a cidade agregada
    destination_station: str # Idealmente o nome da estação específica
    departure_time: datetime
    arrival_time: datetime
    train_number: Optional[str] = None # Se disponível na API
    is_max_jeune: bool = False
    is_max_senior: bool = False
    places_max_jeune: Optional[int] = None # Número de lugares
    places_max_senior: Optional[int] = None # Número de lugares
    api_record: dict = field(default_factory=dict, repr=False) # Opcional: para guardar o registro original da API, não mostrar no repr

    @property
    def duration(self) -> timedelta:
        return self.arrival_time - self.departure_time

@dataclass
class Journey:
    """Representa uma viagem completa, possivelmente com múltiplas pernas (conexões)."""
    legs: List[Leg] = field(default_factory=list)

    @property
    def overall_origin(self) -> Optional[str]:
        return self.legs[0].origin_station if self.legs else None

    @property
    def overall_destination(self) -> Optional[str]:
        return self.legs[-1].destination_station if self.legs else None

    @property
    def overall_departure_time(self) -> Optional[datetime]:
        return self.legs[0].departure_time if self.legs else None

    @property
    def overall_arrival_time(self) -> Optional[datetime]:
        return self.legs[-1].arrival_time if self.legs else None
    
    @property
    def number_of_connections(self) -> int:
        return max(0, len(self.legs) - 1)

    @property
    def total_duration(self) -> Optional[timedelta]:
        if not self.legs:
            return None
        # Considera apenas o tempo em trânsito e não o tempo de espera nas conexões para esta propriedade
        # Se quiser incluir o tempo total da primeira partida à última chegada:
        if self.overall_arrival_time and self.overall_departure_time:
             return self.overall_arrival_time - self.overall_departure_time
        return None

@dataclass
class SearchQuery:
    """Representa os parâmetros de uma pesquisa feita pelo usuário."""
    origin: str
    destination: str
    max_connections: int # 0 para direto, 1 para uma conexão, etc.
    # departure_date: Optional[str] = None # Formato YYYY-MM-DD, para futuras implementações
    search_timestamp: datetime = field(default_factory=datetime.now)

    def __eq__(self, other): # Para evitar duplicatas exatas no histórico
        if not isinstance(other, SearchQuery):
            return NotImplemented
        return (self.origin.upper() == other.origin.upper() and
                self.destination.upper() == other.destination.upper() and
                self.max_connections == other.max_connections)
                # self.departure_date == other.departure_date) # Adicionar se implementar filtro de data

    def __hash__(self): # Necessário se __eq__ é implementado e queremos usar em sets
        return hash((self.origin.upper(), self.destination.upper(), self.max_connections)) # self.departure_date))