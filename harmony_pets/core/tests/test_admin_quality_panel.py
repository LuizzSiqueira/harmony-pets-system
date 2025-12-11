from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
import os
from core.models import AceitacaoTermos

DUMMY_COVERAGE = """<?xml version='1.0'?>\n<coverage line-rate='0.621' lines-valid='100' lines-covered='62'>\n  <packages>\n    <package name='core' line-rate='0.512'/>\n  </packages>\n</coverage>\n"""

class AdminQualityPanelTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass', is_staff=True, is_superuser=True)
        # Admin aceita termos para não ser bloqueado pelo middleware
        AceitacaoTermos.objects.create(
            usuario=self.admin,
            termos_aceitos=True,
            lgpd_aceito=True,
            ip_aceitacao='127.0.0.1',
            user_agent='test',
            versao_termos='1.0'
        )
        # Escreve um coverage.xml mínimo para testes
        coverage_path = os.path.join(settings.BASE_DIR, 'harmony_pets', 'coverage.xml')
        with open(coverage_path, 'w', encoding='utf-8') as f:
            f.write(DUMMY_COVERAGE)

    def test_quality_panel_shows_percentages(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('admin_quality'))
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        # 0.621 -> 62.1% (aceita ponto); 0.512 -> 51.2%
        self.assertIn('62.1%', html)
        self.assertIn('51.2%', html)
        # Métricas adicionais
        self.assertIn('Linhas', html)
        # Badge de sucesso (>=50%)
        self.assertIn('bg-success', html)

    def test_quality_panel_missing_file(self):
        # Remove arquivo para simular ausência
        coverage_path = os.path.join(settings.BASE_DIR, 'harmony_pets', 'coverage.xml')
        if os.path.exists(coverage_path):
            os.remove(coverage_path)
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('admin_quality'))
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn('coverage.xml não encontrado', html)
        # Sem histórico exibido
        self.assertNotIn('Histórico recente', html)
