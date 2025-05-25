# src/gui/widgets/journey_card.py
import customtkinter as ctk
from src.models.journey_models import Journey
from src.core.data_formatter import format_journey_for_display # Para usar a formatação padrão

class JourneyCard(ctk.CTkFrame):
    def __init__(self, master, journey: Journey, **kwargs):
        super().__init__(master, **kwargs)

        self.journey = journey

        # Exemplo: Usar um CTkLabel para mostrar os detalhes da viagem formatados
        # Você pode tornar isso muito mais elaborado com múltiplos labels, ícones, etc.
        
        journey_text = format_journey_for_display(self.journey) # Reutiliza o formatador
        
        self.details_label = ctk.CTkLabel(self, text=journey_text, justify="left", anchor="nw")
        self.details_label.pack(padx=10, pady=10, fill="both", expand=True)

        # Adicionar uma borda para visualização
        self.configure(border_width=1, border_color="gray")

# Exemplo de uso (para teste, se você rodar este arquivo diretamente)
# if __name__ == '__main__':
#     from datetime import datetime, timedelta
#     from src.models.journey_models import Leg

#     # Criar uma janela raiz de teste
#     root = ctk.CTk()
#     root.title("Teste JourneyCard")
#     root.geometry("600x400")

#     # Criar dados de exemplo para uma Journey
#     leg1 = Leg(origin_station="Paris", destination_station="Lyon",
#                departure_time=datetime.now(), arrival_time=datetime.now() + timedelta(hours=2),
#                is_max_jeune=True, places_max_jeune=10)
#     leg2 = Leg(origin_station="Lyon", destination_station="Marseille",
#                departure_time=datetime.now() + timedelta(hours=3), arrival_time=datetime.now() + timedelta(hours=5),
#                is_max_senior=True, places_max_senior=5)
#     sample_journey = Journey(legs=[leg1, leg2])

#     # Criar e exibir o JourneyCard
#     card = JourneyCard(root, sample_journey)
#     card.pack(padx=10, pady=10, fill="x")

#     root.mainloop()