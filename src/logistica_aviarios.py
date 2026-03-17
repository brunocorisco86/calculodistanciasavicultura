import csv
import os
import time
import sys
from pathlib import Path
from src.utils.logger import setup_logger
from src.api_client import OSRMClient
from src.report_generator import ReportGenerator

# Configurações do Ponto de Partida (Abatedouro)
ABATEDOURO_LAT = -24.330706428602536
ABATEDOURO_LON = -53.85805796419288
VELOCIDADE_MEDIA_KMH = 40.0


class AviaryProcessor:
    def __init__(self, raw_csv_path: str, processed_csv_path: str, logger=None) -> None:
        self.raw_csv_path = raw_csv_path
        self.processed_csv_path = processed_csv_path
        self.logger = logger or setup_logger(
            "AviaryProcessor",
            log_file="src/utils/processamento.log"
        )
        self.api_client = OSRMClient(timeout=30, max_retries=3, logger=self.logger)
        self.report_generator = ReportGenerator(logger=self.logger)

    def run(self) -> None:
        self.logger.info("Iniciando processamento de aviários...")
        resultados = []
        all_routes_info = {}

        try:
            with open(self.raw_csv_path, mode="r", encoding="utf-8-sig") as file:
                sample = file.read(1024)
                file.seek(0)

                # Detectar dialeto (delimitador etc.)
                dialect = csv.Sniffer().sniff(sample)
                reader = csv.DictReader(file, dialect=dialect)
                # Normalize fieldnames to remove leading/trailing whitespace
                reader.fieldnames = [name.strip() for name in reader.fieldnames]

                for row in reader:
                    try:
                        # Modified: collect geometry if successful
                        aviario = row["aviario"].strip()
                        processed_row, route_info = self._process_row_v2(row)
                        if processed_row:
                            resultados.append(processed_row)
                            all_routes_info[aviario] = route_info
                    except Exception as e:
                        self.logger.error(
                            f"Erro ao processar linha {row.get('aviario', 'DESCONHECIDO')}: {e}"
                        )

                    # Pequeno delay para evitar sobrecarga na API pública
                    time.sleep(0.5)

            self._save_results(resultados)

            # Generate summary map with all routes
            if all_routes_info:
                self.report_generator.generate_summary_map(
                    all_routes_info,
                    (ABATEDOURO_LAT, ABATEDOURO_LON)
                )

            self.logger.info(
                "Processamento concluído. %d registros processados.",
                len(resultados)
            )

        except FileNotFoundError:
            self.logger.error("Erro: Arquivo %s não encontrado.", self.raw_csv_path)
        except Exception as e:
            self.logger.error("Ocorreu um erro inesperado: %s", e)

    def _process_row(self, row: dict) -> dict | None:
        # Mantendo compatibilidade legada se necessário
        processed, _ = self._process_row_v2(row)
        return processed

    def _process_row_v2(self, row: dict) -> tuple[dict | None, dict | None]:
        aviario = row["aviario"].strip()
        nome = row["nome produtor"].strip()

        try:
            lat = float(row["latitude"].strip().replace(",", "."))
            lon = float(row["longitude"].strip().replace(",", "."))
        except ValueError as e:
            self.logger.warning(
                "Coordenadas inválidas para aviário %s: %s",
                aviario,
                e,
            )
            return None, None

        route_info = self.api_client.get_route(
            ABATEDOURO_LAT,
            ABATEDOURO_LON,
            lat,
            lon,
        )

        if not route_info:
            self.logger.error(
                "Não foi possível calcular a rota para o aviário %s",
                aviario,
            )
            return None, None

        distancia_km = route_info["distancia_km"]
        tempo_horas = distancia_km / VELOCIDADE_MEDIA_KMH
        tempo_minutos = tempo_horas * 60

        row["distancia_km"] = round(distancia_km, 2)
        row["tempo_minutos"] = round(tempo_minutos, 1)

        self.logger.info(
            "Aviário: %-10s | Produtor: %-20s | Dist.: %8.2f km | Tempo: %6.1f min",
            aviario,
            nome[:20],
            distancia_km,
            tempo_minutos,
        )

        # Gerar relatório individual
        self.report_generator.generate_aviary_report(aviario, row, route_info)

        return row, route_info

    def _save_results(self, resultados: list[dict]) -> None:
        if not resultados:
            self.logger.warning("Nenhum resultado para salvar.")
            return

        out_dir = os.path.dirname(self.processed_csv_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        fieldnames = list(resultados[0].keys())

        try:
            with open(
                self.processed_csv_path,
                mode="w",
                encoding="utf-8",
                newline="",
            ) as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(resultados)
            self.logger.info("Resultados salvos em %s", self.processed_csv_path)
        except Exception as e:
            self.logger.error("Erro ao salvar CSV processado: %s", e)

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


def processar_aviarios(csv_path):
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
        processed_csv_path="data/processed/aviarios_processados.csv"
    )
    processor.run()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_input = sys.argv[1]
    else:
        # Resolve o caminho para ../data/raw/aviarios.csv relativo ao script de forma absoluta
        base_path = Path(__file__).resolve().parent
        csv_input = base_path.parent / "data" / "raw" / "aviarios.csv"

    processar_aviarios(str(csv_input))
