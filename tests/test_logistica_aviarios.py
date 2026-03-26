import unittest
from unittest.mock import patch, MagicMock
import requests
from src.api_client import ValhallaClient

class TestLogisticaAviarios(unittest.TestCase):

    @patch('src.api_client.requests.post')
    def test_get_route_success(self, mock_post):
        # Configurar o mock para um retorno de sucesso
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "trip": {
                "legs": [{
                    "summary": {"length": 1.5, "time": 600},
                    "shape": "m_p~E_p~E_p~E_p~E", # Dummy shape
                    "maneuvers": []
                }]
            }
        }
        mock_post.return_value = mock_response

        # Mock polyline.decode to avoid issues with dummy shape
        with patch('src.api_client.polyline.decode', return_value=[(45.0, 10.0), (45.1, 10.1)]):
            client = ValhallaClient()
            resultado = client.get_route(-24.0, -53.0, -24.1, -53.1)
            self.assertEqual(resultado["distancia_km"], 1.5)
            self.assertEqual(resultado["duracao_segundos"], 600)

    @patch('src.api_client.requests.post')
    def test_get_route_api_error(self, mock_post):
        # Configurar o mock para um retorno com erro
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "No route"}
        mock_post.return_value = mock_response

        client = ValhallaClient()
        resultado = client.get_route(-24.0, -53.0, -24.1, -53.1)
        self.assertIsNone(resultado)

    @patch('src.api_client.requests.post')
    def test_get_route_exception(self, mock_post):
        # Configurar o mock para lançar uma exceção
        mock_post.side_effect = requests.exceptions.RequestException("Timeout error")

        client = ValhallaClient()
        resultado = client.get_route(-24.0, -53.0, -24.1, -53.1)
        self.assertIsNone(resultado)

if __name__ == '__main__':
    unittest.main()
