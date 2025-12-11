from django.test import SimpleTestCase
from core.utils import mask_sensitive


class MaskSensitiveTests(SimpleTestCase):
    def test_mask_email_preserves_separators(self):
        original = "usuario.exemplo@mail.com"
        masked = mask_sensitive(original, preserve_chars='@.')
        # mantém '@' e '.'
        self.assertIn('@', masked)
        self.assertIn('.', masked)
        # mesmo comprimento
        self.assertEqual(len(masked), len(original))
        # pelo menos um '*' presente
        self.assertTrue('*' in masked)

    def test_mask_cpf_format(self):
        original = '123.456.789-00'
        masked = mask_sensitive(original, preserve_chars='.-')
        # pontos e traço preservados
        self.assertEqual(masked[3], '.')
        self.assertEqual(masked[7], '.')
        self.assertEqual(masked[11], '-')
        self.assertEqual(len(masked), len(original))

    def test_mask_none_returns_none(self):
        self.assertIsNone(mask_sensitive(None))
