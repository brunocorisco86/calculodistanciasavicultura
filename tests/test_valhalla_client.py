import unittest
from unittest.mock import patch, MagicMock
import requests
import polyline
from src.api_client import ValhallaClient

class TestValhallaClient(unittest.TestCase):

    @patch('src.api_client.requests.post')
    def test_get_route_success(self, mock_post):
        # Configurar o mock para um retorno de sucesso
        mock_response = MagicMock()
        # Polyline para [(45.0, 10.0), (45.1, 10.1)] com precisão 6
        # [[10.0, 45.0], [10.1, 45.1]] em lon, lat
        encoded_shape = polyline.encode([(45.0, 10.0), (45.1, 10.1)], 6)

        mock_response.json.return_value = {
            "trip": {
                "legs": [{
                    "summary": {
                        "length": 1.5,
                        "time": 600
                    },
                    "shape": encoded_shape,
                    "maneuvers": [
                        {"instruction": "Siga em frente", "length": 1.0},
                        {"instruction": "Chegou ao seu destino", "length": 0.5}
                    ]
                }]
            }
        }
        mock_post.return_value = mock_response

        client = ValhallaClient()
        resultado = client.get_route(45.0, 10.0, 45.1, 10.1)

        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["distancia_km"], 1.5)
        self.assertEqual(resultado["duracao_segundos"], 600)
        self.assertEqual(len(resultado["geometria"]["coordinates"]), 2)
        # Verifica se inverteu para lon, lat
        self.assertEqual(resultado["geometria"]["coordinates"][0], [10.0, 45.0])
        self.assertEqual(len(resultado["steps"]), 2)

    @patch('src.api_client.requests.post')
    def test_get_route_api_error(self, mock_post):
        # Configurar o mock para um retorno com erro (ex: trip ausente)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error_code": 171,
            "error": "No route found"
        }
        mock_post.return_value = mock_response

        client = ValhallaClient()
        resultado = client.get_route(45.0, 10.0, 45.1, 10.1)
        self.assertIsNone(resultado)

    @patch('src.api_client.requests.post')
    def test_get_route_exception(self, mock_post):
        # Configurar o mock para lançar uma exceção (ex: Timeout)
        mock_post.side_effect = requests.exceptions.RequestException("Timeout error")

        client = ValhallaClient()
        resultado = client.get_route(45.0, 10.0, 45.1, 10.1)
        self.assertIsNone(resultado)

if __name__ == '__main__':
    unittest.main()
