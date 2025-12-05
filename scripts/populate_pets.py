#!/usr/bin/env python
"""
Script unificado para popular o banco de dados com pets de exemplo.

Execute: python manage.py shell < populate_pets.py

Este script cria:
- Locais de adoção em diferentes cidades (SP capital, Mogi, etc)
- Pets variados com coordenadas geográficas reais
- Dados realistas para teste do sistema
"""

import random
from django.db import transaction
from django.contrib.auth.models import User
from core.models import Pet, LocalAdocao

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

LIMPAR_BANCO = True  # Se True, remove todos os pets e locais antes de popular
QUANTIDADE_PETS_POR_LOCAL = 3  # Pets por local de adoção

# ============================================================================
# LOCAIS DE ADOÇÃO
# ============================================================================

locais_adocao = [
    {
        "username": "ong_pinheiros",
        "email": "contato@ongpinheiros.org",
        "nome": "ONG Pinheiros Pets",
        "tel": "(11) 98811-0001",
        "cnpj": "27849536000101",
        "endereco": "R. dos Pinheiros, 1300 - Pinheiros, São Paulo - SP",
        "lat": -23.5665,
        "lng": -46.6817,
    },
    {
        "username": "ong_moema",
        "email": "contato@ongmoema.org",
        "nome": "ONG Moema Animal",
        "tel": "(11) 97722-0002",
        "cnpj": "11222333000181",
        "endereco": "Al. dos Arapanés, 500 - Moema, São Paulo - SP",
        "lat": -23.6035,
        "lng": -46.6676,
    },
    {
        "username": "ong_tatuape",
        "email": "contato@ongtatuape.org",
        "nome": "ONG Tatuapé Bicho",
        "tel": "(11) 96633-0003",
        "cnpj": "22333444000162",
        "endereco": "R. Tijuco Preto, 300 - Tatuapé, São Paulo - SP",
        "lat": -23.5412,
        "lng": -46.5755,
    },
    {
        "username": "ong_mogi",
        "email": "contato@ongmogi.com",
        "nome": "ONG Mogi Pet",
        "tel": "(11) 99099-0000",
        "cnpj": "55666777000105",
        "endereco": "Av. Voluntário Fernando Pinheiro Franco, 350 - Centro, Mogi das Cruzes, SP",
        "lat": -23.5225,
        "lng": -46.1884,
    },
    {
        "username": "ong_sp_centro",
        "email": "contato@ongspcentro.com",
        "nome": "ONG SP Centro",
        "tel": "(11) 98000-0000",
        "cnpj": "00360305000104",
        "endereco": "Praça da Sé - Centro, São Paulo - SP",
        "lat": -23.5505,
        "lng": -46.6333,
    },
]

# ============================================================================
# CATÁLOGO DE PETS
# ============================================================================

pets_catalogo = [
    {"nome": "Luna", "especie": "cao", "raca": "Vira-lata", "porte": "medio", "cor": "Marrom e branco", "sexo": "femea", "descricao": "Cadela super carinhosa e brincalhona. Adora passear e brincar com bolinhas."},
    {"nome": "Mel", "especie": "cao", "raca": "Labrador", "porte": "grande", "cor": "Amarelo", "sexo": "femea", "descricao": "Muito dócil e companheira, ótima com crianças."},
    {"nome": "Thor", "especie": "cao", "raca": "Pastor Alemão", "porte": "grande", "cor": "Preto e marrom", "sexo": "macho", "descricao": "Cão leal e protetor, muito inteligente."},
    {"nome": "Rex", "especie": "cao", "raca": "SRD", "porte": "medio", "cor": "Caramelo", "sexo": "macho", "descricao": "Brincalhão e ativo, precisa de espaço."},
    {"nome": "Bidu", "especie": "cao", "raca": "Vira-lata", "porte": "medio", "cor": "Cinza", "sexo": "macho", "descricao": "Brincalhão e companheiro."},
    {"nome": "Fred", "especie": "cao", "raca": "Poodle", "porte": "pequeno", "cor": "Branco", "sexo": "macho", "descricao": "Muito esperto e adora passear."},
    {"nome": "Toby", "especie": "cao", "raca": "Beagle", "porte": "medio", "cor": "Marrom e branco", "sexo": "macho", "descricao": "Muito ativo, precisa de espaço para brincar."},
    {"nome": "Bela", "especie": "cao", "raca": "Golden Retriever", "porte": "grande", "cor": "Dourado", "sexo": "femea", "descricao": "Extremamente dócil e sociável."},
    {"nome": "Max", "especie": "cao", "raca": "Bulldog", "porte": "medio", "cor": "Branco e marrom", "sexo": "macho", "descricao": "Calmo e adora dormir."},
    {"nome": "Miau", "especie": "gato", "raca": "Siamês", "porte": "pequeno", "cor": "Creme e marrom", "sexo": "macho", "descricao": "Gato muito tranquilo e carinhoso. Perfeito para apartamentos."},
    {"nome": "Nina", "especie": "gato", "raca": "Siamês", "porte": "pequeno", "cor": "Branco e cinza", "sexo": "femea", "descricao": "Gosta de colo e carinho."},
    {"nome": "Nila", "especie": "gato", "raca": "Persa", "porte": "pequeno", "cor": "Cinza", "sexo": "femea", "descricao": "Gatinha muito dócil e carinhosa."},
    {"nome": "Simba", "especie": "gato", "raca": "Persa", "porte": "pequeno", "cor": "Laranja", "sexo": "macho", "descricao": "Calmo e carinhoso, ideal para apartamento."},
    {"nome": "Mia", "especie": "gato", "raca": "SRD", "porte": "pequeno", "cor": "Rajado", "sexo": "femea", "descricao": "Gata independente, mas gosta de carinho."},
    {"nome": "Luna Gata", "especie": "gato", "raca": "Angorá", "porte": "pequeno", "cor": "Branco", "sexo": "femea", "descricao": "Muito curiosa e brincalhona."},
    {"nome": "Amora", "especie": "gato", "raca": "SRD", "porte": "pequeno", "cor": "Preto", "sexo": "femea", "descricao": "Muito carinhosa e tranquila."},
    {"nome": "Frajola", "especie": "gato", "raca": "SRD", "porte": "medio", "cor": "Preto e branco", "sexo": "macho", "descricao": "Esperto e adora brincar com bolinhas."},
    {"nome": "Bolinha", "especie": "hamster", "raca": "Sírio", "porte": "pequeno", "cor": "Dourado", "sexo": "macho", "descricao": "Hamster super ativo e divertido."},
    {"nome": "Mel Coelha", "especie": "coelho", "raca": "Mini Lop", "porte": "pequeno", "cor": "Branco e marrom", "sexo": "femea", "descricao": "Coelhinha muito meiga e carinhosa."},
    {"nome": "Pipoca", "especie": "coelho", "raca": "Mini Lop", "porte": "pequeno", "cor": "Branco", "sexo": "femea", "descricao": "Coelhinha dócil, ótima para crianças."},
]

