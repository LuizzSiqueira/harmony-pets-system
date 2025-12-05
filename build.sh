#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Navegar para o diretório do Django
cd harmony_pets

# Coletar arquivos estáticos
python manage.py collectstatic --no-input

# Executar migrações
python manage.py migrate

# Criar superusuário se não existir (opcional)
# python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@harmonypets.com', 'senha_segura_aqui')"
