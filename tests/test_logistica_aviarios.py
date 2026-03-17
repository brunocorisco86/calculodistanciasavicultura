import unittest
from unittest.mock import patch, MagicMock
import requests
from src.api_client import OSRMClient

class TestLogisticaAviarios(unittest.TestCase):

    @patch('src.api_client.requests.get')
    def test_get_route_success(self, mock_get):
        # Configurar o mock para um retorno de sucesso
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Ok",
            "routes": [{
                "distance": 1500.0,
                "duration": 120.0,
                "geometry": {"coordinates": [[-53.0, -24.0], [-53.1, -24.1]]}
            }]
        }
        mock_get.return_value = mock_response

        client = OSRMClient()
        resultado = client.get_route(-24.0, -53.0, -24.1, -53.1)

        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["distancia_km"], 1.5)

    @patch('src.api_client.requests.get')
    def test_get_route_api_error_code(self, mock_get):
        # Configurar o mock para um retorno com código de erro da API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "NoRoute"
        }
        mock_get.return_value = mock_response

        client = OSRMClient()
        resultado = client.get_route(-24.0, -53.0, -24.1, -53.1)
        self.assertIsNone(resultado)

    @patch('src.api_client.requests.get')
    def test_get_route_exception(self, mock_get):
        # Configurar o mock para lançar uma exceção (ex: Timeout)
        mock_get.side_effect = requests.exceptions.RequestException("Timeout error")

        client = OSRMClient()
        resultado = client.get_route(-24.0, -53.0, -24.1, -53.1)
        self.assertIsNone(resultado)

if __name__ == '__main__':
    unittest.main()
