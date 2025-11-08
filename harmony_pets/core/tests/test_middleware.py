from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import AceitacaoTermos, TwoFactorAuth


class MiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_terms_acceptance_middleware_blocks_without_terms(self):
        u = User.objects.create_user('m1', 'm1@example.com', 'pass12345')
        self.client.login(username='m1', password='pass12345')
        resp = self.client.get(reverse('profile'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('aceitar_termos'), resp['Location'])

    def test_twofactor_middleware_redirects_to_verify(self):
        u = User.objects.create_user('m2', 'm2@example.com', 'pass12345')
        # Aceita termos para não bloquear nessa etapa
        AceitacaoTermos.objects.create(
            usuario=u,
            termos_aceitos=True,
            lgpd_aceito=True,
            ip_aceitacao='127.0.0.1',
            user_agent='agent',
            versao_termos='1.0',
        )
        # Ativa 2FA (is_enabled=True)
        TwoFactorAuth.objects.create(usuario=u, secret_key='A' * 32, is_enabled=True)
        self.client.login(username='m2', password='pass12345')
        resp = self.client.get(reverse('profile'))
        # Deve redirecionar para verify_2fa
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('verify_2fa'), resp['Location'])
