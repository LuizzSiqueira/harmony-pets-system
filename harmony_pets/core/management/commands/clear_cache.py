from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.template import engines
from django.urls import clear_url_caches


class Command(BaseCommand):
    help = "Limpa o cache da aplicação (cache.default), reseta caches de loaders de templates e limpa caches de URL resolvers."

    def handle(self, *args, **options):
        # Limpa cache padrão
        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS("Cache padrão limpo."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Falha ao limpar cache padrão: {e}"))

        # Reseta caches de loaders de template (se estiver usando cached loader)
        try:
            for eng in engines.all():
                engine = getattr(eng, "engine", eng)
                loaders = getattr(engine, "template_loaders", [])
                for loader in loaders:
                    reset = getattr(loader, "reset", None)
                    if callable(reset):
                        reset()
            self.stdout.write(self.style.SUCCESS("Caches dos loaders de templates resetados."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Falha ao resetar caches de templates: {e}"))

        # Limpa caches do resolver de URLs
        try:
            clear_url_caches()
            self.stdout.write(self.style.SUCCESS("Caches de URLs limpos."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Falha ao limpar caches de URLs: {e}"))

        self.stdout.write(self.style.SUCCESS("Concluído."))
