import sys
import os
import json
from src.logistica_estruturas import processar_estruturas
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

    raw_csv = "data/raw/estruturas.csv"
    points_json = "data/ponto_partida.json"

    start_arg = None

    # Lógica de argumentos simplificada e potente
    # Ex: python main.py [arquivo.csv] [nome_do_ponto]
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.endswith(".csv") and os.path.exists(arg):
                raw_csv = arg
            elif not arg.startswith("-"):
                start_arg = arg

    if not os.path.exists(raw_csv):
        logger.error(f"Arquivo de entrada não encontrado: {raw_csv}")
        return

    points = load_starting_points(points_json)
    if not points:
        logger.error(f"Arquivo de pontos de partida não encontrado ou vazio: {points_json}")
        start_name = "Abatedouro"
        start_lat, start_lon = -24.330339382519863, -53.85809208526941
    else:
        # 1. Tenta usar o nome do ponto passado via argumento
        if start_arg and start_arg in points:
            start_name = start_arg
            coords = points[start_name]
            logger.info(f"Utilizando ponto de partida solicitado: {start_name}")
        # 2. Se for interativo (terminal real), pergunta ao usuário
        elif sys.stdin.isatty():
            start_name, coords = select_starting_point(points)
        # 3. Fallback (ex: echo "1" | python main.py ou rodando via cron)
        else:
            # Tenta pegar o primeiro valor do stdin se houver algo vindo via pipe
            try:
                # Caso o usuário envie "1" via echo "1" | ...
                import select
                if select.select([sys.stdin,],[],[],0.0)[0]:
                    line = sys.stdin.readline().strip()
                    if line.isdigit():
                        idx = int(line) - 1
                        options = list(points.keys())
                        if 0 <= idx < len(options):
                            start_name = options[idx]
                            coords = points[start_name]
                            logger.info(f"Ponto selecionado via input stream: {start_name}")
                        else:
                            raise ValueError
                    else:
                        raise ValueError
                else:
                    raise ValueError
            except:
                # Se tudo falhar, pega o primeiro ponto (abatedouro)
                start_name = list(points.keys())[0]
                coords = points[start_name]
                logger.info(f"Modo não-interativo: utilizando ponto padrão: {start_name}")
        
        start_lat, start_lon = coords['lat'], coords['lon']

    try:
        processar_estruturas(raw_csv, start_lat, start_lon, start_name)
    except Exception as e:
        logger.error(f"Erro durante a execução: {e}")

if __name__ == "__main__":
    main()
