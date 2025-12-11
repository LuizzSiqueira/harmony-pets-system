from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import AceitacaoTermos

class AdminDashboardTests(TestCase):
    def setUp(self):
        # Criar usuário staff com senha adequada e aceitar termos para não ser bloqueado pelo middleware
        self.admin = User.objects.create_user(username='admin', email='admin@test.local', password='Adminpass123', is_staff=True)
        AceitacaoTermos.objects.create(
            usuario=self.admin,
            termos_aceitos=True,
            lgpd_aceito=True,
            ip_aceitacao='127.0.0.1',
            user_agent='test-client',
            versao_termos='1.0'
        )
        self.user = User.objects.create_user(username='normal', password='userpass')

    def test_dashboard_requires_staff(self):
        # não autenticado
        resp = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(resp.status_code, 302)  # redirect to login
        # usuário normal
        self.client.force_login(self.user)
        resp2 = self.client.get(reverse('admin_dashboard'))
        # Django admin decorator redirect -> login with next param
        self.assertEqual(resp2.status_code, 302)
        self.client.logout()
        # staff
        logged_in = self.client.login(username='admin', password='Adminpass123')
        self.assertTrue(logged_in)
        resp3 = self.client.get(reverse('admin_dashboard'), follow=True)
        # staff (não precisa ser superuser) deve acessar
        self.assertEqual(resp3.status_code, 200)
        html = resp3.content.decode()
        self.assertIn('Dashboard Administrativo', html)
        self.assertIn('Cobertura Global', html)
        self.assertIn('Últimas Ações', html)

    def test_dashboard_shows_kpis_placeholders(self):
        logged_in = self.client.login(username='admin', password='Adminpass123')
        self.assertTrue(logged_in)
        resp = self.client.get(reverse('admin_dashboard'), follow=True)
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        # KPIs labels
        for label in ['Usuários', 'Interessados', 'Locais', 'Pets', 'Solicitações', '2FA']:
            self.assertIn(label, html)

    def test_nav_has_dashboard_and_logs_links(self):
        """Verifica se navbar exibe ambos links para Logs e Dashboard para staff."""
        logged_in = self.client.login(username='admin', password='Adminpass123')
        self.assertTrue(logged_in)
        resp = self.client.get(reverse('admin_logs'), follow=True)
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        # Checa pelas rotas (mais robusto que buscar por espaçamento em texto renderizado)
        self.assertIn(reverse('admin_logs'), html)
        self.assertIn(reverse('admin_dashboard'), html)
