from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import InteressadoAdocaoForm, LocalAdocaoForm


def register_view(request):
    termos_aceitos = request.session.get('termos_aceitos')
    if not termos_aceitos:
        messages.info(request, 'Primeiro você precisa aceitar nossos termos de uso.')
        return redirect('core:aceitar_termos')
    return render(request, 'core/register.html')


def register_interessado_view(request):
    termos_aceitos = request.session.get('termos_aceitos')
    if not termos_aceitos:
        messages.warning(request, 'Você precisa aceitar os termos de uso antes de se cadastrar.')
        return redirect('core:aceitar_termos')
    if request.method == 'POST':
        form = InteressadoAdocaoForm(request.POST)
        if form.is_valid():
            interessado = form.save(commit=False)
            interessado.usuario = request.user
            interessado.save()
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('core:profile')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = InteressadoAdocaoForm()
    return render(request, 'core/register_interessado.html', {'form': form})


def register_local_view(request):
    termos_aceitos = request.session.get('termos_aceitos')
    if not termos_aceitos:
        messages.warning(request, 'Você precisa aceitar os termos de uso antes de se cadastrar.')
        return redirect('core:aceitar_termos')
    if request.method == 'POST':
        form = LocalAdocaoForm(request.POST)
        if form.is_valid():
            local = form.save(commit=False)
            local.usuario = request.user
            local.save()
            messages.success(request, 'Cadastro do local realizado com sucesso!')
            return redirect('core:profile')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = LocalAdocaoForm()
    return render(request, 'core/register_local.html', {'form': form})
