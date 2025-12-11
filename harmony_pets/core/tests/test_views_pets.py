from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import LocalAdocao, InteressadoAdocao, Pet, SolicitacaoAdocao, AceitacaoTermos


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PetsViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Usuário org/local com termos aceitos
        self.user_local = User.objects.create_user('org', 'org@example.com', 'pass12345')
        AceitacaoTermos.objects.create(
            usuario=self.user_local,
            termos_aceitos=True,
            lgpd_aceito=True,
            ip_aceitacao='127.0.0.1',
            user_agent='test',
            versao_termos='1.0',
        )
        self.local = LocalAdocao.objects.create(
            usuario=self.user_local,
            cnpj='12345678000199',
            nome_fantasia='Lar Feliz',
            latitude=-23.5,
            longitude=-46.6,
        )
        self.pet = Pet.objects.create(
            nome='Rex',
            especie='cao',
            raca='Vira-lata',
            idade=24,
            sexo='macho',
            porte='medio',
            cor='caramelo',
            descricao='Um bom garoto',
            local_adocao=self.local,
            status='disponivel',
        )

    def test_pets_list_ok(self):
        resp = self.client.get(reverse('pets_list'))
        self.assertEqual(resp.status_code, 200)
        # Deve listar pelo menos nosso pet na página
        self.assertContains(resp, 'Rex')

    def test_pet_detail_ok(self):
        resp = self.client.get(reverse('pet_detail', args=[self.pet.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Rex')

    def test_solicitar_adocao_requires_interessado(self):
        # Loga usuário comum (sem perfil de interessado)
        self.client.login(username='org', password='pass12345')
        resp = self.client.get(reverse('solicitar_adocao', args=[self.pet.id]))
        # Middleware de 2FA pode interferir; garantimos que redirecione ao detalhe com mensagem
        # A view faz redirect para pet_detail quando não é interessado
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('pet_detail', args=[self.pet.id]), resp['Location'])

    def test_solicitar_adocao_post_success(self):
        # Cria usuário interessado com termos aceitos e loga
        u_int = User.objects.create_user('int', 'int@example.com', 'pass12345')
        AceitacaoTermos.objects.create(
            usuario=u_int,
            termos_aceitos=True,
            lgpd_aceito=True,
            ip_aceitacao='127.0.0.1',
            user_agent='test',
            versao_termos='1.0',
        )
        InteressadoAdocao.objects.create(usuario=u_int, cpf='12345678901')
        self.client.login(username='int', password='pass12345')

        resp = self.client.post(
            reverse('solicitar_adocao', args=[self.pet.id]),
            data={
                'motivo': 'Quero adotar',
                'experiencia_pets': 'Já tive cães',
                'situacao_moradia': 'Casa com quintal',
            },
        )
        # Deve redirecionar de volta ao detalhe
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('pet_detail', args=[self.pet.id]), resp['Location'])

        self.assertTrue(
            SolicitacaoAdocao.objects.filter(pet=self.pet, interessado__usuario__username='int').exists()
        )
