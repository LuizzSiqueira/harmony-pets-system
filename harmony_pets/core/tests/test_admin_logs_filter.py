from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from core.models import AuditLog
from core.models import AceitacaoTermos


class AdminLogsFilterTests(TestCase):
    def setUp(self):
        # Cria usuários
        self.admin = User.objects.create_user(username='admin', password='pass123', is_staff=True, is_superuser=True)
        self.user_a = User.objects.create_user(username='alice', password='pass123')
        self.user_b = User.objects.create_user(username='bob', password='pass123')

        # Admin já aceitou termos (bypassa middleware de termos)
        AceitacaoTermos.objects.create(
            usuario=self.admin,
            termos_aceitos=True,
            lgpd_aceito=True,
            ip_aceitacao='127.0.0.1',
            user_agent='test',
            versao_termos='1.0'
        )

        # Cria registros de auditoria distintos
        AuditLog.objects.create(usuario=self.user_a, metodo='GET', caminho='/pets/', view_name='pets_list', status_code=200, ip='127.0.0.1', duracao_ms=50)
        AuditLog.objects.create(usuario=self.user_a, metodo='POST', caminho='/login/', view_name='login', status_code=302, ip='127.0.0.1', duracao_ms=120)
        AuditLog.objects.create(usuario=self.user_b, metodo='GET', caminho='/profile/', view_name='profile', status_code=200, ip='127.0.0.1', duracao_ms=80)
        AuditLog.objects.create(usuario=None, metodo='GET', caminho='/publico/', view_name='public', status_code=200, ip='127.0.0.1', duracao_ms=30)

    def _extract_auditlog_tbody(self, html: str) -> str:
        """Extrai apenas o conteúdo do <tbody> da tabela 'AuditLog (Banco)' para evitar
        falsos positivos vindos do dropdown de usuários e do painel de log de arquivo.
        Se não for possível localizar de forma confiável, retorna o HTML completo.
        """
        marker = 'AuditLog (Banco)'
        idx = html.find(marker)
        if idx == -1:
            return html
        tbody_start = html.find('<tbody>', idx)
        tbody_end = html.find('</tbody>', idx)
        if tbody_start == -1 or tbody_end == -1 or tbody_end <= tbody_start:
            return html
        return html[tbody_start:tbody_end]

    def test_admin_logs_requires_staff(self):
        # Sem login deve redirecionar para login admin
        url = reverse('admin_logs')
        resp = self.client.get(url)
        self.assertNotEqual(resp.status_code, 200)

    def test_filter_by_user_id(self):
        # Login como staff (usando force_login para evitar dependência de backend)
        self.client.force_login(self.admin)
        url = reverse('admin_logs') + f'?usuario={self.user_a.id}'
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        # Deve conter registros da alice e não do bob (apenas dentro do tbody da tabela AuditLog)
        content = resp.content.decode()
        tbody = self._extract_auditlog_tbody(content)
        self.assertIn('alice', tbody)
        # Usa padrão de célula da tabela para evitar falso positivo em dropdown
        self.assertNotIn('<td>bob</td>', tbody)

    def test_filter_by_username_case_insensitive(self):
        self.client.force_login(self.admin)
        url = reverse('admin_logs') + '?user=ALICE'
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        tbody = self._extract_auditlog_tbody(content)
        self.assertIn('alice', tbody)
        self.assertNotIn('<td>bob</td>', tbody)

    def test_filter_path_contains(self):
        self.client.force_login(self.admin)
        url = reverse('admin_logs') + '?audit_path=profile'
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        tbody = self._extract_auditlog_tbody(content)
        self.assertIn('/profile/', tbody)
        # Não deve conter caminhos adicionais que não batem com o filtro
        self.assertNotIn('/extra/', tbody)

    def test_limit_audit_n(self):
        self.client.force_login(self.admin)
        # Cria vários logs adicionais para testar limite
        for i in range(30):
            AuditLog.objects.create(usuario=self.user_a, metodo='GET', caminho=f'/extra/{i}/', view_name='extra', status_code=200, ip='127.0.0.1', duracao_ms=5)
        url = reverse('admin_logs') + '?audit_n=10'
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        # Conta ocorrências de '/extra/' na página deve ser <= 10
        tbody = self._extract_auditlog_tbody(resp.content.decode())
        # Cada linha repete o caminho no atributo title e no texto; conte apenas pelo title para contar linhas
        count_extra_rows = tbody.count('title="/extra/')
        self.assertLessEqual(count_extra_rows, 10)

    def test_limit_audit_n_clamps_to_minimum(self):
        """Quando for passado um valor inválido/negativo, o backend deve aplicar limite mínimo 1."""
        self.client.force_login(self.admin)
        # Gera vários registros para podermos verificar o clamp em 1
        for i in range(5):
            AuditLog.objects.create(usuario=self.user_a, metodo='GET', caminho=f'/extra/{i}/', view_name='extra', status_code=200, ip='127.0.0.1', duracao_ms=5)
        url = reverse('admin_logs') + '?audit_n=-5'
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        tbody = self._extract_auditlog_tbody(resp.content.decode())
        count_extra_rows = tbody.count('title="/extra/')
        self.assertLessEqual(count_extra_rows, 1)

    def test_template_audit_n_min_attribute_is_1(self):
        """O input do template deve expor min=1 para alinhamento com a regra do backend."""
        self.client.force_login(self.admin)
        url = reverse('admin_logs')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        # Verifica que o campo existe e tem min="1"
        self.assertIn('name="audit_n"', html)
        self.assertIn('min="1"', html)
