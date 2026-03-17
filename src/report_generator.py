import os
import matplotlib.pyplot as plt
from src.utils.logger import setup_logger

class ReportGenerator:
    def __init__(self, output_dir="docs/rotas_por_aviario", logger=None):
        self.output_dir = output_dir
        self.logger = logger or setup_logger("ReportGenerator")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_aviary_report(self, aviary_id, data, route_info):
        """
        Generates a folder for the aviary with a markdown report and a route plot.
        """
        aviary_folder = os.path.join(self.output_dir, str(aviary_id))
        if not os.path.exists(aviary_folder):
            os.makedirs(aviary_folder)

        # Plot route
        plot_path = os.path.join(aviary_folder, "rota.png")
        self._plot_route(route_info["geometria"], plot_path, aviary_id)

        # Generate Markdown
        md_path = os.path.join(aviary_folder, "relatorio.md")
        self._save_markdown(md_path, aviary_id, data, route_info)

        self.logger.info(f"Relatório gerado para aviário {aviary_id} em {aviary_folder}")

    def _plot_route(self, geometry, save_path, aviary_id):
        """
        Plots the route coordinates using matplotlib.
        """
        try:
            coords = geometry["coordinates"]
            lons, lats = zip(*coords)

            plt.figure(figsize=(10, 6))
            plt.plot(lons, lats, marker='o', markersize=2, linestyle='-', color='blue', label='Rota')
            plt.plot(lons[0], lats[0], 'go', label='Início (Abatedouro)')
            plt.plot(lons[-1], lats[-1], 'ro', label='Fim (Aviário)')

            plt.title(f"Rota para o Aviário {aviary_id}")
            plt.xlabel("Longitude")
            plt.ylabel("Latitude")
            plt.legend()
            plt.grid(True)

            plt.savefig(save_path)
            plt.close()
        except Exception as e:
            self.logger.error(f"Erro ao plotar rota para {aviary_id}: {e}")

    def _save_markdown(self, path, aviary_id, data, route_info):
        """
        Saves a markdown file with the route information.
        """
        content = f"""# Relatório de Rota - Aviário {aviary_id}

## Informações Gerais
- **Produtor:** {data.get('nome produtor', 'N/A')}
- **Latitude:** {data.get('latitude', 'N/A')}
- **Longitude:** {data.get('longitude', 'N/A')}

## Dados da Rota
- **Distância Real:** {route_info['distancia_km']:.2f} km
- **Tempo Estimado (OSRM):** {route_info['duracao_segundos'] / 60:.1f} minutos
- **Tempo Estimado (40 km/h):** {data.get('tempo_minutos', 'N/A')} minutos

## Mapa da Rota
![Rota](rota.png)
"""
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f"Erro ao salvar markdown para {aviary_id}: {e}")
