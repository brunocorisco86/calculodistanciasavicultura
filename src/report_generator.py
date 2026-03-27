import os
import re
import matplotlib.pyplot as plt
import folium
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from src.utils.logger import setup_logger

class RoutePDF(FPDF):
    def __init__(self, report_title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report_title = report_title

    def header(self):
        if self.page_no() == 1:
            self.set_font("helvetica", "B", 16)
            self.cell(0, 10, self.report_title, border=False, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="C")

class ReportGenerator:
    def __init__(self, output_dir="docs/rotas_por_aviario", logger=None):
        self.output_dir = output_dir
        self.logger = logger or setup_logger("ReportGenerator")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_aviary_report(self, aviary_id, data, route_info):
        """
        Generates a folder for the aviary with a markdown report, route plot, interactive map and PDF.
        """
        aviary_folder = os.path.join(self.output_dir, str(aviary_id))
        if not os.path.exists(aviary_folder):
            os.makedirs(aviary_folder)

        # Plot route
        plot_path = os.path.join(aviary_folder, "rota.png")
        self._plot_route(route_info["geometria"], plot_path, aviary_id)

        # Generate Interactive Map
        map_path = os.path.join(aviary_folder, "mapa_interativo.html")
        self._generate_interactive_map(route_info["geometria"], map_path, aviary_id)

        # Generate Markdown
        md_path = os.path.join(aviary_folder, "relatorio.md")
        self._save_markdown(md_path, aviary_id, data, route_info)

        # Generate PDF
        pdf_path = os.path.join(aviary_folder, f"relatorio_{aviary_id}.pdf")
        self._generate_pdf(aviary_id, aviary_folder, pdf_path)

        self.logger.info(f"Relatório gerado para aviário {aviary_id} em {aviary_folder}")

    def _generate_pdf(self, aviary_id, folder_path, output_path):
        """
        Generates a PDF report combining the plot, a link to the interactive map, and the markdown content.
        """
        try:
            pdf = RoutePDF(report_title=f"Relatório de Rota - Aviário {aviary_id}")
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Link absoluto com prefixo file://
            html_abs_path = os.path.abspath(os.path.join(folder_path, "mapa_interativo.html"))
            link_url = f"file://{html_abs_path}"

            # 1. Inserir o Plot (rota.png)
            plot_path = os.path.join(folder_path, "rota.png")
            if os.path.exists(plot_path):
                pdf.image(plot_path, x=10, y=None, w=190)
                pdf.ln(5)

            # 2. Hyperlink para o Mapa Interativo
            pdf.set_font("helvetica", "U", 12)
            pdf.set_text_color(0, 0, 255)
            pdf.cell(0, 10, "Clique aqui para abrir o Mapa Interativo HTML", align="C", link=link_url, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(5)

            # 3. Conteúdo do relatorio.md
            md_path = os.path.join(folder_path, "relatorio.md")
            if os.path.exists(md_path):
                with open(md_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("# ") or "![" in line or "[Visualizar" in line:
                        continue
                    
                    if line.startswith("## "):
                        pdf.set_font("helvetica", "B", 14)
                        pdf.ln(2)
                        pdf.cell(0, 10, line.replace("## ", ""), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.set_font("helvetica", "", 10)
                        continue

                    clean_line = line.replace("**", "")
                    pdf.set_font("helvetica", "", 10)
                    if clean_line.startswith("- ") or re.match(r'^\d+\.', clean_line):
                        pdf.multi_cell(0, 6, f"  {clean_line}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.multi_cell(0, 6, clean_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.output(output_path)
        except Exception as e:
            self.logger.error(f"Erro ao gerar PDF para {aviary_id}: {e}")

    def _generate_interactive_map(self, geometry, save_path, aviary_id):
        """
        Generates an interactive HTML map using Folium.
        """
        try:
            coords = geometry["coordinates"]
            # Folium uses (lat, lon), OSRM/GeoJSON uses (lon, lat)
            points = [(lat, lon) for lon, lat in coords]

            # Start map centered on the first point
            m = folium.Map(location=points[0], zoom_start=12)

            # Add route line
            folium.PolyLine(points, color="blue", weight=5, opacity=0.7).add_to(m)

            # Add markers
            folium.Marker(location=points[0], popup="Início (Abatedouro)", icon=folium.Icon(color="green")).add_to(m)
            folium.Marker(location=points[-1], popup=f"Fim (Aviário {aviary_id})", icon=folium.Icon(color="red")).add_to(m)

            # Fit map to bounds
            m.fit_bounds([points[0], points[-1]])

            m.save(save_path)
        except Exception as e:
            self.logger.error(f"Erro ao gerar mapa interativo para {aviary_id}: {e}")

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
- **Tempo Estimado (Valhalla):** {route_info['duracao_segundos'] / 60:.1f} minutos
- **Tempo Estimado (40 km/h):** {data.get('tempo_minutos', 'N/A')} minutos

## Mapa da Rota
![Rota](rota.png)

[Visualizar Mapa Interativo](mapa_interativo.html)

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
        Converts Valhalla maneuvers into natural Portuguese sentences.
        """
        instructions = []

        for i, maneuver in enumerate(steps):
            # Valhalla provide instruction directly in the requested language
            instr = maneuver.get("instruction", "")
            length = maneuver.get("length", 0)

            # length is in kilometers (as requested in api_client.py)
            distance_meters = length * 1000
            formatted_dist = self._format_distance(distance_meters)

            if i < len(steps) - 1 and distance_meters > 0:
                # Append distance if not the last maneuver
                if instr.endswith("."):
                    instr = instr[:-1]
                instr += f", siga por {formatted_dist}."
            elif i == len(steps) - 1:
                # Adjust last instruction if necessary
                if "chegar" in instr.lower() or "destino" in instr.lower():
                    instr = instr.replace("Seu destino", f"O aviário {aviary_id}")
                    instr = instr.replace("seu destino", f"o aviário {aviary_id}")

            instructions.append(f"{i+1}. {instr}")

        return instructions
