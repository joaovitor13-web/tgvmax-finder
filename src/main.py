# src/main.py
import customtkinter as ctk # Embora não usado diretamente aqui, é bom ter se App precisar de ctk
from src.gui.main_window import App
import logging
import sys
import os

# Definir um User-Agent pode ser útil para APIs web, embora não usado por 'requests' por padrão
# HEADERS = {'User-Agent': 'TGVMaxFinderApp/1.0 (Python; Windows/Linux/Mac)'}


def setup_logging():
    log_format = "%(asctime)s - %(levelname)s - [%(name)s:%(module)s:%(lineno)d] - %(message)s"
    # Configuração básica para stdout
    logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stdout) # Mudar para DEBUG para mais detalhes
    
    # Opcional: Configurar logging para arquivo também
    try:
        # Tenta salvar logs na pasta de dados do usuário, se não, na pasta do projeto.
        app_data_path = os.getenv('APPDATA') or os.getenv('LOCALAPPDATA')
        log_dir_base = None
        if app_data_path: # Windows
            log_dir_base = os.path.join(app_data_path, "TGVMaxFinder", "logs")
        else: # Linux/macOS (fallback)
            home = os.path.expanduser("~")
            log_dir_base = os.path.join(home, ".local", "share", "TGVMaxFinder", "logs")
        
        if log_dir_base:
            if not os.path.exists(log_dir_base):
                os.makedirs(log_dir_base, exist_ok=True)
            log_file_path = os.path.join(log_dir_base, "app.log")
            
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8', mode='a') # 'a' para append
            file_handler.setFormatter(logging.Formatter(log_format))
            file_handler.setLevel(logging.DEBUG) # Captura logs DEBUG e acima para o arquivo
            logging.getLogger().addHandler(file_handler)
            logging.info(f"Logging para arquivo configurado em: {log_file_path}")
        else:
            logging.warning("Não foi possível determinar o diretório de logs da aplicação. Logs de arquivo desabilitados.")

    except Exception as e:
        logging.error(f"Erro ao configurar logging para arquivo: {e}", exc_info=True)


def main():
    setup_logging()
    main_logger = logging.getLogger(__name__)
    main_logger.info("Iniciando aplicação TGV Max Finder Avançado...")
    main_logger.info(f"Executando em: {sys.platform}, Python: {sys.version.split()[0]}")


    # Para garantir que a pasta do histórico exista (movido para search_history.py)
    # if not os.path.exists(os.path.dirname(settings.HISTORY_FILE_PATH)):
    #     try:
    #         os.makedirs(os.path.dirname(settings.HISTORY_FILE_PATH), exist_ok=True)
    #         main_logger.info(f"Diretório de histórico criado: {os.path.dirname(settings.HISTORY_FILE_PATH)}")
    #     except OSError as e:
    #         main_logger.error(f"Erro ao criar diretório para o arquivo de histórico: {e}")

    app = App()
    app.mainloop()
    main_logger.info("Aplicação TGV Max Finder Avançado finalizada.")

if __name__ == "__main__":
    main()