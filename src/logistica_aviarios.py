import csv
import os
import time
import sys
from pathlib import Path
from src.utils.logger import setup_logger
from src.api_client import ValhallaClient
from src.report_generator import ReportGenerator

VELOCIDADE_MEDIA_KMH = 40.0

class AviaryProcessor:
    def __init__(self, raw_csv_path, processed_csv_path, start_lat, start_lon, start_name="Abatedouro", logger=None):
        self.raw_csv_path = raw_csv_path
        self.processed_csv_path = processed_csv_path
        self.start_lat = start_lat
        self.start_lon = start_lon
        self.start_name = start_name
        self.logger = logger or setup_logger("AviaryProcessor", log_file="src/utils/processamento.log")
        self.api_client = ValhallaClient(timeout=30, max_retries=3, logger=self.logger)
        self.report_generator = ReportGenerator(logger=self.logger)

    def run(self):
        self.logger.info(f"Iniciando processamento de aviários saindo de: {self.start_name}...")
        resultados = []

        try:
            with open(self.raw_csv_path, mode='r', encoding='utf-8-sig') as file:
                sample = file.read(1024)
                file.seek(0)
                dialect = csv.Sniffer().sniff(sample)
                reader = csv.DictReader(file, dialect=dialect)
                # Normalize fieldnames to remove leading/trailing whitespace
                reader.fieldnames = [name.strip() for name in reader.fieldnames]

                for row in reader:
                    try:
                        processed_row = self._process_row(row)
                        if processed_row:
                            resultados.append(processed_row)
                    except Exception as e:
                        self.logger.error(f"Erro ao processar linha {row.get('aviario')}: {e}")

            self._save_results(resultados)
            self.logger.info(f"Processamento concluído. {len(resultados)} registros processados.")

        except FileNotFoundError:
            self.logger.error(f"Erro: Arquivo {self.raw_csv_path} não encontrado.")
        except Exception as e:
            self.logger.error(f"Ocorreu um erro inesperado: {e}")

    def _normalize_coordinate(self, value_str):
        """
        Normaliza coordenadas que podem estar sem o ponto decimal.
        Exemplo: -2434534 -> -24.34534
        """
        if not value_str:
            return None
        
        clean_val = value_str.strip().replace(',', '.')
        
        try:
            val = float(clean_val)
            
            # Se o valor já estiver em uma faixa razoável de coordenadas, retorna ele
            if -180 <= val <= 180:
                # Caso especial: valores como -24000.0 que entraram como float mas estão errados
                # Se for um inteiro grande "disfarçado" de float (ex: -23903.0)
                if abs(val) > 90 and "." in clean_val and clean_val.endswith(".0"):
                    # Trata como se não tivesse o ponto
                    clean_val = clean_val.split('.')[0]
                else:
                    return val

            # Se chegou aqui, o valor está fora da faixa ou precisa de correção
            is_negative = clean_val.startswith('-')
            # Pega apenas os dígitos
            digits = "".join(filter(str.isdigit, clean_val))
            
            if len(digits) >= 2:
                # Insere o ponto após os dois primeiros dígitos
                normalized = digits[:2] + "." + digits[2:]
                final_val = float(normalized)
                return -final_val if is_negative else final_val
            
            return val
        except (ValueError, IndexError):
            return None

    def _process_row(self, row):
        aviario = row['aviario'].strip()
        nome = row['nome produtor'].strip()

        lat = self._normalize_coordinate(row.get('latitude'))
        lon = self._normalize_coordinate(row.get('longitude'))

        if lat is None or lon is None:
            self.logger.warning(f"Coordenadas inválidas para aviário {aviario}: Lat={row.get('latitude')}, Lon={row.get('longitude')}")
            return None

        route_info = self.api_client.get_route(self.start_lat, self.start_lon, lat, lon)

        if route_info:
            distancia_km = route_info['distancia_km']
            tempo_horas = distancia_km / VELOCIDADE_MEDIA_KMH
            tempo_minutos = tempo_horas * 60
            
            row['distancia_km'] = round(distancia_km, 2)
            row['tempo_minutos'] = round(tempo_minutos, 1)
            row['ponto_partida'] = self.start_name
            
            self.logger.info(f"Aviário: {aviario:<10} | Produtor: {nome[:20]:<20} | Dist.: {distancia_km:>8.2f} km | Tempo: {tempo_minutos:>6.1f} min")
            
            # Gerar relatório individual
            self.report_generator.generate_aviary_report(aviario, row, route_info, start_name=self.start_name)

            return row
        else:
            self.logger.error(f"Não foi possível calcular a rota para o aviário {aviario}")
            return None

    def _save_results(self, resultados):
        if not resultados:
            self.logger.warning("Nenhum resultado para salvar.")
            return

        os.makedirs(os.path.dirname(self.processed_csv_path), exist_ok=True)

        fieldnames = resultados[0].keys()
        try:
            with open(self.processed_csv_path, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(resultados)
            self.logger.info(f"Resultados salvos em {self.processed_csv_path}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar CSV processado: {e}")

def processar_aviarios(csv_path, start_lat, start_lon, start_name="Abatedouro"):
    # Validação de segurança do caminho do arquivo (Prevenção de Path Traversal)
    try:
        base_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
        target_path = os.path.realpath(csv_path)

        if os.path.commonpath([base_dir]) != os.path.commonpath([base_dir, target_path]):
            print(f"Erro de Segurança: O caminho {csv_path} está fora do diretório permitido.")
            return []
    except Exception as e:
        print(f"Erro ao validar o caminho do arquivo: {e}")
        return []

    print(f"{'='*60}")
    print(f"{'LOGÍSTICA DE APANHA - AVÍCOLA':^60}")
    print(f"{'='*60}")
    print(f"{'Aviário':<10} | {'Produtor':<20} | {'Dist. (km)':<12} | {'Tempo (min)':<10}")
    print(f"{'-'*60}")

    processor = AviaryProcessor(
        raw_csv_path=target_path,
        processed_csv_path="data/processed/aviarios_processados.csv",
        start_lat=start_lat,
        start_lon=start_lon,
        start_name=start_name
    )
    processor.run()

if __name__ == "__main__":
    # Coordenadas padrão do Abatedouro se rodado diretamente
    DEFAULT_LAT = -24.330339382519863
    DEFAULT_LON = -53.85809208526941

    if len(sys.argv) > 1:
        csv_input = sys.argv[1]
    else:
        # Resolve o caminho para ../data/raw/aviarios.csv relativo ao script de forma absoluta
        base_path = Path(__file__).resolve().parent
        csv_input = base_path.parent / "data" / "raw" / "aviarios.csv"

    processar_aviarios(str(csv_input), DEFAULT_LAT, DEFAULT_LON)
