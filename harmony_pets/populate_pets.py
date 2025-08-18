#!/usr/bin/env python
"""
Script para popular o banco de dados com pets de exemplo
Execute: python manage.py shell < populate_pets.py
"""

from core.models import Pet, LocalAdocao
from django.contrib.auth.models import User

# Buscar um local de adoção existente ou criar um genérico
try:
    local = LocalAdocao.objects.first()
    if not local:
        # Criar um usuário e local de exemplo
        user_local = User.objects.create_user(
            username='exemplo_ong',
            email='contato@exemploong.com',
            first_name='ONG',
            last_name='Exemplo'
        )
        local = LocalAdocao.objects.create(
            usuario=user_local,
            cnpj='12345678000195',
            nome_fantasia='ONG Amor aos Animais',
            telefone='(11) 99999-9999',
            endereco='Rua das Flores, 123 - São Paulo, SP'
        )
except Exception as e:
    print(f"Erro ao criar local: {e}")
    exit()

# Lista de pets para criar
pets_data = [
    {
        'nome': 'Luna',
        'especie': 'cao',
        'raca': 'Vira-lata',
        'idade': 24,
        'sexo': 'femea',
        'porte': 'medio',
        'cor': 'Marrom e branco',
        'peso': 12.5,
        'castrado': True,
        'vacinado': True,
        'vermifugado': True,
        'docil': True,
        'brincalhao': True,
        'calmo': False,
        'descricao': 'Luna é uma cadela super carinhosa e brincalhona. Adora passear e brincar com bolinhas. É muito sociável com outros cães e crianças.',
        'emoji': '🐕',
        'status': 'disponivel'
    },
    {
        'nome': 'Miau',
        'especie': 'gato',
        'raca': 'Siamês',
        'idade': 18,
        'sexo': 'macho',
        'porte': 'pequeno',
        'cor': 'Creme e marrom',
        'peso': 4.2,
        'castrado': True,
        'vacinado': True,
        'vermifugado': True,
        'docil': True,
        'brincalhao': False,
        'calmo': True,
        'descricao': 'Miau é um gato muito tranquilo e carinhoso. Gosta de cochilar no sol e fazer cafuné. Perfeito para apartamentos.',
        'emoji': '🐱',
        'status': 'disponivel'
    },
    {
        'nome': 'Rex',
        'especie': 'cao',
        'raca': 'Pastor Alemão',
        'idade': 36,
        'sexo': 'macho',
        'porte': 'grande',
        'cor': 'Preto e marrom',
        'peso': 28.0,
        'castrado': True,
        'vacinado': True,
        'vermifugado': True,
        'docil': True,
        'brincalhao': True,
        'calmo': False,
        'descricao': 'Rex é um cão leal e protetor. Muito inteligente e obediente. Ideal para famílias com quintal grande.',
        'emoji': '🐕',
        'status': 'disponivel'
    },
    {
        'nome': 'Nila',
        'especie': 'gato',
        'raca': 'Persa',
        'idade': 12,
        'sexo': 'femea',
        'porte': 'pequeno',
        'cor': 'Cinza',
        'peso': 3.8,
        'castrado': True,
        'vacinado': True,
        'vermifugado': True,
        'docil': True,
        'brincalhao': False,
        'calmo': True,
        'descricao': 'Nila é uma gatinha muito dócil e carinhosa. Adora colo e é perfeita para quem busca companhia tranquila.',
        'emoji': '🐱',
        'status': 'disponivel'
    },
    {
        'nome': 'Bolinha',
        'especie': 'hamster',
        'raca': 'Sírio',
        'idade': 8,
        'sexo': 'macho',
        'porte': 'pequeno',
        'cor': 'Dourado',
        'peso': 0.12,
        'castrado': False,
        'vacinado': False,
        'vermifugado': True,
        'docil': True,
        'brincalhao': True,
        'calmo': False,
        'descricao': 'Bolinha é um hamster super ativo e divertido. Adora correr na rodinha e explorar tubinhos.',
        'emoji': '🐹',
        'status': 'disponivel'
    },
    {
        'nome': 'Mel',
        'especie': 'coelho',
        'raca': 'Mini Lop',
        'idade': 15,
        'sexo': 'femea',
        'porte': 'pequeno',
        'cor': 'Branco e marrom',
        'peso': 1.5,
        'castrado': True,
        'vacinado': True,
        'vermifugado': True,
        'docil': True,
        'brincalhao': True,
        'calmo': True,
        'descricao': 'Mel é uma coelhinha muito meiga e carinhosa. Gosta de cenouras e de fazer pequenos pulos pela casa.',
        'emoji': '🐰',
        'status': 'disponivel'
    }
]

# Criar os pets
created_count = 0
for pet_data in pets_data:
    try:
        # Verificar se já existe um pet com esse nome
        if not Pet.objects.filter(nome=pet_data['nome']).exists():
            Pet.objects.create(
                local_adocao=local,
                **pet_data
            )
            created_count += 1
            print(f"Pet {pet_data['nome']} criado com sucesso!")
        else:
            print(f"Pet {pet_data['nome']} já existe.")
    except Exception as e:
        print(f"Erro ao criar pet {pet_data['nome']}: {e}")

print(f"\n✅ {created_count} pets criados com sucesso!")
print(f"Total de pets no sistema: {Pet.objects.count()}")
