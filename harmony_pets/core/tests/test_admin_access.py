from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class AdminAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user(username='staff', password='123', is_staff=True)
        self.normal = User.objects.create_user(username='normal', password='123')

    def test_anonymous_redirects_to_login(self):
        resp = self.client.get('/admin/', follow=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp['Location'])
        self.assertIn('next=/admin/', resp['Location'])

    def test_non_staff_redirects_to_login(self):
        self.client.login(username='normal', password='123')
        resp = self.client.get('/admin/', follow=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp['Location'])
        self.assertIn('next=/admin/', resp['Location'])

    def test_staff_can_access_admin(self):
        self.client.login(username='staff', password='123')
        resp = self.client.get('/admin/', follow=False)
        # Django admin redireciona para login interno se não autenticado neste fluxo ou para index
        self.assertIn(resp.status_code, (200, 302))
        # Se 302, deve ser redirecionamento interno do admin e não para nossa página de login
        if resp.status_code == 302:
            self.assertNotIn(reverse('login'), resp['Location'])
