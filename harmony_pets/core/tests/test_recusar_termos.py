from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class RecusarTermosTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass123456')

    def test_refusal_page_renders_anonymous(self):
        resp = self.client.get(reverse('recusar_termos'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Você optou por não aceitar os termos', resp.content.decode())

    def test_refusal_page_allows_revocation_when_accepted(self):
        # Cria aceite
        from core.models import AceitacaoTermos
        AceitacaoTermos.objects.create(
            usuario=self.user,
            termos_aceitos=True,
            lgpd_aceito=True,
            ip_aceitacao='127.0.0.1',
            user_agent='test',
            versao_termos='1.0'
        )
        self.client.force_login(self.user)
        resp = self.client.get(reverse('recusar_termos'))
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        # Deve exibir opção de revogar
        self.assertIn(reverse('revogar_termos'), html)

    def test_links_present_for_navigation(self):
        resp = self.client.get(reverse('recusar_termos'))
        html = resp.content.decode()
        self.assertIn(reverse('termos_uso'), html)
        self.assertIn(reverse('aceitar_termos'), html)
        self.assertIn(reverse('home'), html)
