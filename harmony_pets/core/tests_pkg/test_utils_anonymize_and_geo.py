from django.test import TestCase
from django.contrib.auth.models import User
from core.models import InteressadoAdocao
from core.utils import anonimizar_dados_interessado, geocodificar_endereco
from unittest.mock import patch, Mock


class AnonymizeUtilsTests(TestCase):
    def test_anonimizar_dados_interessado_overwrites_fields(self):
        user = User.objects.create_user(username='origuser', password='pw', email='orig@example.com', first_name='Orig', last_name='User')
        interessado = InteressadoAdocao.objects.create(usuario=user, cpf='123.456.789-00', telefone='(11)91234-5678', endereco='Rua A, 123')

        anonimizar_dados_interessado(interessado)

        user.refresh_from_db()
        interessado.refresh_from_db()

        # Verifica que campos do user foram sobrescritos
        self.assertEqual(user.first_name, 'Anonimo')
        self.assertEqual(user.last_name, 'Anonimo')
        self.assertEqual(user.email, f'anonimo_{user.id}@exemplo.com')
        self.assertEqual(user.username, f'anonimo_{user.id}')

        # Verifica que campos do interessado foram sobrescritos
        self.assertEqual(interessado.cpf, '***')
        self.assertEqual(interessado.telefone, '***')
        self.assertEqual(interessado.endereco, '***')


class GeocodeUtilsTests(TestCase):
    @patch('core.utils.requests.get')
    def test_geocodificar_endereco_returns_coordinates_on_ok(self, mock_get):
        mock_resp = Mock()
        mock_resp.json.return_value = {
            'status': 'OK',
            'results': [
                {'geometry': {'location': {'lat': 12.34, 'lng': 56.78}}}
            ]
        }
        mock_get.return_value = mock_resp

        coords = geocodificar_endereco('Rua Falsa, 123')
        self.assertIsNotNone(coords)
        self.assertEqual(coords, (12.34, 56.78))

    @patch('core.utils.requests.get')
    def test_geocodificar_endereco_returns_none_on_not_found(self, mock_get):
        mock_resp = Mock()
        mock_resp.json.return_value = {'status': 'ZERO_RESULTS', 'results': []}
        mock_get.return_value = mock_resp

        coords = geocodificar_endereco('Endereço inexistente')
        self.assertIsNone(coords)
