import sys
import os
from src.logistica_aviarios import AviaryProcessor
from src.utils.logger import setup_logger

def main():
    logger = setup_logger("Main", log_file="src/utils/main.log")

    raw_csv = "data/raw/aviarios.csv"
    processed_csv = "data/processed/aviarios_processados.csv"

    if len(sys.argv) > 1:
        raw_csv = sys.argv[1]

    if not os.path.exists(raw_csv):
        logger.error(f"Arquivo de entrada não encontrado: {raw_csv}")
        return

    processor = AviaryProcessor(
        raw_csv_path=raw_csv,
        processed_csv_path=processed_csv,
        logger=logger
    )

    try:
        processor.run()
    except Exception as e:
        logger.error(f"Erro durante a execução do processador: {e}")

if __name__ == "__main__":
    main()
