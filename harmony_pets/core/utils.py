import math
from typing import Tuple, Optional

def calcular_distancia(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula a distância entre duas coordenadas usando a fórmula de Haversine.
    
    Args:
        lat1, lon1: Latitude e longitude do primeiro ponto
        lat2, lon2: Latitude e longitude do segundo ponto
    
    Returns:
        Distância em quilômetros
    """
    # Converte graus para radianos
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Fórmula de Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Raio da Terra em quilômetros
    r = 6371
    
    return c * r

def geocodificar_endereco(endereco: str) -> Optional[Tuple[float, float]]:
    """
    *** RASCUNHO ***
    Função para geocodificar um endereço usando a API do Google Maps.
    
    Args:
        endereco: Endereço em formato string
    
    Returns:
        Tupla (latitude, longitude) ou None se não encontrar
    """
    import requests
    
    # SUBSTITUA SUA_CHAVE_API pela sua chave real do Google Maps
    API_KEY = "SUA_CHAVE_API_GOOGLE_MAPS"  # *** RASCUNHO - INSIRA SUA CHAVE ***
    
    url = f"https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': endereco,
        'key': API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['status'] == 'OK' and data['results']:
            location = data['results'][0]['geometry']['location']
            return (location['lat'], location['lng'])
    except Exception as e:
        print(f"Erro ao geocodificar endereço: {e}")
    
    return None
