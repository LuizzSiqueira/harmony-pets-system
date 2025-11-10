from django.core.management.base import BaseCommand
from core.utils import buscar_emoji_animais, obter_emoji_animal, EmojiAPIError


class Command(BaseCommand):
    help = "Testa a integração com a Emoji API (API Ninjas) buscando emojis de animais."

    def add_arguments(self, parser):
        parser.add_argument('--termo', type=str, default='dog', help='Termo de busca (ex: dog, cat, panda)')
        parser.add_argument('--limit', type=int, default=3, help='Quantidade de resultados detalhados')

    def handle(self, *args, **options):
        termo = options['termo']
        limit = options['limit']
        self.stdout.write(self.style.NOTICE(f"Buscando emojis para termo='{termo}' (limit={limit})..."))
        try:
            lista = buscar_emoji_animais(termo, limit=limit)
            unico = obter_emoji_animal(termo)
        except EmojiAPIError as e:
            self.stderr.write(self.style.ERROR(f"Erro: {e}"))
            return

        if not lista:
            self.stdout.write(self.style.WARNING("Nenhum resultado encontrado."))
            return

        self.stdout.write(self.style.SUCCESS(f"Primeiro emoji encontrado: {unico or '[vazio]'}"))
        self.stdout.write("Resultados detalhados:")
        for item in lista:
            self.stdout.write(
                f" - {item.get('character','?')} | name={item.get('name')} | "
                f"group={item.get('group')} | subgroup={item.get('subgroup')} | code={item.get('code')} | image={item.get('image')}"
            )

        self.stdout.write(self.style.SUCCESS("Teste concluído."))