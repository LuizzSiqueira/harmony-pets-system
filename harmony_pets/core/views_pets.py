from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Pet, InteressadoAdocao, SolicitacaoAdocao
from .utils import calcular_distancia
from django.http import JsonResponse

def pets_list_view(request):
    mostrar_adotados = request.GET.get('adotados') == 'true'
    if mostrar_adotados and request.user.is_authenticated:
        try:
            interessado = InteressadoAdocao.objects.get(usuario=request.user)
            solicitacoes_concluidas = SolicitacaoAdocao.objects.filter(
                interessado=interessado,
                status='concluida'
            ).select_related('pet', 'pet__local_adocao')
            pets = [solicitacao.pet for solicitacao in solicitacoes_concluidas if solicitacao.pet]
            paginator = Paginator(pets, 12)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'page_obj': page_obj,
                'mostrar_adotados': True,
                'especies_choices': Pet.ESPECIES_CHOICES,
                'portes_choices': Pet.PORTES_CHOICES,
                'sexos_choices': Pet.SEXOS_CHOICES,
            }
            return render(request, 'core/pets_list.html', context)
        except InteressadoAdocao.DoesNotExist:
            pass
    pets = Pet.objects.filter(status='disponivel', ativo=True).select_related('local_adocao')
    mostrar_proximos = request.GET.get('proximos') == 'true'
    user_lat = None
    user_lon = None
    pets_com_distancia = {}
    especie = request.GET.get('especie')
    porte = request.GET.get('porte')
    sexo = request.GET.get('sexo')
    search = request.GET.get('search')
    if especie:
        pets = [pet for pet in pets if pet.especie == especie] if mostrar_proximos else pets.filter(especie=especie)
    if porte:
        pets = [pet for pet in pets if pet.porte == porte] if mostrar_proximos else pets.filter(porte=porte)
    if sexo:
        pets = [pet for pet in pets if pet.sexo == sexo] if mostrar_proximos else pets.filter(sexo=sexo)
    paginator = Paginator(pets, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'especie_atual': especie,
        'porte_atual': porte,
        'sexo_atual': sexo,
        'search_atual': search,
        'mostrar_proximos': mostrar_proximos,
        'tem_localizacao': user_lat is not None,
        'pets_com_distancia': pets_com_distancia,
        'especies_choices': Pet.ESPECIES_CHOICES,
        'portes_choices': Pet.PORTES_CHOICES,
        'sexos_choices': Pet.SEXOS_CHOICES,
    }
    return render(request, 'core/pets_list.html', context)


def pet_detail_view(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    interessado = None
    ja_solicitou = False
    if request.user.is_authenticated:
        try:
            interessado = InteressadoAdocao.objects.get(usuario=request.user)
            ja_solicitou = SolicitacaoAdocao.objects.filter(pet=pet, interessado=interessado).exists()
        except InteressadoAdocao.DoesNotExist:
            pass
    context = {
        'pet': pet,
        'interessado': interessado,
        'ja_solicitou': ja_solicitou,
    }
    return render(request, 'core/pet_detail.html', context)


@login_required
def pets_proximos(request):
    pets = Pet.objects.filter(status='disponivel', ativo=True).select_related('local_adocao')
    user_lat = request.user.profile.latitude
    user_lon = request.user.profile.longitude
    distancia_maxima = 5  # em quilômetros

    # Filtrar pets por proximidade
    pets_proximos = []
    for pet in pets:
        distancia = calcular_distancia(user_lat, user_lon, pet.local_adocao.latitude, pet.local_adocao.longitude)
        if distancia <= distancia_maxima:
            pets_proximos.append(pet)

    paginator = Paginator(pets_proximos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'tem_localizacao': True,
    }
    return render(request, 'core/pets_proximos.html', context)


def pets_mapa_api(request):
    pets = Pet.objects.filter(status='disponivel', ativo=True).select_related('local_adocao')
    pets_data = []
    for pet in pets:
        pets_data.append({
            'id': pet.id,
            'nome': pet.nome,
            'latitude': pet.local_adocao.latitude,
            'longitude': pet.local_adocao.longitude,
        })
    return JsonResponse(pets_data, safe=False)
