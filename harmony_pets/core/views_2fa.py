
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TwoFactorSetupForm, TwoFactorLoginForm, DisableTwoFactorForm
from .models import TwoFactorAuth

@login_required
def setup_2fa(request):
    user = request.user
    if request.method == 'POST':
        form = TwoFactorSetupForm(request.POST)
        if form.is_valid():
            # Salva/ativa 2FA para o usuário
            TwoFactorAuth.objects.update_or_create(user=user, defaults={
                'is_active': True,
                'secret': form.cleaned_data['secret'],
                'method': form.cleaned_data['method'],
            })
            messages.success(request, 'Autenticação em duas etapas ativada com sucesso!')
            return redirect('core:profile')
        else:
            messages.error(request, 'Erro ao ativar 2FA. Verifique os dados informados.')
    else:
        form = TwoFactorSetupForm()
    return render(request, 'core/setup_2fa.html', {'form': form})

@login_required
def verify_2fa(request):
    user = request.user
    if request.method == 'POST':
        form = TwoFactorLoginForm(request.POST)
        if form.is_valid():
            # Verifica o código 2FA
            code = form.cleaned_data['code']
            twofa = TwoFactorAuth.objects.filter(user=user, is_active=True).first()
            if twofa and twofa.verify_code(code):
                messages.success(request, 'Verificação 2FA realizada com sucesso!')
                return redirect('core:profile')
            else:
                messages.error(request, 'Código 2FA inválido.')
        else:
            messages.error(request, 'Preencha o código corretamente.')
    else:
        form = TwoFactorLoginForm()
    return render(request, 'core/verify_2fa.html', {'form': form})

@login_required
def set_2fa_preference(request):
    user = request.user
    if request.method == 'POST':
        preference = request.POST.get('preference')
        twofa = TwoFactorAuth.objects.filter(user=user).first()
        if twofa:
            twofa.preference = preference
            twofa.save()
            messages.success(request, 'Preferência de 2FA atualizada!')
        else:
            messages.error(request, 'Configuração de 2FA não encontrada.')
    return redirect('core:profile')

@login_required
def disable_2fa(request):
    user = request.user
    if request.method == 'POST':
        form = DisableTwoFactorForm(request.POST)
        if form.is_valid():
            twofa = TwoFactorAuth.objects.filter(user=user).first()
            if twofa:
                twofa.is_active = False
                twofa.save()
                messages.success(request, 'Autenticação em duas etapas desativada!')
                return redirect('core:profile')
            else:
                messages.error(request, 'Configuração de 2FA não encontrada.')
        else:
            messages.error(request, 'Preencha o formulário corretamente.')
    else:
        form = DisableTwoFactorForm()
    return render(request, 'core/disable_2fa.html', {'form': form})
