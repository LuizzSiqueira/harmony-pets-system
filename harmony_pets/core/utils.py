# Utilitário para calcular distância entre dois pontos (Haversine)
from math import radians, sin, cos, sqrt, atan2

def calcular_distancia_km(lat1, lon1, lat2, lon2):
    """
    Calcula a distância em km entre dois pontos geográficos usando a fórmula de Haversine.
    """
    R = 6371.0  # Raio da Terra em km
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distancia = R * c
    return round(distancia, 2)
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

import os
import requests

def geocodificar_endereco(endereco: str) -> Optional[Tuple[float, float]]:
    """
    Função para geocodificar um endereço usando a API do Google Maps.
    Retorna uma tupla (lat, lng) ou None se não encontrar.
    """
    API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': endereco,
        'key': API_KEY
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data['status'] == 'OK' and data['results']:
            lat = data['results'][0]['geometry']['location']['lat']
            lng = data['results'][0]['geometry']['location']['lng']
            return (lat, lng)
        else:
            return None
    except Exception as e:
        print(f"Erro ao geocodificar endereço: {e}")
        return None

# Função para anonimizar dados sensíveis de InteressadoAdocao e User
def anonimizar_dados_interessado(interessado):
    """
    Anonimiza os dados sensíveis de uma instância de InteressadoAdocao e do usuário relacionado.
    """
    # Anonimizar dados do usuário
    user = interessado.usuario
    user.first_name = "Anonimo"
    user.last_name = "Anonimo"
    user.email = f"anonimo_{user.id}@exemplo.com"
    user.username = f"anonimo_{user.id}"
    user.save()

    # Anonimizar dados do interessado
    interessado.cpf = "***"
    interessado.telefone = "***"
    interessado.endereco = "***"
    interessado.save()


def mask_sensitive(value, preserve_chars='@.-_ '):
    """Retorna uma versão mascarada de `value` substituindo caracteres por '*' preservando alguns separadores.

    Exemplos:
        'joao.silva@example.com' -> '****.*****@*******.***'
        '123.456.789-00' -> '***.***.***-**'
    """
    if value is None:
        return value
    s = str(value)
    masked = []
    for ch in s:
        if ch in preserve_chars:
            masked.append(ch)
        elif ch.isspace():
            masked.append(ch)
        else:
            masked.append('*')
    return ''.join(masked)


def sanitize_payload(data: dict) -> dict:
    """Masca campos sensíveis em dicionários de payload (POST/PUT/PATCH).

    - Remove chaves notoriamente inúteis como csrfmiddlewaretoken
    - Mascara valores de chaves com nomes sensíveis (password, senha, token, secret, key, code)
    """
    if not isinstance(data, dict):
        return {}

    SENSITIVE_KEYS = {'password', 'senha', 'token', 'secret', 'key', 'api_key', 'access_token', 'refresh_token', 'code'}
    cleaned = {}
    for k, v in data.items():
        k_lower = str(k).lower()
        if k_lower in {'csrfmiddlewaretoken'}:
            continue
        if any(s in k_lower for s in SENSITIVE_KEYS):
            cleaned[k] = mask_sensitive(v)
        else:
            # Converte objetos não-serializáveis em string de forma segura
            try:
                cleaned[k] = v if isinstance(v, (int, float, bool)) else str(v)[:2000]
            except Exception:
                cleaned[k] = '<unserializable>'
    return cleaned

# ------------------ Emoji API (API Ninjas) ------------------
from typing import List, Dict

class EmojiAPIError(Exception):
    """Erro genérico ao consultar a Emoji API (API Ninjas)."""
    pass

def buscar_emoji_animais(termo: str, group: str | None = None, limit: int = 1) -> List[Dict]:
    """Consulta a Emoji API (API Ninjas) para buscar emojis (ex.: animais).

    Args:
        termo: termo de busca (ex: 'dog', 'cat', 'panda', 'slightly smiling face').
        group: grupo/categoria principal (ex.: 'animals_nature', 'smileys_emotion').
        limit: máximo de resultados a retornar.

    Returns:
        Lista de dicionários com campos da API (ex.: character, name, code, image, group, subgroup)

    Necessário definir variável de ambiente API_NINJAS_KEY com a chave.
    Documentação: https://api.api-ninjas.com/v1/emoji
    """
    api_key = os.environ.get('API_NINJAS_KEY')
    if not api_key:
        raise EmojiAPIError('Defina a variável de ambiente API_NINJAS_KEY com a chave da API.')

    base_url = 'https://api.api-ninjas.com/v1/emoji'
    params = {}
    if termo:
        params['name'] = termo
    if group:
        params['group'] = group
    if limit:
        params['limit'] = str(limit)

    try:
        resp = requests.get(base_url, headers={'X-Api-Key': api_key}, params=params, timeout=5)
    except requests.RequestException as e:
        raise EmojiAPIError(f'Erro de conexão com a API: {e}') from e

    if resp.status_code != 200:
        raise EmojiAPIError(f'Falha na API (status {resp.status_code}): {resp.text[:200]}')

    try:
        data = resp.json()
    except ValueError as e:
        raise EmojiAPIError('Resposta inválida (JSON).') from e

    if not isinstance(data, list):
        raise EmojiAPIError('Formato inesperado de resposta.')

    return data[:limit]

def obter_emoji_animal(termo: str) -> str:
    """Retorna apenas o caractere Unicode do primeiro emoji encontrado para o termo.

    Fallback: retorna string vazia se nada encontrado ou em erro (não dispara exceção
    para uso em fluxos não-críticos do sistema).
    """
    try:
        resultados = buscar_emoji_animais(termo, limit=1)
        if resultados:
            # API retorna campo 'character'
            return resultados[0].get('character') or ''
        return ''
    except EmojiAPIError as e:
        print(f"[WARN] Falha ao buscar emoji para '{termo}': {e}")
        return ''
