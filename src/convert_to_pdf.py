import os
import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos

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

def generate_pdf_from_folder(aviary_id, folder_path):
    pdf = RoutePDF(report_title=f"Relatório de Rota - Aviário {aviary_id}")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Caminho absoluto para o HTML (mais compatível para uso local)
    html_abs_path = os.path.abspath(os.path.join(folder_path, "mapa_interativo.html"))
    # No Windows, file:// precisa de barras extras, no Linux file:// basta. 
    # Usaremos file:// seguido do caminho.
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

    pdf_output = os.path.join(folder_path, f"relatorio_{aviary_id}.pdf")
    pdf.output(pdf_output)
    return pdf_output

def main():
    base_dir = "docs/rotas_por_aviario"
    if not os.path.exists(base_dir):
        print(f"Diretório {base_dir} não encontrado.")
        return

    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
    folders.sort()

    print(f"Atualizando links em {len(folders)} PDFs...")
    
    count = 0
    for aviary_id in folders:
        folder_path = os.path.join(base_dir, aviary_id)
        try:
            generate_pdf_from_folder(aviary_id, folder_path)
            count += 1
            if count % 100 == 0:
                print(f"Processados: {count}/{len(folders)}")
        except Exception as e:
            print(f"Erro ao gerar PDF para {aviary_id}: {e}")

    print(f"\nConcluído! {count} PDFs atualizados com links absolutos.")

if __name__ == "__main__":
    main()
