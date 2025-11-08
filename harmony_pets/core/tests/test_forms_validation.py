from django.test import TestCase
from django.contrib.auth.models import User
from core.forms import InteressadoAdocaoForm, LocalAdocaoForm, PetForm, ChangePasswordForm
from core.models import LocalAdocao, Pet


class FormsValidationTests(TestCase):
    def test_interessado_form_invalid_cpf(self):
        form = InteressadoAdocaoForm(data={
            'username': 'u1',
            'password1': 'SenhaForte123',
            'password2': 'SenhaForte123',
            'first_name': 'Ana',
            'last_name': 'Silva',
            'email': 'ana@example.com',
            'cpf': '000.000.000-00',  # inválido (sequência)
        })
        self.assertFalse(form.is_valid())
        self.assertIn('cpf', form.errors)

    def test_interessado_form_valid(self):
        # CPF qualquer não sequencial com 11 dígitos passa na validação leve do model
        # CPF válido com dígitos verificadores corretos
        form = InteressadoAdocaoForm(data={
            'username': 'u2',
            'password1': 'SenhaForte123',
            'password2': 'SenhaForte123',
            'first_name': 'Joao',
            'last_name': 'Souza',
            'email': 'joao@example.com',
            'cpf': '529.982.247-25',
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, 'u2')

    def test_local_form_invalid_cnpj(self):
        form = LocalAdocaoForm(data={
            'username': 'org1',
            'password1': 'SenhaForte123',
            'password2': 'SenhaForte123',
            'first_name': 'Org',
            'last_name': 'Teste',
            'email': 'org1@example.com',
            'cnpj': '00.000.000/0000-00',  # inválido (sequência)
        })
        self.assertFalse(form.is_valid())
        self.assertIn('cnpj', form.errors)

    def test_pet_form_auto_emoji(self):
        # Criar local para relação
        u_local = User.objects.create_user('org', 'org@example.com', 'SenhaForte123')
        local = LocalAdocao.objects.create(usuario=u_local, cnpj='12345678000199')
        form = PetForm(data={
            'nome': 'Mimi',
            'especie': 'gato',
            'idade': 6,
            'sexo': 'femea',
            'porte': 'pequeno',
            'descricao': 'Filhote brincalhão',
            # Sem emoji explícito para testar auto preenchimento
        })
        # Ajusta local para ter lat/long antes de validar
        local.latitude = -10.0
        local.longitude = -50.0
        local.save()
        # Vincula via instance para permitir fallback do clean
        pet_instance = Pet(local_adocao=local)
        form.instance = pet_instance
        self.assertTrue(form.is_valid(), form.errors)
        pet = form.save(commit=False)
        pet.local_adocao = local
        pet.save()
        self.assertEqual(pet.emoji, '🐱')

    def test_change_password_form(self):
        user = User.objects.create_user('userx', 'userx@example.com', 'SenhaAntiga123')
        form = ChangePasswordForm(user=user, data={
            'current_password': 'SenhaAntiga123',
            'new_password1': 'NovaSenhaSegura123',
            'new_password2': 'NovaSenhaSegura123',
        })
        self.assertTrue(form.is_valid(), form.errors)
        user.set_password(form.cleaned_data['new_password2'])
        user.save()
        self.assertTrue(user.check_password('NovaSenhaSegura123'))
