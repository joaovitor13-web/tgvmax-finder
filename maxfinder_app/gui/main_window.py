# maxfinder_app/gui/main_window.py
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QDateEdit, QTextEdit, QSpinBox) # Adicionado QSpinBox e QHBoxLayout
from PySide6.QtCore import QDate, Qt # Adicionado Qt

class MaxFinderWindow(QMainWindow):
    def __init__(self, api_client):
        super().__init__()

        self.setWindowTitle("Max Finder - Buscador TGV Max")
        self.setGeometry(100, 100, 850, 700) # Aumentei um pouco o tamanho

        self.api_client = api_client

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Seção de Busca ---
        # Usaremos um layout de formulário ou grid para melhor alinhamento
        search_form_layout = QVBoxLayout() # Poderia ser QFormLayout ou QGridLayout

        # Origem
        origem_layout = QHBoxLayout()
        origem_layout.addWidget(QLabel("Origem:"))
        self.origem_input = QLineEdit()
        self.origem_input.setPlaceholderText("Ex: PARIS (intramuros) ou parte do nome")
        origem_layout.addWidget(self.origem_input)
        search_form_layout.addLayout(origem_layout)

        # Destino
        destino_layout = QHBoxLayout()
        destino_layout.addWidget(QLabel("Destino:"))
        self.destino_input = QLineEdit()
        self.destino_input.setPlaceholderText("Ex: LYON (intramuros) ou parte do nome")
        destino_layout.addWidget(self.destino_input)
        search_form_layout.addLayout(destino_layout)

        # Data e Limite na mesma linha
        date_limit_layout = QHBoxLayout()
        
        date_limit_layout.addWidget(QLabel("Data da Viagem:"))
        self.data_input = QDateEdit()
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setCalendarPopup(True)
        self.data_input.setDisplayFormat("yyyy/MM/dd") # Formato visual na UI
        date_limit_layout.addWidget(self.data_input)
        
        date_limit_layout.addSpacing(20) # Espaço entre data e limite
        
        date_limit_layout.addWidget(QLabel("Limite de Resultados:"))
        self.limite_input = QSpinBox()
        self.limite_input.setMinimum(1)
        self.limite_input.setMaximum(50) # Um limite máximo razoável
        self.limite_input.setValue(self.api_client.limite) # Pega o valor padrão do api_client
        date_limit_layout.addWidget(self.limite_input)
        date_limit_layout.addStretch() # Empurra para a esquerda

        search_form_layout.addLayout(date_limit_layout)
        
        self.buscar_button = QPushButton("Buscar Viagens TGV Max")
        self.buscar_button.setStyleSheet("QPushButton { padding: 10px; font-size: 16px; }") # Estilo básico
        self.buscar_button.clicked.connect(self.realizar_busca)
        search_form_layout.addWidget(self.buscar_button, alignment=Qt.AlignCenter) # Centralizar botão
        
        main_layout.addLayout(search_form_layout)

        # --- Seção de Resultados ---
        self.resultados_output = QTextEdit()
        self.resultados_output.setReadOnly(True)
        self.resultados_output.setFontPointSize(10) # Tamanho de fonte um pouco maior para resultados
        main_layout.addWidget(QLabel("Resultados:"))
        main_layout.addWidget(self.resultados_output, stretch=1) # Faz com que o QTextEdit ocupe mais espaço vertical

        # --- Barra de Status ---
        self.statusBar().showMessage("Pronto para buscar.")

    def realizar_busca(self):
        origem = self.origem_input.text().strip()
        destino = self.destino_input.text().strip()
        
        # O formato da data para a API deve ser AAAA/MM/DD, como já está no displayFormat
        data_str = self.data_input.date().toString("yyyy/MM/dd") 
        limite = self.limite_input.value()

        self.statusBar().showMessage(f"Buscando de '{origem}' para '{destino}' em {data_str} (limite: {limite})...")
        self.resultados_output.setText(f"Buscando de '{origem}' para '{destino}' em {data_str} (limite: {limite})...\n")
        QApplication.processEvents() # Força a UI a atualizar antes da chamada da API

        # Usando os métodos da sua classe MaxFinderAPI
        self.api_client.setOrigemBusca(origem if origem else None) # Envia None se vazio
        self.api_client.setDestinoBusca(destino if destino else None)
        #self.api_client.setDataBusca(data_str if data_str else None) # A API deve tratar se a data é obrigatória ou não
        self.api_client.setLimite(limite)
        
        self.api_client.requestResponse() # Chama o método que faz a requisição e armazena em self.data_response_json
        
        resultados_json = self.api_client.data_response_json # Pega o resultado do atributo

        if resultados_json and "results" in resultados_json:
            if resultados_json["results"]:
                num_viagens = len(resultados_json['results'])
                self.resultados_output.append(f"\n{num_viagens} viagens encontradas:\n" + "="*30 + "\n")
                for i, trem in enumerate(resultados_json["results"]):
                    date = trem.get('date', 'N/A')
                    train_no = trem.get('train_no', 'N/A')
                    axe = trem.get('axe', 'N/A')
                    origine = trem.get('origine', 'N/A')
                    destination = trem.get('destination', 'N/A')
                    heure_depart = trem.get('heure_depart', 'N/A')
                    heure_arrivee = trem.get('heure_arrivee', 'N/A')
                    od_happy = trem.get('od_happy_card', 'N/A') # Para verificar o campo que você usou

                    self.resultados_output.append(
                        f"{i+1}. De: {origine}\n"
                        f"   Para: {destination}\n"
                        f"   Data: {date}\n"
                        f"   Horário partida: {heure_depart}\n"
                        f"   Horário chegada: {heure_arrivee}\n"
                        f"   Trem Nº: {train_no}\n"
                        f"   Eixo : {axe}\n"
                        f"   TGVMax : {od_happy}\n"
                        f"---"
                    )
                self.statusBar().showMessage(f"{num_viagens} viagens encontradas.")
            else:
                self.resultados_output.append("\nNenhuma viagem encontrada para os critérios informados.")
                self.statusBar().showMessage("Nenhuma viagem encontrada.")
        else:
            self.resultados_output.append("\nErro ao buscar viagens ou resposta inesperada da API.")
            self.statusBar().showMessage("Erro na busca. Verifique o console para detalhes da API.")
            if self.api_client.last_URL: # Usando last_URL conforme definido na sua API
                print(f"DEBUG (main_window): Última URL tentada: {self.api_client.last_URL}")
                self.resultados_output.append(f"\nÚltima URL tentada: {self.api_client.last_URL}")
            if self.api_client.data_response_json is not None: # Se houve resposta mas não era o esperado
                 self.resultados_output.append(f"\nResposta bruta da API (verifique se houve erro no formato):\n{json.dumps(self.api_client.data_response_json, indent=2)}")
