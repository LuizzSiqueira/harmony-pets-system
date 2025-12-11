from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import AceitacaoTermos


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class BasicViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_status_ok(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)

    def test_register_redirects_without_terms(self):
        resp = self.client.get(reverse('register'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('aceitar_termos'), resp['Location'])

    def test_aceitar_termos_post_anonymous_sets_session_and_redirects(self):
        resp = self.client.post(
            reverse('aceitar_termos'),
            data={'termos_uso': 'on', 'lgpd': 'on'},
            follow=False,
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('register'), resp['Location'])
        # sessão deve conter flag de termos
        session = self.client.session
        self.assertIn('termos_aceitos', session)
        self.assertTrue(session['termos_aceitos']['termos_uso'])
        self.assertTrue(session['termos_aceitos']['lgpd'])

    def test_terms_middleware_redirects_when_logged_user_without_terms(self):
        user = User.objects.create_user(username='u1', password='pass12345', email='u1@example.com')
        self.client.login(username='u1', password='pass12345')
        # Acessar página protegida deve redirecionar para aceitar_termos por middleware
        resp = self.client.get(reverse('profile'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('aceitar_termos'), resp['Location'])

    def test_logged_user_with_terms_can_access_profile(self):
        user = User.objects.create_user(username='u2', password='pass12345', email='u2@example.com')
        # Criar aceitação de termos para não redirecionar
        AceitacaoTermos.objects.create(
            usuario=user,
            termos_aceitos=True,
            lgpd_aceito=True,
            ip_aceitacao='127.0.0.1',
            user_agent='test-agent',
            versao_termos='1.0',
        )
        self.client.login(username='u2', password='pass12345')
        resp = self.client.get(reverse('profile'))
        # Pode redirecionar para 2FA caso esteja ativo, então checamos não ser redirect para aceitar_termos
        if resp.status_code == 302:
            self.assertNotIn(reverse('aceitar_termos'), resp['Location'])
        else:
            self.assertEqual(resp.status_code, 200)
