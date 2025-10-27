from django.test import TestCase
from django.contrib.auth.models import User
from core.models import TwoFactorAuth
import pyotp


class TwoFactorAuthModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tfuser', password='pw', email='tf@example.com')
        self.tfa = TwoFactorAuth.objects.create(usuario=self.user)

    def test_secret_key_generated_and_totp_uri(self):
        # save() should populate secret_key if empty
        self.assertIsNotNone(self.tfa.secret_key)
        uri = self.tfa.get_totp_uri()
        self.assertIn('otpauth://', uri)

    def test_verify_token_with_valid_totp(self):
        # gerar token usando pyotp com a mesma secret
        totp = pyotp.TOTP(self.tfa.secret_key)
        token = totp.now()
        self.assertTrue(self.tfa.verify_token(token))

    def test_backup_codes_generate_and_verify(self):
        codes = self.tfa.generate_backup_codes()
        self.assertEqual(len(codes), 10)
        code = codes[0]
        # verify_backup_code deve retornar True na primeira vez e False depois
        self.assertTrue(self.tfa.verify_backup_code(code))
        self.assertFalse(self.tfa.verify_backup_code(code))