# Configurações de peso e idade por espécie
pesos = {
    "cao": (5.0, 35.0),
    "gato": (2.0, 8.0),
    "coelho": (1.0, 3.0),
    "hamster": (0.05, 0.2),
    "passaro": (0.03, 0.1),
}

idades = {
    "cao": (4, 120),
    "gato": (4, 180),
    "coelho": (2, 60),
    "hamster": (1, 36),
    "passaro": (2, 120),
}

emojis = {
    "cao": "🐶",
    "gato": "🐱",
    "coelho": "🐰",
    "hamster": "🐹",
    "passaro": "🐦",
}

# ============================================================================
# FUNÇÕES
# ============================================================================

def limpar_banco():
    """Remove todos os pets e locais de adoção."""
    print('Removendo todos os pets, locais de adoção e usuários relacionados...')
    Pet.objects.all().delete()
    for local in LocalAdocao.objects.all():
        if hasattr(local, 'usuario'):
            local.usuario.delete()
        local.delete()
    print('Remoção concluída.\n')


def criar_locais():
    """Cria os locais de adoção."""
    print('Criando locais de adoção...')
    locais = []
    for d in locais_adocao:
        user, created = User.objects.get_or_create(
            username=d["username"],
            defaults={
                "email": d["email"],
                "first_name": d["nome"].split()[0],
                "last_name": d["nome"].split()[-1]
            },
        )
        # Define senha padrão
        try:
            user.set_password('123')
            user.save()
        except Exception:
            pass
        
        local, created = LocalAdocao.objects.get_or_create(
            usuario=user,
            defaults={
                "cnpj": d["cnpj"],
                "nome_fantasia": d["nome"],
                "telefone": d["tel"],
                "endereco": d["endereco"],
                "latitude": d["lat"],
                "longitude": d["lng"],
            },
        )
        locais.append(local)
        status = "✓ Criado" if created else "  Já existe"
        print(f"  {status}: {d['nome']}")
    
    print(f"\n{len(locais)} locais de adoção prontos.\n")
    return locais


def criar_pets(locais):
    """Cria pets para cada local."""
    print('Criando pets...')
    created_count = 0
    pets_usados = set()
    
    for local in locais:
        for i in range(QUANTIDADE_PETS_POR_LOCAL):
            # Seleciona um pet que ainda não foi usado
            pets_disponiveis = [p for p in pets_catalogo if p["nome"] not in pets_usados]
            if not pets_disponiveis:
                break
            
            base = random.choice(pets_disponiveis)
            pets_usados.add(base["nome"])
            
            especie = base["especie"]
            idade = random.randint(*idades.get(especie, (4, 120)))
            peso = round(random.uniform(*pesos.get(especie, (2.0, 15.0))), 2)
            
            # Leve variação ao redor do local
            lat = (local.latitude or -23.5505) + (random.random() - 0.5) * 0.01
            lng = (local.longitude or -46.6333) + (random.random() - 0.5) * 0.01
            
            if not Pet.objects.filter(nome=base["nome"]).exists():
                Pet.objects.create(
                    nome=base["nome"],
                    especie=especie,
                    raca=base["raca"],
                    idade=idade,
                    sexo=base["sexo"],
                    porte=base["porte"],
                    cor=base["cor"],
                    peso=peso,
                    castrado=random.choice([True, False]),
                    vacinado=random.choice([True, False]),
                    vermifugado=random.choice([True, False]),
                    docil=random.choice([True, False]),
                    brincalhao=random.choice([True, False]),
                    calmo=random.choice([True, False]),
                    descricao=base["descricao"],
                    latitude=lat,
                    longitude=lng,
                    status="disponivel",
                    emoji=emojis.get(especie, "🐾"),
                    local_adocao=local,
                )
                created_count += 1
                print(f"  ✓ {base['nome']} ({especie}) - {local.nome_fantasia}")
    
    print(f"\n✅ {created_count} pets criados com sucesso!")
    print(f"Total de pets no sistema: {Pet.objects.count()}\n")

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

print("="*70)
print(" SCRIPT DE POPULAÇÃO DO BANCO DE DADOS - HARMONY PETS")
print("="*70)
print()

with transaction.atomic():
    if LIMPAR_BANCO:
        limpar_banco()
    
    locais = criar_locais()
    criar_pets(locais)

print("="*70)
print(" POPULAÇÃO CONCLUÍDA COM SUCESSO!")
print("="*70)
