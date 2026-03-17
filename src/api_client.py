import requests
import time
from src.utils.logger import setup_logger

class OSRMClient:
    BASE_URL = "http://router.project-osrm.org/route/v1/driving/"

    def __init__(self, timeout=30, max_retries=3, logger=None):
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger or setup_logger("OSRMClient")

    def get_route(self, lat_start, lon_start, lat_end, lon_end):
        """
        Consults the OSRM API to get the real distance and geometry via roads.
        """
        url = f"{self.BASE_URL}{lon_start},{lat_start};{lon_end},{lat_end}?overview=full&geometries=geojson"

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"Tentativa {attempt}/{self.max_retries}: Consultando API OSRM para ({lat_end}, {lon_end})")
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                if data.get("code") == "Ok":
                    route = data["routes"][0]
                    distancia_metros = route["distance"]
                    duracao_segundos = route["duration"]
                    geometria = route["geometry"]

                    return {
                        "distancia_km": distancia_metros / 1000.0,
                        "duracao_segundos": duracao_segundos,
                        "geometria": geometria
                    }
                else:
                    self.logger.error(f"Erro na resposta da API OSRM: {data.get('code')}")
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Erro na tentativa {attempt}: {e}")
                if attempt < self.max_retries:
                    time.sleep(1 * attempt) # Simple backoff
            except Exception as e:
                self.logger.error(f"Erro inesperado: {e}")
                break

        return None
