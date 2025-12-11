from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.urls import reverse
from .models import Pet, InteressadoAdocao, SolicitacaoAdocao, LocalAdocao, AceitacaoTermos
from .forms import InteressadoAdocaoForm
from .utils import enviar_email_notificacao

@login_required
def solicitar_adocao_view(request, pet_id):
    try:
        interessado = request.user.interessadoadocao
    except InteressadoAdocao.DoesNotExist:
        messages.error(request, 'Você precisa completar seu cadastro como interessado em adoção para solicitar um pet.')
        return redirect('core:edit_profile')

    pet = get_object_or_404(Pet, id=pet_id)
    if pet.status != 'disponivel':
        messages.error(request, 'Este pet não está disponível para adoção.')
        return redirect('core:pets_list')

    # Verifica se já existe uma solicitação pendente para este pet/interessado
    existe_solicitacao = SolicitacaoAdocao.objects.filter(pet=pet, interessado=interessado, status__in=['pendente', 'em_entrevista', 'entrevista_aprovada', 'agendado']).exists()
    if existe_solicitacao:
        messages.info(request, 'Você já possui uma solicitação ativa para este pet.')
        return redirect('core:minhas_solicitacoes_adocao')

    if request.method == 'POST':
        # Cria a solicitação
        solicitacao = SolicitacaoAdocao.objects.create(
            pet=pet,
            interessado=interessado,
            status='pendente',
            data_solicitacao=timezone.now()
        )
        # Notifica o local de adoção
        assunto = f'Nova Solicitação de Adoção - {pet.nome}'
        mensagem = f"""Olá {pet.local_adocao.usuario.first_name},\n\n{interessado.usuario.first_name} solicitou a adoção do pet {pet.nome}.\n\nAcesse o painel para gerenciar as solicitações.\n\nAtenciosamente,\nEquipe Harmony Pets"""
        context = {
            'solicitacao': solicitacao,
            'pet': pet,
            'interessado': interessado,
        }
        enviar_email_notificacao(
            pet.local_adocao.usuario.email,
            assunto,
            mensagem,
            'core/email_nova_solicitacao.html',
            context
        )
        messages.success(request, 'Solicitação de adoção enviada com sucesso!')
        return redirect('core:minhas_solicitacoes_adocao')

    return render(request, 'core/solicitar_adocao.html', {'pet': pet})

@login_required
def minhas_solicitacoes_adocao(request):
    try:
        interessado = request.user.interessadoadocao
        solicitacoes = interessado.solicitacoes.select_related('pet', 'pet__local_adocao').order_by('-data_solicitacao')
        return render(request, 'core/minhas_solicitacoes_adocao.html', {'solicitacoes': solicitacoes})
    except InteressadoAdocao.DoesNotExist:
        messages.warning(request, 'Você precisa completar seu cadastro como interessado em adoção para acessar suas solicitações. Preencha seus dados abaixo.')
        return redirect('/edit-profile/?criar_perfil=interessado')
    except Exception as e:
        messages.error(request, 'Não foi possível recuperar suas solicitações de adoção.')
        return redirect('core:profile')

@login_required
def meus_pets_adotados(request):
    try:
        interessado = request.user.interessadoadocao
        pets_adotados = interessado.pets_adotados.all().order_by('-data_adocao')
        return render(request, 'core/pets_adotados.html', {'pets_adotados': pets_adotados})
    except Exception:
        messages.error(request, 'Não foi possível recuperar seus pets adotados.')
        return redirect('profile')

@login_required
def solicitacoes_adocao(request):
    """View para gerenciar solicitações de adoção recebidas"""
    try:
        local = request.user.localadocao
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Apenas organizações podem ver solicitações.')
        return redirect('home')
    # Buscar solicitações para pets do local
    solicitacoes = SolicitacaoAdocao.objects.filter(
        pet__local_adocao=local
    ).order_by('-data_solicitacao')
    # Filtros
    status_filtro = request.GET.get('status')
    status_validos = [
        'pendente', 'em_entrevista', 'entrevista_aprovada', 'entrevista_rejeitada',
        'agendado', 'concluida', 'rejeitada', 'cancelada'
    ]
    if status_filtro and status_filtro in status_validos:
        solicitacoes = solicitacoes.filter(status=status_filtro)
    # Paginação
    paginator = Paginator(solicitacoes, 10)
    page_number = request.GET.get('page')
    solicitacoes_page = paginator.get_page(page_number)
    # Estatísticas
    stats = {
        'total': SolicitacaoAdocao.objects.filter(pet__local_adocao=local).count(),
        'pendentes': SolicitacaoAdocao.objects.filter(pet__local_adocao=local, status='pendente').count(),
        'em_entrevista': SolicitacaoAdocao.objects.filter(pet__local_adocao=local, status='em_entrevista').count(),
        'aprovadas': SolicitacaoAdocao.objects.filter(pet__local_adocao=local, status='entrevista_aprovada').count(),
        'agendadas': SolicitacaoAdocao.objects.filter(pet__local_adocao=local, status='agendado').count(),
        'concluidas': SolicitacaoAdocao.objects.filter(pet__local_adocao=local, status='concluida').count(),
    }
    context = {
        'solicitacoes': solicitacoes_page,
        'stats': stats,
        'status_atual': status_filtro,
    }
    return render(request, 'core/solicitacoes_adocao.html', context)

