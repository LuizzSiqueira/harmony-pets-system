# Buscar ou criar local de adoção genérico para pets de SP (deve estar antes do bloco de criação dos pets)
user_sp, _ = User.objects.get_or_create(
    username='ong_sp',
    defaults={
        'email': 'contato@ongsp.com',
        'first_name': 'ONG',
        'last_name': 'SP',
    }
)
local_sp, _ = LocalAdocao.objects.get_or_create(
    usuario=user_sp,
    defaults={
        'cnpj': '00000000000100',
        'nome_fantasia': 'ONG SP Genérica',
        'telefone': '(11) 90000-0000',
        'endereco': 'São Paulo, SP',
        'latitude': -23.5505,
        'longitude': -46.6333
    }
)
from core.utils import geocodificar_endereco

# --- ONG e pet de teste em Mogi das Cruzes ---
try:
    user_mogi, _ = User.objects.get_or_create(
        username='ong_mogi',
        defaults={
            'email': 'contato@ongmogi.com',
            'first_name': 'ONG',
            'last_name': 'Mogi',
        }
    )
    endereco_mogi = 'Av. Voluntário Fernando Pinheiro Franco, 350 - Centro, Mogi das Cruzes, SP'
    from core.utils import geocodificar_endereco
    latlng_mogi = geocodificar_endereco(endereco_mogi)
    local_mogi, _ = LocalAdocao.objects.get_or_create(
        usuario=user_mogi,
        defaults={
            'cnpj': '0000000000099',
            'nome_fantasia': 'ONG Mogi Pet',
            'telefone': '(11) 90099-0000',
            'endereco': endereco_mogi,
            'latitude': latlng_mogi[0] if latlng_mogi else None,
            'longitude': latlng_mogi[1] if latlng_mogi else None
        }
    )
    if not Pet.objects.filter(nome='Pet Mogi').exists():
        Pet.objects.create(
            nome='Pet Mogi',
            especie='cao',
            raca='SRD',
            idade=10,
            sexo='femea',
            porte='pequeno',
            cor='Caramelo',
            peso=8.0,
            castrado=True,
            vacinado=True,
            vermifugado=True,
            docil=True,
            brincalhao=True,
            calmo=True,
            descricao='Pet de teste para ONG Mogi das Cruzes.',
            emoji='🐶',
            status='disponivel',
            local_adocao=local_mogi
        )
        print("Pet de teste 'Pet Mogi' criado para ONG Mogi das Cruzes.")
except Exception as e:
    print(f"Erro ao criar ONG/pet de Mogi das Cruzes: {e}")
#!/usr/bin/env python
"""
Script para popular o banco de dados com pets de exemplo
Execute: python manage.py shell < populate_pets.py
"""

from django.db import transaction
from core.models import Pet, LocalAdocao
from django.contrib.auth.models import User


# Remover todos os pets e locais de adoção (e usuários relacionados a locais)
with transaction.atomic():
    print('Removendo todos os pets, locais de adoção e usuários relacionados...')
    Pet.objects.all().delete()
    for local in LocalAdocao.objects.all():
        if hasattr(local, 'usuario'):
            local.usuario.delete()
        local.delete()
    print('Remoção concluída.')

# Agora criar user_sp e local_sp após a limpeza
user_sp, _ = User.objects.get_or_create(
    username='ong_sp',
    defaults={
        'email': 'contato@ongsp.com',
        'first_name': 'ONG',
        'last_name': 'SP',
    }
)
local_sp, _ = LocalAdocao.objects.get_or_create(
    usuario=user_sp,
    defaults={
        'cnpj': '00000000000100',
        'nome_fantasia': 'ONG SP Genérica',
        'telefone': '(11) 90000-0000',
        'endereco': 'São Paulo, SP',
        'latitude': -23.5505,
        'longitude': -46.6333
    }
)

