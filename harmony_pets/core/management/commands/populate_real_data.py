from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from django.conf import settings

from core.models import LocalAdocao, Pet

import os
import random
from django.core.files import File


class Command(BaseCommand):
    help = "Popula o sistema com dados reais (locais de adoção em SP e pets com coordenadas)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Remove dados existentes (pets/locais/usuários de locais) antes de popular",
        )
        parser.add_argument(
            "--pets",
            type=int,
            default=20,
            help="Quantidade aproximada de pets a criar (distribuídos entre os locais)",
        )

    def handle(self, *args, **options):
        reset = options.get("reset", False)
        total_pets = int(options.get("pets") or 20)

        # Helper para gerar nomes que sejam nomes próprios (sem adjetivos como "Amigo"/"Fofo"), sem dígitos
        def gerar_nome_unico(base_nome: str, sexo: str, local: LocalAdocao) -> str:
            sufixos_m = ["zinho", "inho"]
            sufixos_f = ["zinha", "inha"]
            nomes_proprios_extra = [
                "Luna", "Nina", "Mia", "Lola", "Bella", "Mel", "Kiara", "Maya", "Lia", "Clara", "Sofia",
                "Theo", "Leo", "Tito", "Nico", "Chico", "Fred", "Bento", "Dudu", "Paco", "Teca", "Tuca"
            ]

            candidatos = []
            # 1) Nome base
            candidatos.append(base_nome)
            # 2) Diminutivos conforme sexo
            sufixos = sufixos_f if (sexo or "").lower().startswith("f") else sufixos_m
            for sfx in sufixos:
                candidatos.append(f"{base_nome}{sfx}")
            # 3) Combinações com outro nome próprio (sem repetir o mesmo nome)
            for outro in nomes_proprios_extra:
                if outro.lower() != (base_nome or "").lower():
                    candidatos.append(f"{base_nome} {outro}")

            # Retorna o primeiro candidato que não exista ainda no banco
            for cand in candidatos:
                if not Pet.objects.filter(nome=cand).exists():
                    return cand

            # Fallback: combinações aleatórias de nomes próprios e diminutivos (sem números)
            tentativas = 0
            while tentativas < 30:
                outro = random.choice(nomes_proprios_extra)
                sfx = random.choice(sufixos)
                cand = random.choice([
                    f"{base_nome} {outro}",
                    f"{base_nome}{sfx}",
                    f"{outro} {base_nome}",
                ])
                if not Pet.objects.filter(nome=cand).exists():
                    return cand
                tentativas += 1
            # Último recurso: devolve o base_nome
            return base_nome

        if reset:
            self.stdout.write(self.style.WARNING("Limpando dados existentes..."))
            with transaction.atomic():
                Pet.objects.all().delete()
                for local in LocalAdocao.objects.all():
                    if hasattr(local, "usuario"):
                        local.usuario.delete()
                    local.delete()
            self.stdout.write(self.style.SUCCESS("Dados limpos."))

        # Locais reais (SP) com coordenadas aproximadas
        locais_sp = [
            {
                "username": "ong_pinheiros",
                "email": "contato@ongpinheiros.org",
                "nome_fantasia": "ONG Pinheiros Pets",
                "telefone": "(11) 98811-0001",
                "cnpj": "27849536000101",
                "endereco": "R. dos Pinheiros, 1300 - Pinheiros, São Paulo - SP",
                "lat": -23.5665,
                "lng": -46.6817,
            },
            {
                "username": "ong_moema",
                "email": "contato@ongmoema.org",
                "nome_fantasia": "ONG Moema Animal",
                "telefone": "(11) 97722-0002",
                "cnpj": "27849536000102",
                "endereco": "Al. dos Arapanés, 500 - Moema, São Paulo - SP",
                "lat": -23.6035,
                "lng": -46.6676,
            },
            {
                "username": "ong_tatuape",
                "email": "contato@ongtatuape.org",
                "nome_fantasia": "ONG Tatuapé Bicho",
                "telefone": "(11) 96633-0003",
                "cnpj": "27849536000103",
                "endereco": "R. Tijuco Preto, 300 - Tatuapé, São Paulo - SP",
                "lat": -23.5412,
                "lng": -46.5755,
            },
            {
                "username": "ong_santana",
                "email": "contato@ongsantana.org",
                "nome_fantasia": "ONG Santana Amigos dos Pets",
                "telefone": "(11) 95544-0004",
                "cnpj": "27849536000104",
                "endereco": "R. Dr. César, 1200 - Santana, São Paulo - SP",
                "lat": -23.4956,
                "lng": -46.6330,
            },
            {
                "username": "ong_lapa",
                "email": "contato@onglapa.org",
                "nome_fantasia": "ONG Lapa Vida Animal",
                "telefone": "(11) 94455-0005",
                "cnpj": "27849536000105",
                "endereco": "R. Doze de Outubro, 500 - Lapa, São Paulo - SP",
                "lat": -23.5270,
                "lng": -46.7033,
            },
            {
                "username": "ong_sto_amaro",
                "email": "contato@ongstoamaro.org",
                "nome_fantasia": "ONG Santo Amaro Pet",
                "telefone": "(11) 93366-0006",
                "cnpj": "27849536000106",
                "endereco": "Av. João Dias, 2000 - Santo Amaro, São Paulo - SP",
                "lat": -23.6457,
                "lng": -46.7067,
            },
        ]

        self.stdout.write("Criando locais de adoção em São Paulo...")
        locais_objs = []
        for idx, data in enumerate(locais_sp, start=1):
            user, _ = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "first_name": data["nome_fantasia"].split()[0],
                    "last_name": data["nome_fantasia"].split()[-1],
                },
            )
            local, created = LocalAdocao.objects.get_or_create(
                usuario=user,
                defaults={
                    "cnpj": data["cnpj"],
                    "nome_fantasia": data["nome_fantasia"],
                    "telefone": data["telefone"],
                    "endereco": data["endereco"],
                    "latitude": data["lat"],
                    "longitude": data["lng"],
                },
            )
            locais_objs.append(local)
            if created:
                self.stdout.write(self.style.SUCCESS(f" - {data['nome_fantasia']} criado"))
            else:
                self.stdout.write(f" - {data['nome_fantasia']} já existia")

        # Catálogo de pets realista
        animais_catalogo = [
            {"nome": "Mel", "especie": "cao", "raca": "Labrador", "porte": "grande", "cor": "Amarelo", "sexo": "femea", "descricao": "Muito dócil, adora brincar com crianças."},
            {"nome": "Thor", "especie": "cao", "raca": "SRD", "porte": "medio", "cor": "Caramelo", "sexo": "macho", "descricao": "Companheiro e brincalhão, adora passeios."},
            {"nome": "Nina", "especie": "gato", "raca": "Siamês", "porte": "pequeno", "cor": "Branco e cinza", "sexo": "femea", "descricao": "Gata carinhosa, gosta de colo."},
            {"nome": "Simba", "especie": "gato", "raca": "Persa", "porte": "pequeno", "cor": "Laranja", "sexo": "macho", "descricao": "Muito calmo, ideal para apartamento."},
            {"nome": "Bidu", "especie": "cao", "raca": "Vira-lata", "porte": "medio", "cor": "Cinza", "sexo": "macho", "descricao": "Brincalhão e companheiro."},
            {"nome": "Lola", "especie": "gato", "raca": "Maine Coon", "porte": "medio", "cor": "Preto e branco", "sexo": "femea", "descricao": "Curiosa e ativa, adora brinquedos."},
            {"nome": "Pipoca", "especie": "coelho", "raca": "Mini Lop", "porte": "pequeno", "cor": "Branco", "sexo": "femea", "descricao": "Coelhinha dócil, ótima para crianças."},
            {"nome": "Fred", "especie": "cao", "raca": "Poodle", "porte": "pequeno", "cor": "Branco", "sexo": "macho", "descricao": "Esperto e obediente, fácil de treinar."},
            {"nome": "Mia", "especie": "gato", "raca": "SRD", "porte": "pequeno", "cor": "Rajado", "sexo": "femea", "descricao": "Independente, mas carinhosa."},
            {"nome": "Toby", "especie": "cao", "raca": "Beagle", "porte": "medio", "cor": "Marrom e branco", "sexo": "macho", "descricao": "Ativo, precisa de passeios diários."},
        ]

        # Faixas de peso/idade por espécie
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
        especie_emoji = {
            "cao": "🐶",
            "gato": "🐱",
            "coelho": "🐰",
            "hamster": "🐹",
            "passaro": "🐦",
            "outro": "🐾",
        }

        # Pasta com imagens opcionais
        images_path = os.path.join(settings.BASE_DIR, "core", "static", "core", "images", "pets")
        image_files = [
            "dog1.jpg",
            "cat1.jpg",
            "dog2.jpg",
            "cat2.jpg",
            "hamster1.jpg",
            "rabbit1.jpg",
        ]

        self.stdout.write("Criando pets...")
        created = 0
        # Distribuir pets entre os locais
        for i in range(total_pets):
            base = random.choice(animais_catalogo)
            especie = base["especie"]
            idade = random.randint(*idades[especie])
            peso = round(random.uniform(*pesos[especie]), 2)
            local = random.choice(locais_objs)
            # Alguns pets com localização própria nas redondezas do local
            lat_jitter = (random.random() - 0.5) * 0.01
            lng_jitter = (random.random() - 0.5) * 0.01
            lat = (local.latitude or -23.5505) + lat_jitter
            lng = (local.longitude or -46.6333) + lng_jitter

            # Gerar nome realista e único, sem números
            nome_unico = gerar_nome_unico(base["nome"], base.get("sexo"), local)
            if Pet.objects.filter(nome=nome_unico).exists():
                # Se por acaso colidir, tenta uma segunda vez com um novo candidato
                nome_unico = gerar_nome_unico(base["nome"], base.get("sexo"), local)
                if Pet.objects.filter(nome=nome_unico).exists():
                    continue

            pet_kwargs = dict(
                nome=nome_unico,
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
                emoji=especie_emoji.get(especie, "🐾"),
                local_adocao=local,
            )

            # Imagem opcional
            if getattr(settings, "POPULATE_PETS_WITH_IMAGES", False) and os.path.isdir(images_path):
                file_name = image_files[i % len(image_files)]
                img_path = os.path.join(images_path, file_name)
                if os.path.exists(img_path):
                    with open(img_path, "rb") as f:
                        pet_kwargs["foto"] = File(f, name=file_name)

            Pet.objects.create(**pet_kwargs)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Concluído. {created} pets criados em {len(locais_objs)} locais."))