@login_required
def responder_solicitacao(request, solicitacao_id):
    try:
        local = request.user.localadocao
        solicitacao = get_object_or_404(
            SolicitacaoAdocao, 
            id=solicitacao_id, 
            pet__local_adocao=local
        )
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    if request.method == 'POST':
        acao = request.POST.get('acao')
        resposta = request.POST.get('resposta', '')
        if acao in ['aprovar', 'rejeitar']:
            solicitacao.status = 'aprovada' if acao == 'aprovar' else 'rejeitada'
            solicitacao.resposta_local = resposta
            solicitacao.data_resposta = timezone.now()
            solicitacao.save()
            # Se aprovada, marcar pet como reservado
            if acao == 'aprovar':
                solicitacao.pet.status = 'reservado'
                solicitacao.pet.adotado_por = solicitacao.interessado
                solicitacao.pet.save()
                # Rejeitar outras solicitações para o mesmo pet
                SolicitacaoAdocao.objects.filter(
                    pet=solicitacao.pet,
                    status='pendente'
                ).exclude(id=solicitacao.id).update(
                    status='rejeitada',
                    resposta_local='Pet já foi reservado para outro interessado.',
                    data_resposta=timezone.now()
                )
            action_text = 'aprovada' if acao == 'aprovar' else 'rejeitada'
            messages.success(request, f'Solicitação {action_text} com sucesso!')
        else:
            messages.error(request, 'Ação inválida.')
        return redirect('core:solicitacoes_adocao')
    return redirect('core:solicitacoes_adocao')

@login_required
def agendar_entrevista(request, solicitacao_id):
    try:
        local = request.user.localadocao
        solicitacao = get_object_or_404(
            SolicitacaoAdocao, 
            id=solicitacao_id, 
            pet__local_adocao=local,
            status='pendente'
        )
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    if request.method == 'POST':
        from datetime import datetime
        data_entrevista_str = request.POST.get('data_entrevista')
        local_entrevista = request.POST.get('local_entrevista', '')
        observacoes = request.POST.get('observacoes_entrevista', '')
        if data_entrevista_str:
            try:
                data_entrevista_naive = datetime.strptime(data_entrevista_str, '%Y-%m-%dT%H:%M')
                data_entrevista = timezone.make_aware(data_entrevista_naive)
                solicitacao.data_entrevista = data_entrevista
                solicitacao.local_entrevista = local_entrevista
                solicitacao.observacoes_entrevista = observacoes
                solicitacao.status = 'em_entrevista'
                solicitacao.save()
                # Enviar e-mail para o interessado sobre o agendamento da entrevista
                assunto = f'Entrevista Agendada - Adoção de {solicitacao.pet.nome}'
                mensagem = f"""Olá {solicitacao.interessado.usuario.first_name},\n\nSua entrevista para adoção do pet {solicitacao.pet.nome} foi agendada!\n\nData e Hora: {data_entrevista.strftime('%d/%m/%Y às %H:%M')}\nLocal: {local_entrevista}\n\nCompareça no horário marcado.\n\nAtenciosamente,\n{solicitacao.pet.local_adocao.usuario.first_name}"""
                context = {
                    'solicitacao': solicitacao,
                    'data_hora': data_entrevista.strftime('%d/%m/%Y às %H:%M'),
                    'local': local_entrevista,
                    'observacoes': observacoes,
                    'contato_email': solicitacao.pet.local_adocao.usuario.email,
                    'contato_telefone': solicitacao.pet.local_adocao.telefone,
                }
                enviar_email_notificacao(
                    solicitacao.interessado.usuario.email,
                    assunto,
                    mensagem,
                    'core/email_entrevista_agendada.html',
                    context
                )
                messages.success(request, 'Entrevista agendada com sucesso!')
                return redirect('core:solicitacoes_adocao')
            except ValueError:
                messages.error(request, 'Data inválida.')
                return redirect('core:solicitacoes_adocao')
        else:
            messages.error(request, 'Por favor, informe a data da entrevista.')
            return redirect('core:solicitacoes_adocao')
    return redirect('core:solicitacoes_adocao')

