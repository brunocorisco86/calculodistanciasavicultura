import requests
import time
import polyline
from src.utils.logger import setup_logger

class ValhallaClient:
    BASE_URL = "https://valhalla1.openstreetmap.de/route"

    def __init__(self, timeout=30, max_retries=3, logger=None):
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger or setup_logger("ValhallaClient")

    def get_route(self, lat_start, lon_start, lat_end, lon_end):
        """
        Consults the Valhalla API to get the real distance and geometry via roads.
        """
        params = {
            "locations": [
                {"lat": lat_start, "lon": lon_start},
                {"lat": lat_end, "lon": lon_end}
            ],
            "costing": "truck",
            "language": "pt-BR",
            "units": "kilometers"
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"Tentativa {attempt}/{self.max_retries}: Consultando API Valhalla para ({lat_end}, {lon_end})")
                response = requests.post(self.BASE_URL, json=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                if "trip" in data:
                    trip = data["trip"]
                    leg = trip["legs"][0]

                    # Decodificar a polyline (Valhalla usa 6 casas decimais por padrão)
                    shape = leg["shape"]
                    coords = polyline.decode(shape, 6)
                    # Converter de (lat, lon) para (lon, lat) para manter compatibilidade com GeoJSON/OSRM anterior
                    geojson_coords = [[lon, lat] for lat, lon in coords]

                    geometria = {
                        "type": "LineString",
                        "coordinates": geojson_coords
                    }

                    distancia_km = leg["summary"]["length"]
                    duracao_segundos = leg["summary"]["time"]
                    maneuvers = leg["maneuvers"]

                    return {
                        "distancia_km": distancia_km,
                        "duracao_segundos": duracao_segundos,
                        "geometria": geometria,
                        "steps": maneuvers
                    }
                else:
                    self.logger.error(f"Erro na resposta da API Valhalla: {data}")
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Erro na tentativa {attempt}: {e}")
                if attempt < self.max_retries:
                    time.sleep(1 * attempt) # Simple backoff
            except Exception as e:
                self.logger.error(f"Erro inesperado: {e}")
                break

        return None