import os
from core.models import Pet, LocalAdocao
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files import File

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
        endereco = 'Rua das Flores, 123 - São Paulo, SP'
        latlng = geocodificar_endereco(endereco)
        local = LocalAdocao.objects.create(
            usuario=user_local,
            cnpj='12345678000195',
            nome_fantasia='ONG Amor aos Animais',
            telefone='(11) 99999-9999',
            endereco=endereco,
            latitude=latlng[0] if latlng else None,
            longitude=latlng[1] if latlng else None
        )
except Exception as e:
    print(f"Erro ao criar local: {e}")
    exit()

IMAGES_PATH = os.path.join(
    os.path.dirname(__file__),
    'core', 'static', 'core', 'images', 'pets'
)

# Lista de imagens para associar aos pets (ordem deve bater com pets_data)
images_files = [
    'dog1.jpg',  # Luna
    'cat1.jpg',  # Miau
    'dog2.jpg',  # Rex
    'cat2.jpg',  # Nila
    'hamster1.jpg',  # Bolinha
    'rabbit1.jpg',   # Mel
]

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

for idx, pet_data in enumerate(pets_data):
    try:
        # Verificar se já existe um pet com esse nome
        if not Pet.objects.filter(nome=pet_data['nome']).exists():
            pet_kwargs = pet_data.copy()
            # Adiciona imagem se ativado e arquivo existir
            if getattr(settings, 'POPULATE_PETS_WITH_IMAGES', False):
                if idx < len(images_files):
                    image_path = os.path.join(IMAGES_PATH, images_files[idx])
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as img_file:
                            pet_kwargs['foto'] = File(img_file, name=images_files[idx])
            Pet.objects.create(
                local_adocao=local,
                **pet_kwargs
            )
            created_count += 1
            print(f"Pet {pet_data['nome']} criado com sucesso!")
        else:
            print(f"Pet {pet_data['nome']} já existe.")
    except Exception as e:
        print(f"Erro ao criar pet {pet_data['nome']}: {e}")

print(f"\n✅ {created_count} pets criados com sucesso!")
print(f"Total de pets no sistema: {Pet.objects.count()}")

# --- Adiciona pets com diferentes locais de adoção para teste de distância ---
from django.db import transaction

novos_locais = [
    {
        'username': 'ong_rio',
        'email': 'contato@ongrio.com',
        'nome_fantasia': 'ONG Rio Pet',
        'endereco': 'Av. Atlântica, 1702 - Copacabana, Rio de Janeiro, RJ',
    },
    {
        'username': 'ong_bh',
        'email': 'contato@ongbh.com',
        'nome_fantasia': 'ONG BH Animal',
        'endereco': 'Praça Sete de Setembro, Centro, Belo Horizonte, MG',
    },
    {
        'username': 'ong_curitiba',
        'email': 'contato@ongcuritiba.com',
        'nome_fantasia': 'ONG Curitiba Bicho',
        'endereco': 'Rua XV de Novembro, 1000 - Centro, Curitiba, PR',
    },
    {
        'username': 'ong_salvador',
        'email': 'contato@ongsalvador.com',
        'nome_fantasia': 'ONG Salvador Pet',
        'endereco': 'Av. Sete de Setembro, 2000 - Salvador, BA',
    },
]

with transaction.atomic():
    for idx, local_data in enumerate(novos_locais):
        user, _ = User.objects.get_or_create(
            username=local_data['username'],
            defaults={
                'email': local_data['email'],
                'first_name': local_data['nome_fantasia'].split()[0],
                'last_name': local_data['nome_fantasia'].split()[-1],
            }
        )
        endereco = local_data['endereco']
        latlng = geocodificar_endereco(endereco)
        local, _ = LocalAdocao.objects.get_or_create(
            usuario=user,
            defaults={
                'cnpj': f'00000000000{idx+2}',
                'nome_fantasia': local_data['nome_fantasia'],
                'telefone': f'(11) 9000{idx+2}-0000',
                'endereco': endereco,
                'latitude': latlng[0] if latlng else None,
                'longitude': latlng[1] if latlng else None
            }
        )
        pet_nome = f"Pet Teste {idx+1}"
        if not Pet.objects.filter(nome=pet_nome).exists():
            Pet.objects.create(
                nome=pet_nome,
                especie='cao',
                raca='SRD',
                idade=12,
                sexo='macho',
                porte='medio',
                cor='Preto',
                peso=10.0,
                castrado=True,
                vacinado=True,
                vermifugado=True,
                docil=True,
                brincalhao=True,
                calmo=False,
                descricao=f'Pet de teste para {local_data["nome_fantasia"]}',
                emoji='🐶',
                status='disponivel',
                local_adocao=local
            )
            print(f"Pet de teste '{pet_nome}' criado para {local_data['nome_fantasia']}.")

