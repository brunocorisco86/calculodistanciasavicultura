import os
import subprocess
import time
import shutil
import sys
from pathlib import Path

# Configuração de caminhos baseada na localização do script
SCRIPT_PATH = Path(__file__).resolve()
ROOT_DIR = SCRIPT_PATH.parent.parent

# Configurações relativas à raiz do projeto
DOCKER_DIR = ROOT_DIR / "docker"
CUSTOM_FILES_DIR = ROOT_DIR / "custom_files"
DOCS_DIR = ROOT_DIR / "docs/rotas_por_aviario"
CONTAINER_NAME = "valhalla_cvale"

def log(msg):
    print(f"[LOG] {msg}")

def check_docker_running():
    """Verifica se o container está rodando."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", CONTAINER_NAME],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip() == "true"
    except subprocess.CalledProcessError:
        return False

def restart_and_rebuild():
    """Reinicia o container e força o recálculo dos grafos (deletando tiles)."""
    log("Reiniciando Valhalla e recalculando grafos...")
    
    # Parar container
    compose_file = DOCKER_DIR / "docker-compose.yml"
    subprocess.run(["docker", "compose", "-f", str(compose_file), "down"], cwd=str(ROOT_DIR), check=False)
    
    # Deletar tiles existentes para forçar recálculo
    # Usamos um container temporário para deletar, pois o Docker pode ter criado arquivos como root
    log("Limpando arquivos antigos com Docker (evitando erro de permissão)...")
    subprocess.run([
        "docker", "run", "--rm", 
        "-v", f"{ROOT_DIR}:/work", 
        "busybox", "rm", "-rf", 
        "/work/custom_files/valhalla_tiles", "/work/custom_files/valhalla_tiles.tar"
    ], check=False)

    # Subir via setup_valhalla.sh
    setup_script = DOCKER_DIR / "setup_valhalla.sh"
    log(f"Executando {setup_script}...")
    subprocess.run(["bash", str(setup_script)], cwd=str(ROOT_DIR), check=True)

def update_reports():
    """Executa o processamento principal para gerar novos relatórios/PDFs."""
    log("Iniciando atualização dos relatórios...")
    
    # Rodar scripts a partir da raiz do projeto
    log("Rodando main.py --first para processar novos dados se houver...")
    try:
        subprocess.run([sys.executable, "main.py", "--first"], cwd=str(ROOT_DIR), check=True)
    except subprocess.CalledProcessError:
        log("Erro ao rodar main.py. Tentando apenas atualizar PDFs existentes...")
        subprocess.run([sys.executable, "src/convert_to_pdf.py"], cwd=str(ROOT_DIR), check=True)
    
    log("Garantindo que todos os PDFs estejam atualizados com src/convert_to_pdf.py...")
    subprocess.run([sys.executable, "src/convert_to_pdf.py"], cwd=str(ROOT_DIR), check=True)

def copy_pdfs_to_custom_files():
    """
    Copia todos os PDFs gerados para a pasta custom_files.
    """
    log(f"Sincronizando arquivos PDF em {CUSTOM_FILES_DIR}...")
    count = 0
    if not DOCS_DIR.exists():
        log(f"Diretório de documentos {DOCS_DIR} não existe.")
        return

    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".pdf"):
                src_path = Path(root) / file
                dst_path = CUSTOM_FILES_DIR / file
                shutil.copy2(src_path, dst_path)
                count += 1
    log(f"{count} PDFs copiados para {CUSTOM_FILES_DIR}.")

def main():
    # 1. Verificar Docker
    if not check_docker_running():
        log(f"Container {CONTAINER_NAME} não está rodando.")
        restart_and_rebuild()
    else:
        log(f"Container {CONTAINER_NAME} está rodando normalmente.")
        if "--force" in sys.argv:
            restart_and_rebuild()

    # 2. Atualizar PDFs
    update_reports()
    copy_pdfs_to_custom_files()

    log("Sistema atualizado com sucesso!")

if __name__ == "__main__":
    main()
