from harmony_pets.core.models import Pet, LocalAdocao
from django.contrib.auth.models import User
import random

# Lista de coordenadas próximas a Mogi das Cruzes e outras cidades de SP
localizacoes = [
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

nomes_pets = ["Rex", "Luna", "Mia", "Thor", "Mel", "Bob", "Nina", "Max", "Bidu", "Toby", "Simba", "Bela", "Pipoca", "Lola", "Fred"]
especies = ["cao", "gato", "coelho", "passaro", "hamster", "outro"]

# Cria pets com localizações variadas
for i in range(20):
    nome = random.choice(nomes_pets) + f"_{i}"
    especie = random.choice(especies)
    lat, lng = random.choice(localizacoes)
    pet = Pet(
        nome=nome,
        especie=especie,
        latitude=lat,
        longitude=lng,
        status="disponivel",
        emoji="🐾"
    )
    pet.save()
print("Pets criados com sucesso!")
