from django.shortcuts import render, redirect
from django.contrib import messages


def aceitar_termos(request):
    if request.method == 'POST':
        termos_uso_aceito = request.POST.get('termos_uso') == 'on'
        lgpd_aceito = request.POST.get('lgpd') == 'on'
        if not termos_uso_aceito or not lgpd_aceito:
            messages.error(request, 'Você deve aceitar os termos de uso e a LGPD.')
            return render(request, 'core/aceitar_termos.html')
        # Lógica de aceite: salva na sessão
        request.session['termos_aceitos'] = True
        messages.success(request, 'Termos aceitos com sucesso!')
        return redirect('core:register')
    return render(request, 'core/aceitar_termos.html')


def recusar_termos(request):
    # Lógica de recusa: remove flag da sessão
    request.session['termos_aceitos'] = False
    messages.info(request, 'Você recusou os termos. Não será possível prosseguir com o cadastro.')
    return render(request, 'core/recusar_termos.html')


def revogar_termos(request):
    # Lógica de revogação: remove flag da sessão
    request.session['termos_aceitos'] = False
    messages.info(request, 'Você revogou o aceite dos termos. Para continuar, aceite novamente.')
    return redirect('aceitar_termos')
