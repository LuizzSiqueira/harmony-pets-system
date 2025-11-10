#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'harmony_pets.settings')
    # Interativo: ao usar `runserver`, permitir escolher banco local (SQLite) ou web (Postgres/Supabase)
    try:
        if len(sys.argv) >= 2 and sys.argv[1] == 'runserver' and not os.environ.get('USE_DB'):
            # Apenas se for um terminal interativo
            is_tty = hasattr(sys.stdin, 'isatty') and sys.stdin.isatty()
            if is_tty:
                print("\n=== Seleção de Banco de Dados ===")
                print("[1] Local (SQLite) — recomendado para apresentação/offline")
                print("[2] Web (Postgres/Supabase)")
                choice = input("Opção [1/2] (padrão 1): ").strip()
            else:
                choice = ''
            os.environ['USE_DB'] = 'web' if choice == '2' else 'local'
    except Exception:
        # Em caso de qualquer problema no prompt, segue com padrão local
        os.environ.setdefault('USE_DB', 'local')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
