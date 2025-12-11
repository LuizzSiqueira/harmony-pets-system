from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .utils import obter_emoji_animal, buscar_emoji_animais, EmojiAPIError

@require_GET
def sugerir_emoji(request):
    termo = (request.GET.get('termo') or '').strip()
    group = (request.GET.get('group') or '').strip() or None
    if not termo:
        return JsonResponse({'ok': False, 'emoji': '', 'error': 'Termo não informado'})
    # Se o termo for uma espécie, traduz para inglês para a API
    especie_map = {
        'cao': 'dog',
        'gato': 'cat',
        'coelho': 'rabbit',
        'hamster': 'hamster',
        'passaro': 'bird',
        'outro': 'paw prints',
    }
    termo_api = especie_map.get(termo.lower(), termo)
    try:
        emoji_char = obter_emoji_animal(termo_api)
    except EmojiAPIError as e:
        return JsonResponse({'ok': False, 'emoji': '', 'error': str(e)})
    return JsonResponse({'ok': bool(emoji_char), 'emoji': emoji_char})