# --- Adiciona pets com localização individual (latitude/longitude) em Mogi das Cruzes e cidades próximas de SP ---
import random
localizacoes_sp = [
    # Mogi das Cruzes
    (-23.5225, -46.1884),
    (-23.5200, -46.1850),
    (-23.5260, -46.1900),
    # São Paulo
    (-23.5505, -46.6333),
    (-23.5596, -46.7314),
    (-23.5489, -46.6388),
    # Guarulhos
    (-23.4545, -46.5333),
    # Suzano
    (-23.5428, -46.3108),
    # Poá
    (-23.5333, -46.3500),
    # Itaquaquecetuba
    (-23.4867, -46.3483),
    # Ferraz de Vasconcelos
    (-23.5411, -46.3719),
    # Arujá
    (-23.3964, -46.3200),
    # São Bernardo do Campo
    (-23.6914, -46.5646),
    # Santo André
    (-23.6639, -46.5383),
    # Osasco
    (-23.5320, -46.7916),
]

# Nomes, espécies, raças e descrições realistas
animais_sp = [
    {"nome": "Mel", "especie": "cao", "raca": "Labrador", "porte": "grande", "cor": "Amarelo", "sexo": "femea", "descricao": "Muito dócil, adora brincar com crianças."},
    {"nome": "Thor", "especie": "cao", "raca": "Pastor Alemão", "porte": "grande", "cor": "Preto e marrom", "sexo": "macho", "descricao": "Protetor e inteligente, ótimo para companhia."},
    {"nome": "Nina", "especie": "gato", "raca": "Siamês", "porte": "pequeno", "cor": "Branco e cinza", "sexo": "femea", "descricao": "Gata carinhosa, gosta de colo."},
    {"nome": "Simba", "especie": "gato", "raca": "Persa", "porte": "pequeno", "cor": "Laranja", "sexo": "macho", "descricao": "Muito calmo, ideal para apartamento."},
    {"nome": "Bidu", "especie": "cao", "raca": "Vira-lata", "porte": "medio", "cor": "Cinza", "sexo": "macho", "descricao": "Brincalhão e companheiro."},
    {"nome": "Lola", "especie": "gato", "raca": "Maine Coon", "porte": "medio", "cor": "Preto e branco", "sexo": "femea", "descricao": "Gosta de explorar e caçar brinquedos."},
    {"nome": "Pipoca", "especie": "coelho", "raca": "Mini Lop", "porte": "pequeno", "cor": "Branco", "sexo": "femea", "descricao": "Coelhinha dócil, ótima para crianças."},
    {"nome": "Fred", "especie": "cao", "raca": "Poodle", "porte": "pequeno", "cor": "Branco", "sexo": "macho", "descricao": "Muito esperto e adora passear."},
    {"nome": "Mia", "especie": "gato", "raca": "SRD", "porte": "pequeno", "cor": "Rajado", "sexo": "femea", "descricao": "Gata independente, mas gosta de carinho."},
    {"nome": "Toby", "especie": "cao", "raca": "Beagle", "porte": "medio", "cor": "Marrom e branco", "sexo": "macho", "descricao": "Muito ativo, precisa de espaço para brincar."},
    {"nome": "Bela", "especie": "cao", "raca": "Golden Retriever", "porte": "grande", "cor": "Dourado", "sexo": "femea", "descricao": "Extremamente dócil e sociável."},
    {"nome": "Max", "especie": "cao", "raca": "Bulldog", "porte": "medio", "cor": "Branco e marrom", "sexo": "macho", "descricao": "Calmo e adora dormir."},
    {"nome": "Luna", "especie": "gato", "raca": "Angorá", "porte": "pequeno", "cor": "Branco", "sexo": "femea", "descricao": "Muito curiosa e brincalhona."},
    {"nome": "Bolinha", "especie": "hamster", "raca": "Sírio", "porte": "pequeno", "cor": "Dourado", "sexo": "macho", "descricao": "Adora correr na rodinha."},
    {"nome": "Cacau", "especie": "coelho", "raca": "Lionhead", "porte": "pequeno", "cor": "Marrom", "sexo": "femea", "descricao": "Muito dócil e gosta de cenoura."},
    {"nome": "Nico", "especie": "passaro", "raca": "Calopsita", "porte": "pequeno", "cor": "Cinza e amarelo", "sexo": "macho", "descricao": "Canta bastante e é manso."},
    {"nome": "Melancia", "especie": "hamster", "raca": "Anão Russo", "porte": "pequeno", "cor": "Cinza", "sexo": "femea", "descricao": "Pequena e muito ativa."},
    {"nome": "Dudu", "especie": "passaro", "raca": "Periquito", "porte": "pequeno", "cor": "Verde", "sexo": "macho", "descricao": "Gosta de companhia e de cantar."},
    {"nome": "Amora", "especie": "gato", "raca": "SRD", "porte": "pequeno", "cor": "Preto", "sexo": "femea", "descricao": "Muito carinhosa e tranquila."},
    {"nome": "Frajola", "especie": "gato", "raca": "SRD", "porte": "medio", "cor": "Preto e branco", "sexo": "macho", "descricao": "Esperto e adora brincar com bolinhas."},
]
pesos = {
    "cao": (5.0, 35.0),
    "gato": (2.0, 8.0),
    "coelho": (1.0, 3.0),
    "hamster": (0.05, 0.2),
    "passaro": (0.03, 0.1),
    "outro": (0.2, 10.0),
}
idades = {
    "cao": (4, 120),
    "gato": (4, 180),
    "coelho": (2, 60),
    "hamster": (1, 36),
    "passaro": (2, 120),
    "outro": (2, 120),
}
for i, animal in enumerate(animais_sp):
    lat, lng = random.choice(localizacoes_sp)
    especie = animal["especie"]
    idade = random.randint(*idades[especie])
    peso = round(random.uniform(*pesos[especie]), 2)
    castrado = random.choice([True, False])
    vacinado = random.choice([True, False])
    vermifugado = random.choice([True, False])
    docil = random.choice([True, False])
    brincalhao = random.choice([True, False])
    calmo = random.choice([True, False])
    especie_emoji = {
        "cao": "🐶",
        "gato": "🐱",
        "coelho": "🐰",
        "hamster": "🐹",
        "passaro": "🐦",
        "outro": "🐾",
    }
    emoji = especie_emoji.get(especie, "🐾")
    if not Pet.objects.filter(nome=animal["nome"]).exists():
        Pet.objects.create(
            nome=animal["nome"],
            especie=especie,
            raca=animal["raca"],
            idade=idade,
            sexo=animal["sexo"],
            porte=animal["porte"],
            cor=animal["cor"],
            peso=peso,
            castrado=castrado,
            vacinado=vacinado,
            vermifugado=vermifugado,
            docil=docil,
            brincalhao=brincalhao,
            calmo=calmo,
            descricao=animal["descricao"],
            latitude=lat,
            longitude=lng,
            status="disponivel",
            emoji=emoji,
            local_adocao=local_sp
        )
        print(f"Pet '{animal['nome']}' criado com localização individual em SP.")
