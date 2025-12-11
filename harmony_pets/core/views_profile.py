from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EditUserForm, EditInteressadoForm, EditLocalForm, ChangePasswordForm
from .models import InteressadoAdocao, LocalAdocao
from django.conf import settings
import copy

@login_required
def profile_view(request):
    user = request.user
    interessado = None
    local = None
    try:
        interessado = InteressadoAdocao.objects.get(usuario=user)
    except InteressadoAdocao.DoesNotExist:
        try:
            local = LocalAdocao.objects.get(usuario=user)
        except LocalAdocao.DoesNotExist:
            pass
    context = {
        'user': user,
        'interessado': interessado,
        'local': local,
    }
    return render(request, 'core/profile.html', context)

@login_required
def edit_profile_view(request):
    user = request.user
    interessado = None
    local = None
    criar_perfil = request.GET.get('criar_perfil')
    try:
        interessado = InteressadoAdocao.objects.get(usuario=user)
    except InteressadoAdocao.DoesNotExist:
        try:
            local = LocalAdocao.objects.get(usuario=user)
        except LocalAdocao.DoesNotExist:
            pass
    user_form = EditUserForm(instance=user)
    interessado_form = EditInteressadoForm(instance=interessado) if interessado else None
    local_form = EditLocalForm(instance=local) if local else None
    context = {
        'user_form': user_form,
        'interessado_form': interessado_form,
        'local_form': local_form,
        'interessado': interessado,
        'local': local,
        'criar_perfil': criar_perfil,
        'pode_criar_perfil': not interessado and not local,
    }
    return render(request, 'core/edit_profile.html', context)

@login_required
def change_password_view(request):
    form = ChangePasswordForm(user=request.user)
    return render(request, 'core/change_password.html', {'form': form})
