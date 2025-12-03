from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
import logging
logger = logging.getLogger('core')

class Command(BaseCommand):
    help = "Dispara fluxo de password reset usando rota estilizada e mostra resultado no backend console."

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='E-mail do usuário alvo (default: admin@example.com)')

    def handle(self, *args, **options):
        User = get_user_model()
        email = options.get('email') or 'admin@example.com'
        user = User.objects.filter(email=email).first()
        if not user:
            self.stdout.write(self.style.WARNING(f'Usuário com email {email} não existe, criando admin padrão.'))
            user = User.objects.create_superuser('admin', email, 'admin123')
        c = Client()
        # Usa a rota padrão para garantir subject do template PT-BR
        resp = c.post(reverse('password_reset'), {'email': email})
        if resp.status_code in (200,302):
            self.stdout.write(self.style.SUCCESS('Solicitação de reset enviada. Verifique console ou backend SMTP.'))
        else:
            self.stdout.write(self.style.ERROR(f'Falha no envio: status {resp.status_code}'))
        # Log origem template
        from django.template import engines
        html_tpl = engines['django'].get_template('registration/core_password_reset_email.html')
        subj_tpl = engines['django'].get_template('registration/core_password_reset_subject.txt')
        logger.info('Template HTML carregado em: %s', html_tpl.origin.name)
        logger.info('Template Subject carregado em: %s', subj_tpl.origin.name)
        self.stdout.write(f'Template HTML: {html_tpl.origin.name}')
        self.stdout.write(f'Template Subject: {subj_tpl.origin.name}')
