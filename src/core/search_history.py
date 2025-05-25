# src/core/search_history.py
import json
import os
import logging
from typing import List
from src.models.journey_models import SearchQuery
from src.config import settings
from datetime import datetime

logger = logging.getLogger(__name__)

# Determinar o caminho do arquivo de histórico
# Tenta salvar na pasta de dados do usuário, se não, na pasta do projeto.
try:
    app_data_path = os.getenv('APPDATA') or os.getenv('LOCALAPPDATA')
    if app_data_path: # Windows
        HISTORY_DIR = os.path.join(app_data_path, "TGVMaxFinder")
    else: # Linux/macOS (fallback)
        home = os.path.expanduser("~")
        HISTORY_DIR = os.path.join(home, ".local", "share", "TGVMaxFinder")
    
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR, exist_ok=True)
    HISTORY_FILE_PATH = os.path.join(HISTORY_DIR, settings.SEARCH_HISTORY_FILE)
except Exception as e:
    logger.warning(f"Não foi possível criar/acessar diretório de histórico em AppData/local. Usando diretório do projeto. Erro: {e}")
    HISTORY_FILE_PATH = os.path.join(os.getcwd(), settings.SEARCH_HISTORY_FILE)


def load_history() -> List[SearchQuery]:
    """Carrega o histórico de pesquisas do arquivo JSON."""
    if not os.path.exists(HISTORY_FILE_PATH):
        logger.info(f"Arquivo de histórico não encontrado em {HISTORY_FILE_PATH}. Retornando lista vazia.")
        return []
    try:
        with open(HISTORY_FILE_PATH, "r", encoding="utf-8") as f:
            history_data = json.load(f)
            history = []
            for item in history_data:
                try:
                    # Lidar com o timestamp que é salvo como string ISO
                    item['search_timestamp'] = datetime.fromisoformat(item['search_timestamp'])
                    # Remover 'departure_date' se não estiver presente no item para compatibilidade com versões antigas
                    # item.pop('departure_date', None) # Se 'departure_date' for opcional
                    history.append(SearchQuery(**item))
                except TypeError as te: # Captura erro se faltar algum campo no JSON vs. dataclass
                     logger.warning(f"Item de histórico malformado ou incompatível: {item}. Erro: {te}")
                except ValueError as ve: # Captura erro de data
                     logger.warning(f"Erro ao parsear data no histórico: {item}. Erro: {ve}")

            logger.info(f"Histórico carregado de {HISTORY_FILE_PATH} com {len(history)} itens válidos.")
            return history
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Erro ao carregar ou decodificar o histórico de {HISTORY_FILE_PATH}: {e}")
        return []

def save_history(history: List[SearchQuery]):
    """Salva o histórico de pesquisas em um arquivo JSON."""
    try:
        history_data = []
        for query in history:
            query_dict = {
                "origin": query.origin,
                "destination": query.destination,
                "max_connections": query.max_connections,
                # "departure_date": query.departure_date, # Adicionar se implementar
                "search_timestamp": query.search_timestamp.isoformat()
            }
            history_data.append(query_dict)
        
        # Garante que o diretório de histórico existe antes de salvar
        history_dir_for_file = os.path.dirname(HISTORY_FILE_PATH)
        if not os.path.exists(history_dir_for_file):
            os.makedirs(history_dir_for_file, exist_ok=True)
            logger.info(f"Diretório de histórico criado: {history_dir_for_file}")

        with open(HISTORY_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=4, ensure_ascii=False)
        logger.info(f"Histórico salvo em {HISTORY_FILE_PATH} com {len(history_data)} itens.")
    except IOError as e:
        logger.error(f"Erro ao salvar o histórico em {HISTORY_FILE_PATH}: {e}")
    except Exception as e_gen:
        logger.error(f"Erro inesperado ao salvar o histórico: {e_gen}", exc_info=True)


def add_to_history(query: SearchQuery, current_history: List[SearchQuery]) -> List[SearchQuery]:
    """Adiciona uma nova pesquisa ao histórico, evitando duplicatas exatas e respeitando o limite."""
    temp_history = [item for item in current_history if item != query] # Usa __eq__ da dataclass
    
    updated_history = [query] + temp_history # Adiciona no início
    
    if len(updated_history) > settings.MAX_SEARCH_HISTORY_ITEMS:
        updated_history = updated_history[:settings.MAX_SEARCH_HISTORY_ITEMS]
    
    logger.debug(f"Histórico atualizado. Nova query: {query}. Tamanho: {len(updated_history)}")
    return updated_history