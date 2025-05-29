# maxfinder_app/gui/main_window.py
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QDateEdit, QSpinBox, QTableWidget, QTableWidgetItem,
                               QHeaderView, QCheckBox) # Adicionado QCheckBox
from PySide6.QtCore import QDate, Qt
import json
from datetime import datetime

class MaxFinderWindow(QMainWindow):
    def __init__(self, api_client):
        super().__init__()

        self.setWindowTitle("Max Finder - Buscador TGV Max")
        self.setGeometry(100, 100, 950, 700)

        self.api_client = api_client
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        search_form_layout = QVBoxLayout()

        # Origem e Destino (semelhante ao anterior)
        origem_layout = QHBoxLayout()
        origem_layout.addWidget(QLabel("Origem:"))
        self.origem_input = QLineEdit()
        self.origem_input.setPlaceholderText("Ex: PARIS (intramuros)")
        origem_layout.addWidget(self.origem_input)
        search_form_layout.addLayout(origem_layout)

        destino_layout = QHBoxLayout()
        destino_layout.addWidget(QLabel("Destino:"))
        self.destino_input = QLineEdit()
        self.destino_input.setPlaceholderText("Ex: LYON (intramuros)")
        destino_layout.addWidget(self.destino_input)
        search_form_layout.addLayout(destino_layout)

        # Layout para CheckBox de Data e QDateEdit
        date_filter_layout = QHBoxLayout()
        self.date_filter_checkbox = QCheckBox("Filtrar por data específica?")
        self.date_filter_checkbox.setChecked(True) # Começa marcado por padrão
        self.date_filter_checkbox.stateChanged.connect(self.toggle_date_input)
        date_filter_layout.addWidget(self.date_filter_checkbox)

        self.data_input = QDateEdit()
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setCalendarPopup(True)
        self.data_input.setDisplayFormat("yyyy/MM/dd")
        # self.data_input.setEnabled(self.date_filter_checkbox.isChecked()) # Estado inicial
        date_filter_layout.addWidget(self.data_input)
        date_filter_layout.addStretch() # Empurra o QDateEdit para perto do checkbox
        search_form_layout.addLayout(date_filter_layout)
        self.toggle_date_input() # Define o estado inicial do QDateEdit

        # Limite de Resultados
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("Limite de Resultados:"))
        self.limite_input = QSpinBox()
        self.limite_input.setMinimum(1)
        self.limite_input.setMaximum(100)
        self.limite_input.setValue(self.api_client.limite) # Pega o valor padrão do api_client
        limit_layout.addWidget(self.limite_input)
        limit_layout.addStretch() # Empurra para a esquerda
        search_form_layout.addLayout(limit_layout)
        
        self.buscar_button = QPushButton("Buscar Viagens TGV Max")
        self.buscar_button.setStyleSheet("QPushButton { padding: 10px; font-size: 16px; }")
        self.buscar_button.clicked.connect(self.realizar_busca)
        search_form_layout.addWidget(self.buscar_button, alignment=Qt.AlignCenter)
        main_layout.addLayout(search_form_layout)

        # --- Seção de Resultados com QTableWidget ---
        main_layout.addWidget(QLabel("Resultados:"))
        self.resultados_table = QTableWidget()
        self.resultados_table.setColumnCount(7)
        self.resultados_table.setHorizontalHeaderLabels([
            "Data", "Origem", "Destino", "Horário de partida", "Horário de chegada", "Trem Nº", "TGV Max disponível"
        ])
        self.resultados_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.resultados_table.setAlternatingRowColors(True)
        self.resultados_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.resultados_table, stretch=1)

        self.statusBar().showMessage("Pronto para buscar.")

    def formatar_data(self, data_str):
        """
        Converte uma string de data do formato 'AAAA-MM-DD' 
        para um formato mais legível: 'DD nome_mes_abrev AAAA'.
        Exemplo: '2025-05-29' se torna '29 mai 2025'.
        """
        if not data_str:
            return "Data não fornecida"

        try:
            # 1. Analisar a string de data de entrada (AAAA-MM-DD)
            objeto_data = datetime.strptime(data_str, "%Y-%m-%d")

            # 2. Mapeamento dos números dos meses para suas abreviações em português
            meses_pt_abrev = {
                1: "jan", 2: "fev", 3: "mar", 4: "abr", 5: "mai", 6: "jun",
                7: "jul", 8: "ago", 9: "set", 10: "out", 11: "nov", 12: "dez"
            }

            # 3. Obter os componentes da data
            dia = objeto_data.day
            mes_numero = objeto_data.month
            ano = objeto_data.year

            # 4. Formatar a string de saída
            data_formatada = f"{dia} {meses_pt_abrev[mes_numero]} {ano}"
            
            return data_formatada
            
        except ValueError:
            # Se a string de data de entrada não estiver no formato correto
            print(f"Aviso: Formato de data inválido recebido: {data_str}")
            return data_str # Retorna a string original ou uma mensagem de erro
        
    
    def toggle_date_input(self):
        """Habilita ou desabilita o QDateEdit com base no checkbox."""
        is_checked = self.date_filter_checkbox.isChecked()
        self.data_input.setEnabled(is_checked)
        if not is_checked:
            self.data_input.setStyleSheet("background-color: #f0f0f0;") # Visualmente desabilitado
        else:
            self.data_input.setStyleSheet("") # Estilo padrão


    def _clear_resultados_table(self):
        self.resultados_table.setRowCount(0)

    def realizar_busca(self):
        origem = self.origem_input.text().strip()
        destino = self.destino_input.text().strip()
        limite = self.limite_input.value()
        
        data_para_api = None
        status_data_str = "Qualquer data"

        if self.date_filter_checkbox.isChecked():
            data_str_ui = self.data_input.date().toString("yyyy/MM/dd")
            data_para_api = data_str_ui # Define a data para a API
            status_data_str = data_str_ui
        
        self.statusBar().showMessage(f"Buscando de '{origem}' para '{destino}' em '{status_data_str}' (limite: {limite})...")
        self._clear_resultados_table()
        QApplication.processEvents()

        self.api_client.setOrigemBusca(origem if origem else None)
        self.api_client.setDestinoBusca(destino if destino else None)
        self.api_client.setDataBusca(data_para_api) # <<< --- Passa a data ou None para a API
        self.api_client.setLimite(limite)
        
        self.api_client.requestResponse()
        resultados_json = self.api_client.data_response_json
        
        # (O restante da lógica para popular a tabela permanece o mesmo da sua última versão)
        # Apenas ajuste a mensagem inicial da tabela se necessário:
        self.resultados_table.clearContents() # Limpa o conteúdo, mas mantém os cabeçalhos
        self.resultados_table.setRowCount(0)  # Garante que não há linhas antes de popular

        if resultados_json and "results" in resultados_json and resultados_json["results"]:
            viagens = resultados_json["results"]
            num_viagens = len(viagens)
            self.resultados_table.setRowCount(num_viagens)

            for row, trem_data in enumerate(viagens):
                data_viagem = trem_data.get('date', 'N/A')
                hora_partida = trem_data.get('heure_depart', 'N/A')
                hora_chegada = trem_data.get('heure_arrivee', 'N/A')
                origem_api = trem_data.get('origine', 'N/A')
                destino_api = trem_data.get('destination', 'N/A')
                num_trem = trem_data.get('numero_de_train', trem_data.get('train_no', 'N/A'))
                od_happy_val = trem_data.get('od_happy_card', 'N/A')

                self.resultados_table.setItem(row, 0, QTableWidgetItem(self.formatar_data(data_viagem)))
                self.resultados_table.setItem(row, 1, QTableWidgetItem(origem_api))
                self.resultados_table.setItem(row, 2, QTableWidgetItem(destino_api))
                self.resultados_table.setItem(row, 3, QTableWidgetItem(hora_partida))
                self.resultados_table.setItem(row, 4, QTableWidgetItem(hora_chegada))
                self.resultados_table.setItem(row, 5, QTableWidgetItem(str(num_trem)))
                self.resultados_table.setItem(row, 6, QTableWidgetItem(od_happy_val))
            
            self.statusBar().showMessage(f"{num_viagens} viagens encontradas.")
        elif resultados_json and "results" in resultados_json: # 0 resultados
            self.statusBar().showMessage(f"Nenhuma viagem encontrada para os critérios em '{status_data_str}'.")
        else:
            self.statusBar().showMessage("Erro na busca. Verifique o console para detalhes.")
            if self.api_client.last_URL:
                print(f"DEBUG (main_window): Última URL tentada: {self.api_client.last_URL}")
            if self.api_client.data_response_json is not None:
                print(f"DEBUG (main_window): Resposta bruta da API:\n{json.dumps(self.api_client.data_response_json, indent=2)}")