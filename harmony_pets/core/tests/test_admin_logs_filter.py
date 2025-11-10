from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from core.models import AuditLog


class AdminLogsFilterTests(TestCase):
    def setUp(self):
        # Cria usuários
        self.admin = User.objects.create_user(username='admin', password='pass123', is_staff=True, is_superuser=True)
        self.user_a = User.objects.create_user(username='alice', password='pass123')
        self.user_b = User.objects.create_user(username='bob', password='pass123')

        # Cria registros de auditoria distintos
        AuditLog.objects.create(usuario=self.user_a, metodo='GET', caminho='/pets/', view_name='pets_list', status_code=200, ip='127.0.0.1', duracao_ms=50)
        AuditLog.objects.create(usuario=self.user_a, metodo='POST', caminho='/login/', view_name='login', status_code=302, ip='127.0.0.1', duracao_ms=120)
        AuditLog.objects.create(usuario=self.user_b, metodo='GET', caminho='/profile/', view_name='profile', status_code=200, ip='127.0.0.1', duracao_ms=80)
        AuditLog.objects.create(usuario=None, metodo='GET', caminho='/publico/', view_name='public', status_code=200, ip='127.0.0.1', duracao_ms=30)

    def test_admin_logs_requires_staff(self):
        # Sem login deve redirecionar para login admin
        url = reverse('admin_logs')
        resp = self.client.get(url)
        self.assertNotEqual(resp.status_code, 200)

    def test_filter_by_user_id(self):
        self.client.login(username='admin', password='pass123')
        url = reverse('admin_logs') + f'?usuario={self.user_a.id}'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # Deve conter caminhos da alice e não o de bob
        content = resp.content.decode()
        self.assertIn('/pets/', content)
        self.assertIn('/login/', content)
        self.assertNotIn('/profile/', content)

    def test_filter_by_username_case_insensitive(self):
        self.client.login(username='admin', password='pass123')
        url = reverse('admin_logs') + '?user=ALICE'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('/pets/', content)
        self.assertIn('/login/', content)
        self.assertNotIn('/profile/', content)

    def test_filter_path_contains(self):
        self.client.login(username='admin', password='pass123')
        url = reverse('admin_logs') + '?audit_path=profile'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('/profile/', content)
        # Não deve conter /pets/ se apenas profile foi filtrado
        # Pode conter outros se sem usuário, então verificação parcial
        self.assertNotIn('/pets/', content)

    def test_limit_audit_n(self):
        self.client.login(username='admin', password='pass123')
        # Cria vários logs adicionais para testar limite
        for i in range(30):
            AuditLog.objects.create(usuario=self.user_a, metodo='GET', caminho=f'/extra/{i}/', view_name='extra', status_code=200, ip='127.0.0.1', duracao_ms=5)
        url = reverse('admin_logs') + '?audit_n=10'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # Conta ocorrências de '/extra/' na página deve ser <= 10
        count_extra = resp.content.decode().count('/extra/')
        self.assertLessEqual(count_extra, 10)
