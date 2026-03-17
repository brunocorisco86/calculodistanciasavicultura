import os
import matplotlib.pyplot as plt
import folium
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

        # Plot route (Static)
        plot_path = os.path.join(aviary_folder, "rota.png")
        self._plot_route(route_info["geometria"], plot_path, aviary_id)

        # Generate Interactive Map (Folium)
        map_path = os.path.join(aviary_folder, "mapa_interativo.html")
        self._generate_folium_map(route_info["geometria"], map_path, aviary_id)

        # Generate Markdown
        md_path = os.path.join(aviary_folder, "relatorio.md")
        self._save_markdown(md_path, aviary_id, data, route_info)

        self.logger.info(f"Relatório gerado para aviário {aviary_id} em {aviary_folder}")

    def generate_summary_map(self, all_routes_info, abatedouro_coords):
        """
        Generates a summary map with all routes and aviaries.
        """
        try:
            m = folium.Map(location=abatedouro_coords, zoom_start=10)

            # Add abatedouro marker
            folium.Marker(
                location=abatedouro_coords,
                popup="Abatedouro (Base)",
                icon=folium.Icon(color="green", icon="home")
            ).add_to(m)

            for aviary_id, route_info in all_routes_info.items():
                coords = route_info["geometria"]["coordinates"]
                route_lats_lons = [(lat, lon) for lon, lat in coords]

                # Add route line
                folium.PolyLine(
                    route_lats_lons,
                    color="blue",
                    weight=3,
                    opacity=0.5,
                    popup=f"Rota Aviário {aviary_id}"
                ).add_to(m)

                # Add aviary marker
                folium.Marker(
                    location=route_lats_lons[-1],
                    popup=f"Aviário {aviary_id}",
                    icon=folium.Icon(color="red", icon="info-sign")
                ).add_to(m)

            summary_map_path = os.path.join(self.output_dir, "mapa_geral.html")
            m.save(summary_map_path)
            self.logger.info(f"Mapa geral gerado em {summary_map_path}")
        except Exception as e:
            self.logger.error(f"Erro ao gerar mapa geral: {e}")

    def _generate_folium_map(self, geometry, save_path, aviary_id):
        """
        Generates an interactive map using Folium with OpenStreetMap background.
        """
        try:
            coords = geometry["coordinates"]
            # Folium uses (lat, lon), GeoJSON uses (lon, lat)
            route_lats_lons = [(lat, lon) for lon, lat in coords]

            # Center map on the start point
            m = folium.Map(location=route_lats_lons[0], zoom_start=12)

            # Add the route line
            folium.PolyLine(route_lats_lons, color="blue", weight=5, opacity=0.7).add_to(m)

            # Add markers for start and end
            folium.Marker(
                location=route_lats_lons[0],
                popup="Abatedouro (Início)",
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)

            folium.Marker(
                location=route_lats_lons[-1],
                popup=f"Aviário {aviary_id} (Fim)",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)

            m.save(save_path)
        except Exception as e:
            self.logger.error(f"Erro ao gerar mapa folium para {aviary_id}: {e}")

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
        If the file already exists, it updates the "Rota até o aviário" section.
        """
        steps = route_info.get("steps", [])
        instructions = self._generate_instructions(steps, aviary_id) if steps else ["Rota não disponível."]
        instructions_md = "\n".join(instructions)

        new_section = f"## Rota até o aviário\n{instructions_md}\n"

        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # Find the start of the section
                start_index = -1
                for i, line in enumerate(lines):
                    if line.strip() == "## Rota até o aviário":
                        start_index = i
                        break

                if start_index != -1:
                    # Section exists, find where it ends (next ## or end of file)
                    end_index = len(lines)
                    for i in range(start_index + 1, len(lines)):
                        if lines[i].startswith("## "):
                            end_index = i
                            break

                    # Replace the content of the section
                    lines[start_index:end_index] = [f"{new_section}\n"]
                    content = "".join(lines)
                else:
                    # Section doesn't exist, append it
                    content = "".join(lines) + f"\n{new_section}"
            except Exception as e:
                self.logger.error(f"Erro ao ler markdown existente para {aviary_id}: {e}")
                return
        else:
            # Create new content
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

{new_section}"""

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f"Erro ao salvar markdown para {aviary_id}: {e}")

    def _format_distance(self, distance_meters):
        """
        Formats distance according to requirements:
        - Below 1km: Round to nearest 10m (e.g. 152m -> 150m)
        - 1km or over: Convert to km with one decimal place (e.g. 1094m -> 1,1 km)
        """
        if distance_meters < 1000:
            rounded = round(distance_meters / 10.0) * 10
            return f"{int(rounded)}m"
        else:
            km = distance_meters / 1000.0
            return f"{km:.1f} km".replace('.', ',')

    def _generate_instructions(self, steps, aviary_id):
        """
        Converts OSRM RouteSteps into natural Portuguese sentences.
        """
        instructions = []

        # Mapping for modifiers
        modifiers_pt = {
            "left": "à esquerda",
            "right": "à direita",
            "sharp left": "acentuadamente à esquerda",
            "sharp right": "acentuadamente à direita",
            "slight left": "levemente à esquerda",
            "slight right": "levemente à direita",
            "straight": "em frente",
            "uturn": "em retorno"
        }

        for i, step in enumerate(steps):
            maneuver = step.get("maneuver", {})
            m_type = maneuver.get("type")
            m_modifier = maneuver.get("modifier")
            name = step.get("name", "")
            distance = step.get("distance", 0)

            if not name:
                name = "rua sem nome"

            formatted_dist = self._format_distance(distance)

            if m_type == "depart":
                instr = f"Saia da {name}"
            elif m_type == "arrive":
                instr = f"Você chegará ao aviário {aviary_id}"
                if m_modifier in ["left", "right"]:
                    instr += f" {modifiers_pt[m_modifier]}"
            elif m_type == "turn":
                modifier_str = modifiers_pt.get(m_modifier, m_modifier)
                instr = f"Vire {modifier_str} na {name}"
            elif m_type in ["continue", "on ramp", "merge"]:
                instr = f"Siga em frente na {name}"
            else:
                modifier_str = modifiers_pt.get(m_modifier, m_modifier if m_modifier else "")
                if modifier_str:
                    instr = f"{m_type.capitalize()} {modifier_str} na {name}"
                else:
                    instr = f"{m_type.capitalize()} na {name}"

            if distance > 0 and m_type != "arrive":
                instr += f", siga por {formatted_dist}."
            else:
                instr += "."

            instructions.append(f"{i+1}. {instr}")

        return instructions
