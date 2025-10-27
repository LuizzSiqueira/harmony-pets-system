from django.test import TestCase
from django.contrib.auth.models import User
from core.models import UserLoginAttempt, LocalAdocao, Pet
from django.utils import timezone
from datetime import timedelta


class UserLoginAttemptTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password')
        self.attempt = UserLoginAttempt.objects.create(user=self.user)

    def test_block_and_is_blocked(self):
        # Initially not blocked
        self.assertFalse(self.attempt.is_blocked())
        # Block for 1 minute
        self.attempt.block(minutes=1)
        self.assertTrue(self.attempt.is_blocked())
        # Simulate time after blocked_until
        self.attempt.blocked_until = timezone.now() - timedelta(minutes=5)
        self.attempt.save()
        self.assertFalse(self.attempt.is_blocked())

    def test_reset_attempts_clears_block(self):
        self.attempt.failed_attempts = 3
        self.attempt.block(minutes=10)
        self.attempt.reset_attempts()
        self.assertEqual(self.attempt.failed_attempts, 0)
        self.assertIsNone(self.attempt.blocked_until)


class PetBusinessRuleTests(TestCase):
    def setUp(self):
        # Criar usuario e local para relacionamentos obrigatórios
        u = User.objects.create_user(username='localuser', password='pw')
        local = LocalAdocao.objects.create(usuario=u, cnpj='12.345.678/0001-99')

        self.local = local

    def test_get_idade_display_meses(self):
        pet = Pet.objects.create(
            nome='Rex', especie='cao', idade=6, sexo='macho', porte='medio',
            descricao='Um cãozinho', local_adocao=self.local
        )
        self.assertEqual(pet.get_idade_display(), '6 meses')

    def test_get_idade_display_anos_e_meses(self):
        pet = Pet.objects.create(
            nome='Mimi', especie='gato', idade=26, sexo='femea', porte='pequeno',
            descricao='Gatinha', local_adocao=self.local
        )
        # 26 meses = 2 anos e 2 meses
        self.assertIn('2 ano', pet.get_idade_display())
        self.assertIn('2 meses', pet.get_idade_display())

    def test_get_idade_display_anos_exato(self):
        pet = Pet.objects.create(
            nome='Ze', especie='cao', idade=24, sexo='macho', porte='grande',
            descricao='Cachorro adulto', local_adocao=self.local
        )
        self.assertIn('2 ano', pet.get_idade_display())
        self.assertNotIn('meses', pet.get_idade_display())