@login_required
def responder_entrevista(request, solicitacao_id):
    try:
        local = request.user.localadocao
        solicitacao = get_object_or_404(
            SolicitacaoAdocao, 
            id=solicitacao_id, 
            pet__local_adocao=local,
            status='em_entrevista'
        )
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    if request.method == 'POST':
        resultado = request.POST.get('resultado')  # 'aprovar' ou 'rejeitar'
        observacoes = request.POST.get('observacoes', '')
        if resultado == 'aprovar':
            solicitacao.status = 'entrevista_aprovada'
            if observacoes:
                solicitacao.observacoes_entrevista = f"{solicitacao.observacoes_entrevista}\n\nResultado: Aprovado\n{observacoes}".strip()
            else:
                solicitacao.observacoes_entrevista = f"{solicitacao.observacoes_entrevista}\n\nResultado: Aprovado".strip()
            solicitacao.data_resposta = timezone.now()
            solicitacao.save()
            # Enviar e-mail de aprovação na entrevista
            assunto = f'Parabéns! Entrevista Aprovada - {solicitacao.pet.nome}'
            mensagem = f"""Olá {solicitacao.interessado.usuario.first_name},\n\nVocê foi aprovado na entrevista para adoção do {solicitacao.pet.nome}! 🎉\n\nAtenciosamente,\nEquipe Harmony Pets"""
            context = {
                'solicitacao': solicitacao,
                'observacoes': observacoes,
            }
            enviar_email_notificacao(
                solicitacao.interessado.usuario.email,
                assunto,
                mensagem,
                'core/email_entrevista_aprovada.html',
                context
            )
            messages.success(request, 'Entrevista aprovada! Agora você pode agendar a retirada do pet.')
            return redirect('core:solicitacoes_adocao')
        elif resultado == 'rejeitar':
            solicitacao.status = 'entrevista_rejeitada'
            if observacoes:
                solicitacao.observacoes_entrevista = f"{solicitacao.observacoes_entrevista}\n\nResultado: Rejeitado\nMotivo: {observacoes}".strip()
            solicitacao.resposta_local = observacoes
            solicitacao.data_resposta = timezone.now()
            solicitacao.save()
            # Enviar e-mail de rejeição na entrevista
            assunto = f'Resultado da Entrevista - {solicitacao.pet.nome}'
            mensagem = f"""Olá {solicitacao.interessado.usuario.first_name},\n\nAgradecemos seu interesse em adotar o {solicitacao.pet.nome}.\n\nApós análise, não foi possível aprovar sua solicitação neste momento.\n\nAtenciosamente,\nEquipe Harmony Pets"""
            context = {
                'solicitacao': solicitacao,
                'observacoes': observacoes,
                'pets_url': request.build_absolute_uri(reverse('core:pets_list')),
            }
            enviar_email_notificacao(
                solicitacao.interessado.usuario.email,
                assunto,
                mensagem,
                'core/email_entrevista_rejeitada.html',
                context
            )
            messages.info(request, 'Entrevista rejeitada.')
            return redirect('core:solicitacoes_adocao')
        else:
            messages.error(request, 'Ação inválida.')
            return redirect('core:solicitacoes_adocao')
    return redirect('core:solicitacoes_adocao')

