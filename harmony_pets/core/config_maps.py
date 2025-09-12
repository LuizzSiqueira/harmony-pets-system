# *** RASCUNHO - Configurações para Google Maps ***
# 
# INSTRUÇÕES PARA CONFIGURAR A API DO GOOGLE MAPS:
# 
# 1. Acesse: https://console.cloud.google.com/
# 2. Crie um novo projeto ou selecione um existente
# 3. Ative as seguintes APIs:
#    - Maps JavaScript API
#    - Geocoding API
# 4. Crie uma chave de API
# 5. Substitua "SUA_CHAVE_API_AQUI" pela sua chave real
# 6. Configure restrições de segurança (domínios permitidos)

# *** SUBSTITUA ESTA CHAVE PELA SUA CHAVE REAL ***
import os
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

# Configurações do mapa
GOOGLE_MAPS_CONFIG = {
    'default_zoom': 12,
    'default_location': {
        'lat': -23.55052,  # São Paulo - coordenadas padrão
        'lng': -46.633308
    },
    'max_pets_display': 20,  # Máximo de pets a exibir no mapa
    'max_distance_km': 50    # Distância máxima para buscar pets (em km)
}
