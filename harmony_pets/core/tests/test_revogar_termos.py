from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import AceitacaoTermos

class RevogarTermosTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', email='user1@test.local', password='Userpass123')
        # cria aceite prévio
        AceitacaoTermos.objects.create(
            usuario=self.user,
            termos_aceitos=True,
            lgpd_aceito=True,
            ip_aceitacao='127.0.0.1',
            user_agent='test-client',
            versao_termos='1.0'
        )

    def test_revogar_termos_flags_and_redirect(self):
        # login
        logged = self.client.login(username='user1', password='Userpass123')
        self.assertTrue(logged)
        # POST revogar
        resp = self.client.post(reverse('revogar_termos'), follow=True)
        self.assertEqual(resp.status_code, 200)
        # flags devem ficar falsos
        aceitacao = AceitacaoTermos.objects.get(usuario=self.user)
        self.assertFalse(aceitacao.termos_aceitos)
        self.assertFalse(aceitacao.lgpd_aceito)
        # tentar acessar home deve redirecionar para aceitar_termos por middleware
        resp2 = self.client.get(reverse('home'))
        self.assertEqual(resp2.status_code, 302)
        self.assertIn(reverse('aceitar_termos'), resp2['Location'])

    def test_access_recusar_page_authenticated(self):
        # Mesmo com termos aceitos, recusar_termos deve estar acessível
        self.client.login(username='user1', password='Userpass123')
        resp = self.client.get(reverse('recusar_termos'))
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        # Botão de revogação deve estar presente
        self.assertIn(reverse('revogar_termos'), html)
