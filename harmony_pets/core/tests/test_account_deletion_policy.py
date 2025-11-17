from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user
from core.models import AceitacaoTermos


class AccountDeletionPolicyTests(TestCase):
    def setUp(self):
        self.username = 'user_delete'
        self.password = 'pass123456'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        # Criar aceite de termos para não ser bloqueado pelo middleware
        AceitacaoTermos.objects.create(
            usuario=self.user,
            termos_aceitos=True,
            lgpd_aceito=True,
            ip_aceitacao='127.0.0.1',
            user_agent='test-client',
            versao_termos='1.0'
        )

    @override_settings(ACCOUNT_DELETION_ENABLED=False)
    def test_delete_option_hidden_and_post_blocked_when_disabled(self):
        self.client.force_login(self.user)
        # GET perfil: botão/form não deve renderizar (sem action para delete_account)
        resp = self.client.get(reverse('profile'))
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(reverse('delete_account'), resp.content.decode())
        # POST tentativa de exclusão: deve ser redirecionado e usuário continuar existindo
        resp_post = self.client.post(reverse('delete_account'), {})
        self.assertEqual(resp_post.status_code, 302)
        self.assertTrue(User.objects.filter(username=self.username).exists())

    @override_settings(ACCOUNT_DELETION_ENABLED=True)
    def test_post_without_confirmation_does_not_delete(self):
        self.client.force_login(self.user)
        resp_post = self.client.post(reverse('delete_account'), {})
        # deve redirecionar de volta ao perfil e manter o usuário
        self.assertEqual(resp_post.status_code, 302)
        self.assertIn(reverse('profile'), resp_post.url)
        self.assertTrue(User.objects.filter(username=self.username).exists())

    @override_settings(ACCOUNT_DELETION_ENABLED=True)
    def test_post_with_confirmation_deletes_and_redirects_home(self):
        self.client.force_login(self.user)
        resp_post = self.client.post(reverse('delete_account'), {'confirm_delete': 'on'})
        # deve redirecionar para home e remover usuário
        self.assertEqual(resp_post.status_code, 302)
        self.assertIn(reverse('home'), resp_post.url)
        self.assertFalse(User.objects.filter(username=self.username).exists())
