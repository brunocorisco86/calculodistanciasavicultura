import csv
import os
import time
from src.utils.logger import setup_logger
from src.api_client import OSRMClient
from src.report_generator import ReportGenerator

# Configurações do Ponto de Partida (Abatedouro)
ABATEDOURO_LAT = -24.330706428602536
ABATEDOURO_LON = -53.85805796419288
VELOCIDADE_MEDIA_KMH = 40.0

class AviaryProcessor:
    def __init__(self, raw_csv_path, processed_csv_path, logger=None):
        self.raw_csv_path = raw_csv_path
        self.processed_csv_path = processed_csv_path
        self.logger = logger or setup_logger("AviaryProcessor", log_file="src/utils/processamento.log")
        self.api_client = OSRMClient(timeout=30, max_retries=3, logger=self.logger)
        self.report_generator = ReportGenerator(logger=self.logger)

    def run(self):
        self.logger.info("Iniciando processamento de aviários...")
        resultados = []
        
        try:
            with open(self.raw_csv_path, mode='r', encoding='utf-8-sig') as file:
                sample = file.read(1024)
                file.seek(0)
                dialect = csv.Sniffer().sniff(sample)
                reader = csv.DictReader(file, dialect=dialect)
                reader.fieldnames = [name.strip() for name in reader.fieldnames]

                for row in reader:
                    try:
                        processed_row = self._process_row(row)
                        if processed_row:
                            resultados.append(processed_row)
                    except Exception as e:
                        self.logger.error(f"Erro ao processar linha {row.get('aviario')}: {e}")

                    # Pequeno delay para evitar sobrecarga na API pública
                    time.sleep(0.5)

            self._save_results(resultados)
            self.logger.info(f"Processamento concluído. {len(resultados)} registros processados.")

        except FileNotFoundError:
            self.logger.error(f"Erro: Arquivo {self.raw_csv_path} não encontrado.")
        except Exception as e:
            self.logger.error(f"Ocorreu um erro inesperado: {e}")

    def _process_row(self, row):
        aviario = row['aviario'].strip()
        nome = row['nome produtor'].strip()

        try:
            lat = float(row['latitude'].strip().replace(',', '.'))
            lon = float(row['longitude'].strip().replace(',', '.'))
        except ValueError as e:
            self.logger.warning(f"Coordenadas inválidas para aviário {aviario}: {e}")
            return None

        route_info = self.api_client.get_route(ABATEDOURO_LAT, ABATEDOURO_LON, lat, lon)

        if route_info:
            distancia_km = route_info['distancia_km']
            tempo_horas = distancia_km / VELOCIDADE_MEDIA_KMH
            tempo_minutos = tempo_horas * 60
            
            row['distancia_km'] = round(distancia_km, 2)
            row['tempo_minutos'] = round(tempo_minutos, 1)
            
            self.logger.info(f"Aviário: {aviario:<10} | Produtor: {nome[:20]:<20} | Dist.: {distancia_km:>8.2f} km | Tempo: {tempo_minutos:>6.1f} min")
            
            # Gerar relatório individual
            self.report_generator.generate_aviary_report(aviario, row, route_info)

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

if __name__ == "__main__":
    # Mantendo compatibilidade se chamado diretamente
    processor = AviaryProcessor(
        raw_csv_path="data/raw/aviarios.csv",
        processed_csv_path="data/processed/aviarios_processados.csv"
    )
    processor.run()
