# Max-Finder/main.py

import sys
from PySide6.QtWidgets import QApplication

# Importe suas classes personalizadas
from maxfinder_app.api_handler import MaxFinderAPI 
from maxfinder_app.gui.main_window import MaxFinderWindow

if __name__ == "__main__":
    # 1. Cria a instância da aplicação Qt
    app = QApplication(sys.argv)

    # 2. Cria uma instância do seu manipulador de API
    api_client = MaxFinderAPI() 

    # 3. Cria uma instância da sua janela principal, passando o api_client
    window = MaxFinderWindow(api_client=api_client)

    # 4. Exibe a janela
    window.show()

    # 5. Inicia o loop de eventos da aplicação
    #    A execução do script Python ficará aqui até a janela ser fechada.
    sys.exit(app.exec())