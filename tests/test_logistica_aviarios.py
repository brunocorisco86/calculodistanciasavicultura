import unittest
from unittest.mock import patch, MagicMock
import requests
from src.logistica_aviarios import calcular_rota_real

class TestLogisticaAviarios(unittest.TestCase):

    @patch('src.logistica_aviarios.requests.get')
    def test_calcular_rota_real_success(self, mock_get):
        # Configurar o mock para um retorno de sucesso
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Ok",
            "routes": [{"distance": 1500.0}]  # 1.5 km
        }
        mock_get.return_value = mock_response

        resultado = calcular_rota_real(-24.0, -53.0)
        self.assertEqual(resultado, 1.5)

    @patch('src.logistica_aviarios.requests.get')
    def test_calcular_rota_real_api_error_code(self, mock_get):
        # Configurar o mock para um retorno com código de erro da API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "NoRoute"
        }
        mock_get.return_value = mock_response

        resultado = calcular_rota_real(-24.0, -53.0)
        self.assertIsNone(resultado)

    @patch('src.logistica_aviarios.requests.get')
    def test_calcular_rota_real_exception(self, mock_get):
        # Configurar o mock para lançar uma exceção (ex: Timeout)
        mock_get.side_effect = requests.exceptions.RequestException("Timeout error")

        resultado = calcular_rota_real(-24.0, -53.0)
        self.assertIsNone(resultado)

if __name__ == '__main__':
    unittest.main()
