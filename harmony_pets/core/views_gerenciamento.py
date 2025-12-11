from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Pet, LocalAdocao
from .forms import PetForm

@login_required
def gerenciar_pets(request):
    try:
        local = request.user.localadocao
    except LocalAdocao.DoesNotExist:
        local = None
    pets = Pet.objects.filter(local_adocao=local, ativo=True).order_by('-data_cadastro')
    total_pets = pets.count()
    pets_disponiveis = pets.filter(status='disponivel').count()
    pets_adotados = pets.filter(status='adotado').count()
    pets_reservados = pets.filter(status='reservado').count()
    paginator = Paginator(pets, 12)
    page_number = request.GET.get('page')
    pets_page = paginator.get_page(page_number)
    context = {
        'pets': pets_page,
        'local': local,
        'stats': {
            'total': total_pets,
            'disponiveis': pets_disponiveis,
            'adotados': pets_adotados,
            'reservados': pets_reservados,
        }
    }
    return render(request, 'core/gerenciar_pets.html', context)

@login_required
def adicionar_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.local_adocao = request.user.localadocao
            pet.save()
            messages.success(request, 'Pet adicionado com sucesso!')
            return redirect('core:gerenciar_pets')
    else:
        form = PetForm()
    return render(request, 'core/adicionar_pet.html', {'form': form})

@login_required
def editar_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, local_adocao=request.user.localadocao)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pet atualizado com sucesso!')
            return redirect('core:gerenciar_pets')
    else:
        form = PetForm(instance=pet)
    return render(request, 'core/editar_pet.html', {'form': form, 'pet': pet})

@login_required
def excluir_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, local_adocao=request.user.localadocao)
    if request.method == 'POST':
        pet.ativo = False
        pet.save()
        messages.success(request, 'Pet excluído com sucesso!')
        return redirect('core:gerenciar_pets')
    return render(request, 'core/excluir_pet.html', {'pet': pet})

@login_required
def alterar_status_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, local_adocao=request.user.localadocao)
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status in dict(Pet.STATUS_CHOICES).keys():
            pet.status = novo_status
            pet.save()
            messages.success(request, 'Status do pet alterado com sucesso!')
        else:
            messages.error(request, 'Status inválido!')
        return redirect('core:gerenciar_pets')
    return render(request, 'core/alterar_status_pet.html', {'pet': pet})
