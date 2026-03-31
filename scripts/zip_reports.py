import os
import zipfile
from datetime import datetime

def zip_aviary_reports():
    base_dir = "docs/rotas_por_aviario"
    output_dir = "docs"
    
    # Nome do arquivo com timestamp para evitar sobrescrita se desejar, 
    # ou fixo como solicitado. Usaremos fixo conforme seu pedido.
    zip_filename = os.path.join(output_dir, "relatorios_rotas.zip")
    
    if not os.path.exists(base_dir):
        print(f"Erro: Diretorio {base_dir} nao encontrado.")
        return

    print(f"Iniciando a compactacao de arquivos em {zip_filename}...")
    
    count_files = 0
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Percorre todas as pastas de aviarios
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    # Filtra apenas mapas (html) e relatorios (txt)
                    if file.endswith('.html') or file.endswith('.txt'):
                        file_path = os.path.join(root, file)
                        # Mantem a estrutura de pastas dentro do zip (ex: 101/mapa_101.html)
                        arcname = os.path.relpath(file_path, base_dir)
                        zipf.write(file_path, arcname)
                        count_files += 1
                        
                        if count_files % 100 == 0:
                            print(f"Arquivos adicionados: {count_files}...")

        print(f"\nSucesso! {count_files} arquivos foram compactados em: {zip_filename}")
    except Exception as e:
        print(f"Ocorreu um erro durante a compactacao: {e}")

if __name__ == "__main__":
    zip_aviary_reports()
