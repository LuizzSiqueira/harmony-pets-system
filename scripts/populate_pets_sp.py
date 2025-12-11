#!/usr/bin/env python
"""
Script especializado para popular dados de São Paulo com coordenadas reais.

LOCALIZAÇÃO: harmony-pets-system/scripts/populate_pets_sp.py

COMO EXECUTAR:
    cd harmony-pets-system/harmony_pets
    python manage.py shell < ../scripts/populate_pets_sp.py

Este script é similar ao populate_pets.py mas com foco em:
- Coordenadas geográficas precisas de São Paulo
- Maior variedade de localizações (bairros diversos)
- Mais pets para testar funcionalidades de busca por proximidade

Para uso básico, prefira: scripts/populate_pets.py
Para comandos avançados: python manage.py populate_real_data --help
"""

import random
from django.db import transaction
from django.contrib.auth.models import User
from core.models import Pet, LocalAdocao

print("="*70)
print(" SCRIPT DE POPULAÇÃO - SÃO PAULO")
print("="*70)
print()
print("Este script cria dados específicos para São Paulo.")
print("Para população básica, use: scripts/populate_pets.py")
print()
print("Executando população de dados de São Paulo...")
print()

# Importar e executar o script principal
import sys
import os

# Adicionar o diretório scripts ao path para importar o módulo
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

# Importar configurações do script principal
from populate_pets import (
    locais_adocao, pets_catalogo, pesos, idades, emojis,
    criar_locais, criar_pets, limpar_banco, LIMPAR_BANCO
)

# Executar população
try:
    with transaction.atomic():
        if LIMPAR_BANCO:
            limpar_banco()
        
        locais = criar_locais()
        criar_pets(locais)
    
    print("="*70)
    print(" POPULAÇÃO DE SÃO PAULO CONCLUÍDA!")
    print("="*70)
    
except Exception as e:
    print(f"\nErro ao popular dados: {e}")
    print("\nVerifique se as migrações foram executadas:")
    print("  python manage.py migrate")
    raise
