import sys
import os
import json
from src.logistica_aviarios import processar_aviarios
from src.utils.logger import setup_logger

def load_starting_points(json_path):
    if not os.path.exists(json_path):
        return {}
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def select_starting_point(points):
    print("\nSelecione o ponto de partida:")
    options = list(points.keys())
    for i, name in enumerate(options, 1):
        print(f"{i}. {name}")
    
    while True:
        try:
            choice = int(input("\nDigite o número da opção desejada: "))
            if 1 <= choice <= len(options):
                name = options[choice-1]
                return name, points[name]
        except ValueError:
            pass
        print("Opção inválida. Tente novamente.")

def main():
    logger = setup_logger("Main", log_file="src/utils/main.log")

    raw_csv = "data/raw/aviarios.csv"
    points_json = "data/ponto_partida.json"

    if len(sys.argv) > 1:
        raw_csv = sys.argv[1]

    if not os.path.exists(raw_csv):
        logger.error(f"Arquivo de entrada não encontrado: {raw_csv}")
        return

    points = load_starting_points(points_json)
    if not points:
        logger.error(f"Arquivo de pontos de partida não encontrado ou vazio: {points_json}")
        # Fallback para abatedouro se falhar
        start_name = "Abatedouro"
        start_lat, start_lon = -24.330339382519863, -53.85809208526941
    else:
        start_name, coords = select_starting_point(points)
        start_lat, start_lon = coords['lat'], coords['lon']

    try:
        processar_aviarios(raw_csv, start_lat, start_lon, start_name)
    except Exception as e:
        logger.error(f"Erro durante a execução: {e}")

if __name__ == "__main__":
    main()