@login_required
def agendar_retirada(request, solicitacao_id):
    try:
        local = request.user.localadocao
        solicitacao = get_object_or_404(
            SolicitacaoAdocao, 
            id=solicitacao_id, 
            pet__local_adocao=local,
            status='entrevista_aprovada'
        )
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    if request.method == 'POST':
        from datetime import datetime
        data_retirada_str = request.POST.get('data_retirada')
        observacoes = request.POST.get('observacoes_retirada', '')
        if data_retirada_str:
            try:
                data_retirada_naive = datetime.strptime(data_retirada_str, '%Y-%m-%dT%H:%M')
                data_retirada = timezone.make_aware(data_retirada_naive)
                solicitacao.data_retirada = data_retirada
                solicitacao.observacoes_retirada = observacoes
                solicitacao.status = 'agendado'
                solicitacao.save()
                # Marcar pet como reservado
                solicitacao.pet.status = 'reservado'
                solicitacao.pet.adotado_por = solicitacao.interessado
                solicitacao.pet.save()
                # Rejeitar outras solicitações pendentes para o mesmo pet
                SolicitacaoAdocao.objects.filter(
                    pet=solicitacao.pet,
                    status__in=['pendente', 'em_entrevista']
                ).exclude(id=solicitacao.id).update(
                    status='rejeitada',
                    resposta_local='Pet já foi reservado para outro interessado.',
                    data_resposta=timezone.now()
                )
                # Enviar e-mail com data de retirada agendada
                assunto = f'Retirada Agendada! Seu novo pet {solicitacao.pet.nome} te espera! 🎉'
                mensagem = f"""Olá {solicitacao.interessado.usuario.first_name},\n\nA retirada do {solicitacao.pet.nome} foi agendada!\n\nData e Hora: {data_retirada.strftime('%d/%m/%Y às %H:%M')}\n\nAtenciosamente,\nEquipe Harmony Pets"""
                context = {
                    'solicitacao': solicitacao,
                    'data_hora': data_retirada.strftime('%d/%m/%Y às %H:%M'),
                    'endereco': solicitacao.pet.local_adocao.endereco,
                    'observacoes': observacoes,
                    'contato_email': solicitacao.pet.local_adocao.usuario.email,
                    'contato_telefone': solicitacao.pet.local_adocao.telefone,
                }
                enviar_email_notificacao(
                    solicitacao.interessado.usuario.email,
                    assunto,
                    mensagem,
                    'core/email_retirada_agendada.html',
                    context
                )
                messages.success(request, f'Retirada agendada para {data_retirada.strftime("%d/%m/%Y às %H:%M")}!')
                return redirect('core:solicitacoes_adocao')
            except ValueError:
                messages.error(request, 'Data inválida.')
                return redirect('core:solicitacoes_adocao')
        else:
            messages.error(request, 'Por favor, informe a data da retirada.')
            return redirect('core:solicitacoes_adocao')
    return redirect('core:solicitacoes_adocao')

@login_required
def aceitar_termo(request, solicitacao_id):
    try:
        interessado = request.user.interessadoadocao
        solicitacao = get_object_or_404(
            SolicitacaoAdocao, 
            id=solicitacao_id, 
            interessado=interessado,
            status__in=['agendado', 'em_entrevista', 'entrevista_aprovada']
        )
    except InteressadoAdocao.DoesNotExist:
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    if request.method == 'POST':
        solicitacao.termo_aceito = True
        solicitacao.data_aceite_termo = timezone.now()
        solicitacao.save()
        # Notificar o local de adoção que o termo foi aceito
        assunto = f'Termo Aceito - {solicitacao.interessado.usuario.first_name} para {solicitacao.pet.nome}'
        mensagem = f"""Olá {solicitacao.pet.local_adocao.usuario.first_name},\n\n{solicitacao.interessado.usuario.first_name} aceitou o Termo de Responsabilidade para adoção do {solicitacao.pet.nome}.\n\nAtenciosamente,\nEquipe Harmony Pets"""
        context = {
            'solicitacao': solicitacao,
            'data_aceite': timezone.now().strftime('%d/%m/%Y às %H:%M'),
            'data_retirada': solicitacao.data_retirada.strftime('%d/%m/%Y às %H:%M') if solicitacao.data_retirada else None,
        }
        enviar_email_notificacao(
            solicitacao.pet.local_adocao.usuario.email,
            assunto,
            mensagem,
            'core/email_termo_aceito.html',
            context
        )
        messages.success(request, 'Termo de responsabilidade aceito com sucesso! ✓')
        return redirect('core:minhas_solicitacoes_adocao')
    return redirect('core:minhas_solicitacoes_adocao')

