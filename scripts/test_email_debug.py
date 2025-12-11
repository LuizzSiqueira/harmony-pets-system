import os
import sys

# Configurar Django
sys.path.insert(0, 'harmony_pets')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'harmony_pets.settings')

# Forçar banco local
os.environ['USE_DB'] = 'local'

import django
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

print('=== DIAGNÓSTICO DE E-MAIL ===\n')
print(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
print(f'EMAIL_HOST: {settings.EMAIL_HOST}')
print(f'EMAIL_PORT: {settings.EMAIL_PORT}')
print(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
print(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
print(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
print()

# Simular contexto
context = {
    'user': type('obj', (object,), {'first_name': 'Teste', 'username': 'teste'}),
    'uid': 'test123',
    'token': 'token123',
    'uidb64': 'test123',
    'domain': '127.0.0.1:8000',
    'protocol': 'http',
    'site_name': 'Harmony Pets',
}

print('=== RENDERIZANDO TEMPLATES ===\n')
try:
    from django.template import loader
    subject_template = loader.get_template('registration/password_reset_subject.txt')
    text_template = loader.get_template('registration/password_reset_email.txt')
    html_template = loader.get_template('registration/password_reset_email.html')
    
    subject = subject_template.render(context).strip()
    text_body = text_template.render(context)
    html_body = html_template.render(context)
    
    print(f'[OK] Subject: {subject}')
    print(f'[OK] Text body: {len(text_body)} caracteres')
    print(f'[OK] HTML body: {len(html_body)} caracteres')
    print()
    
    # Mostrar primeiras linhas do HTML
    print('=== PREVIEW HTML (primeiras 500 chars) ===\n')
    print(html_body[:500])
    print('...\n')
    
except Exception as e:
    print(f'✗ ERRO ao renderizar templates: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('=== CRIANDO MENSAGEM ===\n')
try:
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=['central.seguranca.app@gmail.com']
    )
    message.attach_alternative(html_body, 'text/html')
    
    print(f'✓ From: {message.from_email}')
    print(f'✓ To: {message.to}')
    print(f'✓ Subject: {message.subject}')
    print(f'✓ Body type: {type(message.body)}')
    print(f'✓ Alternatives: {len(message.alternatives)} attached')
    if message.alternatives:
        print(f'  - Type: {message.alternatives[0][1]}')
        print(f'  - Length: {len(message.alternatives[0][0])} chars')
    print()
    
except Exception as e:
    print(f'✗ ERRO ao criar mensagem: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('=== ENVIANDO E-MAIL ===\n')
try:
    result = message.send()
    print(f'✓ E-mail enviado com sucesso!')
    print(f'  Result code: {result}')
except Exception as e:
    print(f'✗ ERRO ao enviar: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
