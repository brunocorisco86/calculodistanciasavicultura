import csv
import requests
import time
import sys
from functools import lru_cache

# Configurações do Ponto de Partida (Abatedouro)
ABATEDOURO_LAT = -24.330706428602536
ABATEDOURO_LON = -53.85805796419288
VELOCIDADE_MEDIA_KMH = 40.0

# Endpoint Público do OSRM (Open Source Routing Machine)
# Nota: OSRM usa o formato (longitude, latitude)
OSRM_URL = "http://router.project-osrm.org/route/v1/driving/{lon_start},{lat_start};{lon_end},{lat_end}?overview=false"


@lru_cache(maxsize=None)
def calcular_rota_real(lat_dest, lon_dest):
    """
    Consulta a API OSRM para obter a distância real via estradas.
    Retorna a distância em km.
    """
    url = OSRM_URL.format(
        lon_start=ABATEDOURO_LON,
        lat_start=ABATEDOURO_LAT,
        lon_end=lon_dest,
        lat_end=lat_dest,
    )

    try:
        response = requests.get(url, timeout=30)
        data = response.json()

        if data.get("code") == "Ok":
            # A distância retornada pelo OSRM é em metros
            distancia_metros = data["routes"][0]["distance"]
            return distancia_metros / 1000.0
        else:
            return None
    except Exception as e:
        print(f"Erro ao consultar API: {e}")
        return None


def processar_aviarios(csv_path):
    print(f"{'='*60}")
    print(f"{'LOGÍSTICA DE APANHA - AVÍCOLA':^60}")
    print(f"{'='*60}")
    print(
        f"{'Aviário':<10} | {'Produtor':<20} | {'Dist. (km)':<12} | {'Tempo (min)':<10}"
    )
    print(f"{'-'*60}")

    resultados = []

    try:
        # Usando utf-8-sig para remover automaticamente o BOM (\ufeff) se presente
        with open(csv_path, mode="r", encoding="utf-8-sig") as file:
            # Detectando se o delimitador é vírgula ou ponto e vírgula
            sample = file.read(1024)
            file.seek(0)
            dialect = csv.Sniffer().sniff(sample)

            reader = csv.DictReader(file, dialect=dialect)

            # Limpando espaços em branco dos nomes das colunas (caso existam)
            reader.fieldnames = [name.strip() for name in reader.fieldnames]

            for row in reader:
                try:
                    # Usando strip() nos valores para evitar erros de conversão
                    aviario = row["aviario"].strip()
                    nome = row["nome produtor"].strip()
                    lat = float(row["latitude"].strip())
                    lon = float(row["longitude"].strip())

                    # Cálculo da distância real via OSRM
                    distancia_km = calcular_rota_real(lat, lon)

                    if distancia_km is not None:
                        # Tempo = Distância / Velocidade
                        tempo_horas = distancia_km / VELOCIDADE_MEDIA_KMH
                        tempo_minutos = tempo_horas * 60

                        print(
                            f"{aviario:<10} | {nome[:20]:<20} | {distancia_km:>10.2f} | {tempo_minutos:>10.1f}"
                        )

                        row["distancia_km"] = round(distancia_km, 2)
                        row["tempo_minutos"] = round(tempo_minutos, 1)
                        resultados.append(row)
                    else:
                        print(
                            f"{aviario:<10} | {nome[:20]:<20} | {'ERRO API':>10} | {'ERRO API':>10}"
                        )

                except (ValueError, KeyError) as e:
                    # Pular linhas com erro de dado (ex: latitude vazia ou inválida)
                    continue

                # Pequeno delay para evitar sobrecarga na API pública
                time.sleep(0.5)

    except FileNotFoundError:
        print(f"Erro: Arquivo {csv_path} não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

    return resultados


if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_input = sys.argv[1]
    else:
        csv_input = "../data/raw/aviarios.csv"

    processar_aviarios(csv_input)