@login_required
def cancelar_solicitacao(request, solicitacao_id):
    try:
        interessado = request.user.interessadoadocao
        solicitacao = get_object_or_404(
            SolicitacaoAdocao, 
            id=solicitacao_id, 
            interessado=interessado,
            status__in=['pendente', 'em_entrevista', 'entrevista_aprovada', 'agendado']
        )
    except InteressadoAdocao.DoesNotExist:
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    if request.method == 'POST':
        justificativa = request.POST.get('justificativa', '').strip()
        if not justificativa or len(justificativa) < 10:
            messages.error(request, 'Por favor, forneça uma justificativa válida (mínimo 10 caracteres).')
            return redirect('core:minhas_solicitacoes_adocao')
        solicitacao.status = 'cancelada'
        solicitacao.justificativa_cancelamento = justificativa
        solicitacao.data_cancelamento = timezone.now()
        solicitacao.save()
        # Se o pet estava reservado, liberar para outras solicitações
        if solicitacao.pet.status == 'reservado' and solicitacao.pet.adotado_por == interessado:
            solicitacao.pet.status = 'disponivel'
            solicitacao.pet.adotado_por = None
            solicitacao.pet.save()
        # Notificar o local de adoção sobre o cancelamento
        assunto = f'Solicitação Cancelada - {solicitacao.pet.nome}'
        mensagem = f"""Olá {solicitacao.pet.local_adocao.usuario.first_name},\n\n{interessado.usuario.first_name} cancelou a solicitação de adoção do {solicitacao.pet.nome}.\n\nO pet foi liberado novamente.\n\nAtenciosamente,\nEquipe Harmony Pets"""
        context = {
            'solicitacao': solicitacao,
            'interessado': interessado,
            'data_cancelamento': timezone.now().strftime('%d/%m/%Y às %H:%M'),
            'justificativa': justificativa,
        }
        enviar_email_notificacao(
            solicitacao.pet.local_adocao.usuario.email,
            assunto,
            mensagem,
            'core/email_solicitacao_cancelada.html',
            context
        )
        messages.success(request, 'Solicitação cancelada com sucesso.')
        return redirect('core:minhas_solicitacoes_adocao')
    return redirect('core:minhas_solicitacoes_adocao')

@login_required
def historico_pet(request, pet_id):
    try:
        local = request.user.localadocao
        pet = get_object_or_404(Pet, id=pet_id, local_adocao=local)
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    solicitacoes = SolicitacaoAdocao.objects.filter(pet=pet).select_related(
        'interessado__usuario'
    ).order_by('-data_solicitacao')
    stats = {
        'total': solicitacoes.count(),
        'pendentes': solicitacoes.filter(status='pendente').count(),
        'em_entrevista': solicitacoes.filter(status='em_entrevista').count(),
        'aprovadas': solicitacoes.filter(status='entrevista_aprovada').count(),
        'agendadas': solicitacoes.filter(status='agendado').count(),
        'concluidas': solicitacoes.filter(status='concluida').count(),
        'rejeitadas': solicitacoes.filter(status__in=['rejeitada', 'entrevista_rejeitada']).count(),
        'canceladas': solicitacoes.filter(status='cancelada').count(),
    }
    context = {
        'pet': pet,
        'solicitacoes': solicitacoes,
        'stats': stats,
    }
    return render(request, 'core/historico_pet.html', context)

@login_required
def confirmar_adocao(request, solicitacao_id):
    try:
        local = request.user.localadocao
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Acesso negado. Apenas locais de adoção podem confirmar adoções.')
        return redirect('core:home')
    try:
        solicitacao = SolicitacaoAdocao.objects.get(
            id=solicitacao_id, 
            pet__local_adocao=local
        )
    except SolicitacaoAdocao.DoesNotExist:
        messages.error(request, 'Solicitação de adoção não encontrada.')
        return redirect('core:solicitacoes_adocao')
    if solicitacao.status == 'concluida':
        messages.info(request, 'Esta adoção já foi concluída anteriormente.')
        return redirect('core:solicitacoes_adocao')
    if solicitacao.status not in ['agendado', 'entrevista_aprovada']:
        messages.error(request, f'Não é possível confirmar esta adoção. Status atual: {solicitacao.get_status_display()}')
        return redirect('core:solicitacoes_adocao')
    if request.method == 'POST':
        if not solicitacao.termo_aceito:
            messages.error(request, 'Não é possível confirmar a adoção. O interessado ainda não aceitou o termo de responsabilidade.')
            return redirect('core:solicitacoes_adocao')
        solicitacao.status = 'concluida'
        solicitacao.save()
        solicitacao.pet.status = 'adotado'
        solicitacao.pet.save()
        assunto = f'Parabéns! Adoção Concluída - {solicitacao.pet.nome} ❤️'
        mensagem = f"""Olá {solicitacao.interessado.usuario.first_name},\n\nA adoção do {solicitacao.pet.nome} foi concluída com sucesso! 🎉\n\nDesejamos muita felicidade!\n\nAtenciosamente,\nEquipe Harmony Pets"""
        context = {
            'solicitacao': solicitacao,
            'contato_nome': solicitacao.pet.local_adocao.usuario.first_name,
            'contato_email': solicitacao.pet.local_adocao.usuario.email,
            'contato_telefone': solicitacao.pet.local_adocao.telefone,
        }
        enviar_email_notificacao(
            solicitacao.interessado.usuario.email,
            assunto,
            mensagem,
            'core/email_adocao_concluida.html',
            context
        )
        messages.success(request, 'Adoção concluída com sucesso! 🎉')
        return redirect('core:solicitacoes_adocao')
    return redirect('core:solicitacoes_adocao')
