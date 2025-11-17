"""
Script rápido para popular dados reais de SP.

Execute dentro do shell do Django:
  python manage.py shell < scripts/populate_pets_sp.py

Para uso mais completo e parametrizável, prefira o comando:
  python manage.py populate_real_data --reset --pets 30
"""

from core.models import Pet, LocalAdocao
from django.contrib.auth.models import User
import random

# Locais de adoção reais (aproximados) em São Paulo
locais_sp = [
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
        "cnpj": "27849536000102",
        "endereco": "Al. dos Arapanés, 500 - Moema, São Paulo - SP",
        "lat": -23.6035,
        "lng": -46.6676,
    },
    {
        "username": "ong_tatuape",
        "email": "contato@ongtatuape.org",
        "nome": "ONG Tatuapé Bicho",
        "tel": "(11) 96633-0003",
        "cnpj": "27849536000103",
        "endereco": "R. Tijuco Preto, 300 - Tatuapé, São Paulo - SP",
        "lat": -23.5412,
        "lng": -46.5755,
    },
]

# Catálogo simples de pets
animais_catalogo = [
    {"nome": "Mel", "especie": "cao", "raca": "Labrador", "porte": "grande", "cor": "Amarelo", "sexo": "femea", "descricao": "Muito dócil e companheira."},
    {"nome": "Thor", "especie": "cao", "raca": "SRD", "porte": "medio", "cor": "Caramelo", "sexo": "macho", "descricao": "Brincalhão e ativo."},
    {"nome": "Nina", "especie": "gato", "raca": "Siamês", "porte": "pequeno", "cor": "Branco e cinza", "sexo": "femea", "descricao": "Gosta de colo."},
    {"nome": "Simba", "especie": "gato", "raca": "Persa", "porte": "pequeno", "cor": "Laranja", "sexo": "macho", "descricao": "Calmo e carinhoso."},
]

pesos = {"cao": (5.0, 35.0), "gato": (2.0, 8.0)}
idades = {"cao": (4, 120), "gato": (4, 180)}
emoji = {"cao": "🐶", "gato": "🐱"}


def criar_locais():
    locais = []
    for d in locais_sp:
        user, _ = User.objects.get_or_create(
            username=d["username"],
            defaults={"email": d["email"], "first_name": d["nome"].split()[0], "last_name": d["nome"].split()[-1]},
        )
        # Define senha padrão para ambientes de desenvolvimento
        try:
            user.set_password('123')
            user.save()
        except Exception:
            pass
        local, _ = LocalAdocao.objects.get_or_create(
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
    return locais


def criar_pets(locais, quantidade=12):
    created = 0
    for i in range(quantidade):
        base = random.choice(animais_catalogo)
        especie = base["especie"]
        idade = random.randint(*idades[especie])
        peso = round(random.uniform(*pesos[especie]), 2)
        local = random.choice(locais)
        # Leve variação ao redor do local
        lat = (local.latitude or -23.5505) + (random.random() - 0.5) * 0.01
        lng = (local.longitude or -46.6333) + (random.random() - 0.5) * 0.01
        nome = f"{base['nome']}-{i+1}"
        if Pet.objects.filter(nome=nome).exists():
            continue
        Pet.objects.create(
            nome=nome,
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
            emoji=emoji[especie],
            local_adocao=local,
        )
        created += 1
    print(f"{created} pets criados/atualizados.")


locais = criar_locais()
criar_pets(locais, quantidade=18)
print("Concluído: locais e pets de SP criados com lat/lng reais.")