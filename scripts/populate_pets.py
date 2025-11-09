"""
Script legado de população.

Este script foi substituído pelo comando de management e pelo script de SP:

  - Recomendado: python manage.py populate_real_data --reset --pets 30
  - Alternativa: python manage.py shell < scripts/populate_pets_sp.py

Mantenha-o apenas por compatibilidade. Não realiza nenhuma operação.
"""

print(
    "[INFO] Script legado. Use 'python manage.py populate_real_data --reset --pets 30' "
    "ou 'python manage.py shell < scripts/populate_pets_sp.py'"
)
