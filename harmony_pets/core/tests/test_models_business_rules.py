from django.test import TestCase
from django.contrib.auth.models import User
from core.models import UserLoginAttempt, LocalAdocao, Pet, InteressadoAdocao, TwoFactorAuth, AceitacaoTermos
from django.utils import timezone
from datetime import timedelta
import pyotp


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


class TwoFactorAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password')
        self.two_fa = TwoFactorAuth.objects.create(usuario=self.user, is_enabled=True)

    def test_verify_token(self):
        valid_token = pyotp.TOTP(self.two_fa.secret_key).now()
        self.assertTrue(self.two_fa.verify_token(valid_token))
        self.assertFalse(self.two_fa.verify_token('123456'))

    def test_verify_token_invalid(self):
        invalid_token = '000000'
        self.assertFalse(self.two_fa.verify_token(invalid_token))

    def test_verify_token_expired(self):
        expired_token = pyotp.TOTP(self.two_fa.secret_key).now()
        # Simular expiração com atraso
        import time
        time.sleep(61)  # Aguardar mais que a janela de tolerância (60s)
        self.assertFalse(self.two_fa.verify_token(expired_token))

    def test_verify_backup_code(self):
        self.two_fa.backup_codes = ['CODE1234']
        self.two_fa.save()
        self.assertTrue(self.two_fa.verify_backup_code('CODE1234'))
        self.assertFalse(self.two_fa.verify_backup_code('INVALID'))

    def test_generate_backup_codes(self):
        codes = self.two_fa.generate_backup_codes()
        self.assertEqual(len(codes), 10)
        self.assertTrue(all(len(code) == 16 for code in codes))

    def test_generate_backup_codes_overwrite(self):
        self.two_fa.backup_codes = ['OLD_CODE']
        new_codes = self.two_fa.generate_backup_codes()
        self.assertNotIn('OLD_CODE', new_codes)
        self.assertEqual(len(new_codes), 10)

    def test_get_totp_uri(self):
        uri = self.two_fa.get_totp_uri()
        self.assertIn('otpauth://totp/', uri)
        self.assertIn('Harmony%20Pets', uri)

    def test_get_qr_code(self):
        qr_code = self.two_fa.get_qr_code()
        self.assertTrue(qr_code.startswith('iVBOR'))  # Base64 PNG header


class AceitacaoTermosTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password')
        self.termos = AceitacaoTermos.objects.create(
            usuario=self.user, termos_aceitos=True, lgpd_aceito=True,
            ip_aceitacao='127.0.0.1', user_agent='TestAgent'
        )

    def test_termos_completos_aceitos(self):
        self.assertTrue(self.termos.termos_completos_aceitos)
        self.termos.lgpd_aceito = False
        self.assertFalse(self.termos.termos_completos_aceitos)

    def test_termos_completos_aceitos_combinacoes(self):
        self.termos.termos_aceitos = False
        self.assertFalse(self.termos.termos_completos_aceitos)
        self.termos.termos_aceitos = True
        self.termos.lgpd_aceito = False
        self.assertFalse(self.termos.termos_completos_aceitos)
        self.termos.lgpd_aceito = True
        self.assertTrue(self.termos.termos_completos_aceitos)


class InteressadoAdocaoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='interessado', password='password')

    def test_valid_cpf(self):
        interessado = InteressadoAdocao.objects.create(
            usuario=self.user, cpf='123.456.789-09'
        )
        self.assertEqual(interessado.cpf, '123.456.789-09')

    def test_invalid_cpf(self):
        with self.assertRaises(Exception):
            InteressadoAdocao.objects.create(
                usuario=self.user, cpf='000.000.000-00'
            )


class LocalAdocaoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='local', password='password')

    def test_valid_cnpj(self):
        local = LocalAdocao.objects.create(
            usuario=self.user, cnpj='12.345.678/0001-99'
        )
        self.assertEqual(local.cnpj, '12.345.678/0001-99')

    def test_invalid_cnpj(self):
        with self.assertRaises(Exception):
            LocalAdocao.objects.create(
                usuario=self.user, cnpj='00.000.000/0000-00'
            )
