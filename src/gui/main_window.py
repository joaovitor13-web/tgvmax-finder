# src/gui/main_window.py
import customtkinter as ctk
from tkinter import messagebox # ttk para Treeview se CustomTkinter não tiver um equivalente fácil
import logging
from typing import List
import threading # Para rodar a busca em background
from datetime import datetime # Para o filtro de data, se adicionar

from src.models.journey_models import SearchQuery, Journey
from src.core import journey_builder, search_history, data_formatter
# from src.gui.widgets.journey_card import JourneyCard # Descomente se for usar o JourneyCard

logger = logging.getLogger(__name__)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TGV Max Finder Avançado")
        self.geometry("1100x700")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.current_search_history: List[SearchQuery] = []
        self.found_journeys: List[Journey] = [] # Para armazenar as jornadas encontradas

        # --- Layout Principal (Esquerda: Entradas e Histórico, Direita: Resultados) ---
        self.grid_columnconfigure(0, weight=1, minsize=300) # Coluna de inputs/histórico
        self.grid_columnconfigure(1, weight=3)              # Coluna de resultados
        self.grid_rowconfigure(0, weight=1)

        # --- Frame da Esquerda ---
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=(10,5), pady=10, sticky="nsew")
        self.left_frame.grid_rowconfigure(1, weight=0) # Input
        self.left_frame.grid_rowconfigure(3, weight=1) # Histórico lista

        # Input Frame
        self.input_controls_frame = ctk.CTkFrame(self.left_frame)
        self.input_controls_frame.grid(row=0, column=0, padx=5, pady=5, sticky="new")
        
        ctk.CTkLabel(self.input_controls_frame, text="Origem:").grid(row=0, column=0, padx=5, pady=3, sticky="w")
        self.entry_origin = ctk.CTkEntry(self.input_controls_frame, placeholder_text="Ex: PARIS")
        self.entry_origin.grid(row=0, column=1, padx=5, pady=3, sticky="ew")

        ctk.CTkLabel(self.input_controls_frame, text="Destino:").grid(row=1, column=0, padx=5, pady=3, sticky="w")
        self.entry_destination = ctk.CTkEntry(self.input_controls_frame, placeholder_text="Ex: LYON")
        self.entry_destination.grid(row=1, column=1, padx=5, pady=3, sticky="ew")
        
        # Opcional: Filtro de Data
        # ctk.CTkLabel(self.input_controls_frame, text="Data (AAAA-MM-DD):").grid(row=2, column=0, padx=5, pady=3, sticky="w")
        # self.entry_date = ctk.CTkEntry(self.input_controls_frame, placeholder_text="Opcional")
        # self.entry_date.grid(row=2, column=1, padx=5, pady=3, sticky="ew")

        ctk.CTkLabel(self.input_controls_frame, text="Max Conexões:").grid(row=3, column=0, padx=5, pady=3, sticky="w")
        self.combo_max_connections = ctk.CTkComboBox(self.input_controls_frame, values=["0 (Direto)", "1 Conexão"]) # , "2 Conexões" (adicionar quando implementado)
        self.combo_max_connections.set("0 (Direto)")
        self.combo_max_connections.grid(row=3, column=1, padx=5, pady=3, sticky="ew")

        self.button_search = ctk.CTkButton(self.input_controls_frame, text="Buscar Viagens", command=self.start_search_thread)
        self.button_search.grid(row=4, column=0, columnspan=2, padx=5, pady=10)
        
        self.input_controls_frame.grid_columnconfigure(1, weight=1)

        # Histórico Frame
        ctk.CTkLabel(self.left_frame, text="Histórico de Pesquisas:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=1, column=0, padx=5, pady=(10,2), sticky="w")
        self.history_scrollable_frame = ctk.CTkScrollableFrame(self.left_frame, label_text="")
        self.history_scrollable_frame.grid(row=2, column=0, padx=5, pady=(0,5), sticky="nsew")
           
        # --- Frame da Direita (Resultados) ---
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=(5,10), pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.right_frame, text="Resultados da Busca:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Usar CTkScrollableFrame para os resultados, se for usar JourneyCard
        # self.results_scrollable_frame = ctk.CTkScrollableFrame(self.right_frame)
        # self.results_scrollable_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Ou, continuar com CTkTextbox por enquanto
        self.results_textbox = ctk.CTkTextbox(self.right_frame, state="disabled", wrap="none", height=300, font=("Consolas", 10) if os.name == 'nt' else ("monospace", 11))
        self.results_textbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
           
        # Status Bar
        self.status_label = ctk.CTkLabel(self, text="Pronto.", text_color="gray", anchor="w")
        self.status_label.grid(row=1, column=0, columnspan=2, padx=10, pady=(0,5), sticky="ew")

        self.load_and_display_history()

    def start_search_thread(self):
        origin = self.entry_origin.get().strip().upper()
        destination = self.entry_destination.get().strip().upper()
        # date_str = self.entry_date.get().strip() # Descomentar se adicionar campo de data
        
        if not origin or not destination:
            messagebox.showwarning("Entrada Inválida", "Origem e Destino são obrigatórios.", parent=self)
            return

        # Validação de data (se adicionado)
        # valid_date_str = None
        # if date_str:
        #     try:
        #         datetime.strptime(date_str, "%Y-%m-%d")
        #         valid_date_str = date_str
        #     except ValueError:
        #         messagebox.showerror("Data Inválida", "Formato da data deve ser AAAA-MM-DD.", parent=self)
        #         return
        
        try:
            max_conn_str = self.combo_max_connections.get().split(" ")[0]
            max_connections = int(max_conn_str)
        except ValueError:
            messagebox.showerror("Erro", "Número de conexões inválido.", parent=self)
            return

        query = SearchQuery(origin=origin, destination=destination, max_connections=max_connections) #, departure_date=valid_date_str)

        self.button_search.configure(state="disabled", text="Buscando...")
        self.clear_results_display() # Limpa antes de mostrar "buscando"
        self.update_results_display("Buscando viagens para: {} -> {} (Máx Conexões: {})\nPor favor, aguarde...".format(origin, destination, max_connections))
        self.status_label.configure(text=f"Buscando: {origin} -> {destination}...")
        self.update_idletasks()

        thread = threading.Thread(target=self.perform_search, args=(query,))
        thread.daemon = True
        thread.start()

    def perform_search(self, query: SearchQuery):
        try:
            logger.info(f"Iniciando busca para: {query}")
            self.found_journeys = journey_builder.find_journeys(query) # Armazena as jornadas
            logger.info(f"Busca concluída. Encontradas {len(self.found_journeys)} jornadas.")
            self.after(0, self.update_ui_with_results, query, self.found_journeys)
        except Exception as e:
            logger.error(f"Erro na thread de busca: {e}", exc_info=True)
            self.after(0, messagebox.showerror, "Erro de Busca", f"Ocorreu um erro: {e}")
            self.after(0, self.reset_search_button_and_status, "Erro na busca.")

    def clear_results_display(self):
        # Se usar CTkScrollableFrame com JourneyCards:
        # for widget in self.results_scrollable_frame.winfo_children():
        #     widget.destroy()
        # Se usar CTkTextbox:
        self.results_textbox.configure(state="normal")
        self.results_textbox.delete("1.0", "end")
        self.results_textbox.configure(state="disabled")

    def update_results_display(self, content: str):
        self.results_textbox.configure(state="normal")
        self.results_textbox.insert("end", content)
        self.results_textbox.configure(state="disabled")

    def update_ui_with_results(self, query: SearchQuery, journeys: List[Journey]):
        self.clear_results_display()

        if not journeys:
            self.update_results_display("Nenhuma viagem TGV Max encontrada para os critérios informados.")
        else:
            # Se usar CTkScrollableFrame com JourneyCards:
            # for journey in journeys:
            #     card = JourneyCard(self.results_scrollable_frame, journey)
            #     card.pack(pady=5, padx=5, fill="x")
            # Se usar CTkTextbox:
            results_text = f"Encontradas {len(journeys)} opções de viagem:\n\n"
            for journey in journeys:
                formatted_journey = data_formatter.format_journey_for_display(journey)
                results_text += formatted_journey + "\n\n"
            self.update_results_display(results_text)
        
        self.reset_search_button_and_status(f"Busca concluída. {len(journeys)} resultados.")

        self.current_search_history = search_history.add_to_history(query, self.current_search_history)
        search_history.save_history(self.current_search_history)
        self.display_history()

    def reset_search_button_and_status(self, status_message="Pronto."):
        self.button_search.configure(state="normal", text="Buscar Viagens")
        self.status_label.configure(text=status_message)

    def load_and_display_history(self):
        self.current_search_history = search_history.load_history()
        self.display_history()

    def display_history(self):
        for widget in self.history_scrollable_frame.winfo_children():
            widget.destroy()

        if not self.current_search_history:
            ctk.CTkLabel(self.history_scrollable_frame, text="Nenhuma pesquisa recente.").pack(padx=5, pady=5, anchor="w")
            return

        for query_item in self.current_search_history:
            item_frame = ctk.CTkFrame(self.history_scrollable_frame, fg_color="transparent")
            item_frame.pack(fill="x", padx=2, pady=1)

            label_text = f"{query_item.origin} → {query_item.destination} ({query_item.max_connections}c)"
            # if query_item.departure_date:
            #     label_text += f" em {query_item.departure_date}"
            
            btn_action = lambda q=query_item: self.reuse_history_item(q)
            
            hist_button = ctk.CTkButton(item_frame, text=label_text, command=btn_action, anchor="w", fg_color="transparent", hover_color="gray70", text_color=("gray10", "gray90"))
            hist_button.pack(side="left", fill="x", expand=True)

    def reuse_history_item(self, query_item: SearchQuery):
        logger.info(f"Reutilizando item do histórico: {query_item}")
        self.entry_origin.delete(0, "end")
        self.entry_origin.insert(0, query_item.origin)
        self.entry_destination.delete(0, "end")
        self.entry_destination.insert(0, query_item.destination)
        
        # if query_item.departure_date: # Se filtro de data for adicionado
        #     self.entry_date.delete(0, "end")
        #     self.entry_date.insert(0, query_item.departure_date)
        # else:
        #     self.entry_date.delete(0, "end")

        conn_text_map = {0: "0 (Direto)", 1: "1 Conexão", 2: "2 Conexões"}
        self.combo_max_connections.set(conn_text_map.get(query_item.max_connections, "0 (Direto)"))
        
        self.start_search_thread() # Opcional: iniciar a busca automaticamente