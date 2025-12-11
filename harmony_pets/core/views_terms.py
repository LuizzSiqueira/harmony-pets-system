from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import AceitacaoTermos
import os

def termos_uso(request):
    return render(request, 'core/termos_uso.html')

def aceitar_termos(request):
    if request.method == 'POST':
        termos_uso_aceito = request.POST.get('termos_uso') == 'on'
        lgpd_aceito = request.POST.get('lgpd') == 'on'
        if not termos_uso_aceito or not lgpd_aceito:
            messages.error(request, 'Você deve aceitar os termos de uso e a LGPD.')
            return render(request, 'core/termos_uso.html')
        request.session['termos_aceitos'] = True
        messages.success(request, 'Termos aceitos com sucesso!')
        return redirect('core:register')
    return render(request, 'core/termos_uso.html')

def recusar_termos(request):
    request.session['termos_aceitos'] = False
    messages.info(request, 'Você recusou os termos. Não será possível prosseguir com o cadastro.')
    return render(request, 'core/recusar_termos.html')

@require_POST
def revogar_termos(request):
    request.session['termos_aceitos'] = False
    messages.info(request, 'Você revogou o aceite dos termos. Para continuar, aceite novamente.')
    return redirect('core:termos_uso')

def politica_privacidade(request):
    return redirect(f"{reverse('termos_uso')}#politica-privacidade")

def contato(request):
    meios = {
        'email': os.environ.get('HARMONY_CONTACT_EMAIL', 'contato@harmonypets.org'),
        'telefone': os.environ.get('HARMONY_CONTACT_PHONE', '(11) 0000-0000'),
        'instagram': os.environ.get('HARMONY_CONTACT_INSTAGRAM', '@harmonypets'),
        'facebook': os.environ.get('HARMONY_CONTACT_FACEBOOK', 'facebook.com/harmonypets'),
        'horario': 'Seg – Sex, 09h00 – 18h00 (Horário de Brasília)',
        'suporte': 'Tempo médio de resposta: até 2 dias úteis',
    }
    return render(request, 'core/contato.html', {'meios': meios})
