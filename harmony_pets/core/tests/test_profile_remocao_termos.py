from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import AceitacaoTermos

class ProfileRemocaoTermosTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='perfiluser', password='secret123')
        AceitacaoTermos.objects.create(
            usuario=self.user,
            termos_aceitos=True,
            lgpd_aceito=True,
            ip_aceitacao='127.0.0.1',
            user_agent='test',
            versao_termos='1.0'
        )

    def test_location_card_removed_and_removal_card_present(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('profile'))
        html = resp.content.decode()
        # Verifica que o texto de localização não está mais presente
        self.assertNotIn('Atualizar minha localização', html)
        self.assertNotIn('Usar minha localização', html)
        # Verifica presença do novo quadro de remoção conforme termos
        self.assertIn('Remoção de Conta conforme Termos', html)
        self.assertIn(reverse('aceitar_termos'), html)
        self.assertIn(reverse('recusar_termos'), html)
        self.assertIn(reverse('contato'), html)
