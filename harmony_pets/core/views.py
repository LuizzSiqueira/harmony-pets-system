

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
## Views de 2FA migradas para views_2fa.py
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PetForm(instance=pet)
    
    return render(request, 'core/pet_form.html', {
        'form': form,
        'pet': pet,
        'title': f'Editar {pet.nome}',
        'button_text': 'Salvar Alterações'
    })

@login_required
def excluir_pet(request, pet_id):
    """View para ocultar pet (soft delete) - mantém dados e vínculos"""
    try:
        local = request.user.localadocao
        pet = get_object_or_404(Pet, id=pet_id, local_adocao=local)
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Apenas organizações podem excluir pets.')
        return redirect('home')
    
    if request.method == 'POST':
        nome_pet = pet.nome
        # Soft delete - apenas oculta o pet
        pet.ativo = False
        pet.data_exclusao = timezone.now()
        pet.save()
        messages.success(request, f'Pet {nome_pet} foi ocultado com sucesso. Os dados e histórico foram preservados.')
        logger.warning(f"Pet ocultado (soft delete): id={pet_id} nome='{nome_pet}' por '{request.user.username}'")
        return redirect('gerenciar_pets')
    
    return render(request, 'core/confirmar_exclusao_pet.html', {'pet': pet})

@login_required
def alterar_status_pet(request, pet_id):
    """View para alterar status do pet (disponível, adotado, reservado)"""
    try:
        local = request.user.localadocao
        pet = get_object_or_404(Pet, id=pet_id, local_adocao=local)
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status in ['disponivel', 'adotado', 'reservado']:
            status_anterior = pet.get_status_display()
            pet.status = novo_status
            
            # Se foi adotado, registrar data
            if novo_status == 'adotado':
                from django.utils import timezone
                pet.data_adocao = timezone.now()
                # Se o pet está reservado, manter o adotado_por
                # Se não, tentar associar ao interessado da solicitação aprovada mais recente
                if not pet.adotado_por:
                    solicitacao_aprovada = pet.solicitacoes.filter(status='aprovada').order_by('-data_resposta').first()
                    if solicitacao_aprovada:
                        pet.adotado_por = solicitacao_aprovada.interessado
            else:
                pet.data_adocao = None
                pet.adotado_por = None
            pet.save()
            
            messages.success(request, f'Status do pet {pet.nome} alterado de "{status_anterior}" para "{pet.get_status_display()}".')
            logger.info(f"Status do pet alterado: id={pet.id} de '{status_anterior}' para '{pet.get_status_display()}' por '{request.user.username}'")
        else:
            messages.error(request, 'Status inválido.')
    
    return redirect('gerenciar_pets')

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
    """View para responder solicitação de adoção"""
    try:
        local = request.user.localadocao
        solicitacao = get_object_or_404(
            SolicitacaoAdocao, 
            id=solicitacao_id, 
            pet__local_adocao=local
        )
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        resposta = request.POST.get('resposta', '')
        
        if acao in ['aprovar', 'rejeitar']:
            from django.utils import timezone
            
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
    
    return redirect('solicitacoes_adocao')

@login_required
def agendar_entrevista(request, solicitacao_id):
    """View para agendar entrevista com o interessado"""
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
        return redirect('home')
    
    if request.method == 'POST':
        from django.utils import timezone
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
                mensagem = f"""Olá {solicitacao.interessado.usuario.first_name},

Sua entrevista para adoção do pet {solicitacao.pet.nome} foi agendada!

Data e Hora: {data_entrevista.strftime('%d/%m/%Y às %H:%M')}
Local: {local_entrevista}

Compareça no horário marcado.

Atenciosamente,
{solicitacao.pet.local_adocao.usuario.first_name}"""
                
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
            except ValueError:
                messages.error(request, 'Data inválida.')
        else:
            messages.error(request, 'Por favor, informe a data da entrevista.')
    
    return redirect('solicitacoes_adocao')

@login_required
def responder_entrevista(request, solicitacao_id):
    """View para aprovar ou rejeitar após entrevista"""
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
        return redirect('home')
    
    if request.method == 'POST':
        from django.utils import timezone
        
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
            mensagem = f"""Olá {solicitacao.interessado.usuario.first_name},

Você foi aprovado na entrevista para adoção do {solicitacao.pet.nome}! 🎉

Atenciosamente,
Equipe Harmony Pets"""
            
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
        elif resultado == 'rejeitar':
            solicitacao.status = 'entrevista_rejeitada'
            if observacoes:
                solicitacao.observacoes_entrevista = f"{solicitacao.observacoes_entrevista}\n\nResultado: Rejeitado\nMotivo: {observacoes}".strip()
            solicitacao.resposta_local = observacoes
            solicitacao.data_resposta = timezone.now()
            solicitacao.save()
            
            # Enviar e-mail de rejeição na entrevista
            assunto = f'Resultado da Entrevista - {solicitacao.pet.nome}'
            mensagem = f"""Olá {solicitacao.interessado.usuario.first_name},

Agradecemos seu interesse em adotar o {solicitacao.pet.nome}.

Após análise, não foi possível aprovar sua solicitação neste momento.

Atenciosamente,
Equipe Harmony Pets"""
            
            context = {
                'solicitacao': solicitacao,
                'observacoes': observacoes,
                'pets_url': request.build_absolute_uri(reverse('pets_list')),
            }
            enviar_email_notificacao(
                solicitacao.interessado.usuario.email,
                assunto,
                mensagem,
                'core/email_entrevista_rejeitada.html',
                context
            )
            
            messages.info(request, 'Entrevista rejeitada.')
        else:
            messages.error(request, 'Ação inválida.')
    
    return redirect('solicitacoes_adocao')

@login_required
def agendar_retirada(request, solicitacao_id):
    """View para agendar data de retirada do pet"""
    try:
        local = request.user.localadocao
        solicitacao = get_object_or_404(
                solicitacao.pet.status = 'reservado'
                solicitacao.pet.save()
                # Rejeitar outras solicitações pendentes para o mesmo pet
                from django.utils import timezone
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
                    from django.utils import timezone
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
                    mensagem = f"""Olá {solicitacao.interessado.usuario.first_name},

                    'data_hora': data_retirada.strftime('%d/%m/%Y às %H:%M'),

                    'endereco': solicitacao.pet.local_adocao.endereco,

                    'observacoes': observacoes,
                    'contato_email': solicitacao.pet.local_adocao.usuario.email,
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
        else:
            return redirect('core:solicitacoes_adocao')
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
            except ValueError:
                messages.error(request, 'Data inválida.')
        else:
            messages.error(request, 'Por favor, informe a data da retirada.')
    
    return redirect('core:solicitacoes_adocao')

@login_required
def aceitar_termo(request, solicitacao_id):
    """View para o interessado aceitar o termo de responsabilidade"""
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
        return redirect('home')
    
    if request.method == 'POST':
        from django.utils import timezone
        
        solicitacao.termo_aceito = True
        solicitacao.data_aceite_termo = timezone.now()
        solicitacao.save()
        
        # Notificar o local de adoção que o termo foi aceito
        assunto = f'Termo Aceito - {solicitacao.interessado.usuario.first_name} para {solicitacao.pet.nome}'
        mensagem = f"""Olá {solicitacao.pet.local_adocao.usuario.first_name},

{solicitacao.interessado.usuario.first_name} aceitou o Termo de Responsabilidade para adoção do {solicitacao.pet.nome}.

Atenciosamente,
Equipe Harmony Pets"""
        
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
    
    return redirect('minhas_solicitacoes_adocao')

@login_required
def cancelar_solicitacao(request, solicitacao_id):
    """View para o interessado cancelar sua solicitação de adoção com justificativa"""
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
        return redirect('home')
    
    if request.method == 'POST':
        justificativa = request.POST.get('justificativa', '').strip()
        
        if not justificativa or len(justificativa) < 10:
            messages.error(request, 'Por favor, forneça uma justificativa válida (mínimo 10 caracteres).')
            return redirect('minhas_solicitacoes_adocao')
        
        from django.utils import timezone
        
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
        mensagem = f"""Olá {solicitacao.pet.local_adocao.usuario.first_name},

{interessado.usuario.first_name} cancelou a solicitação de adoção do {solicitacao.pet.nome}.

O pet foi liberado novamente.

Atenciosamente,
Equipe Harmony Pets"""
        
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
    
    return redirect('minhas_solicitacoes_adocao')

@login_required
def historico_pet(request, pet_id):
    """View para o local de adoção visualizar o histórico completo do pet"""
    try:
        local = request.user.localadocao
        pet = get_object_or_404(Pet, id=pet_id, local_adocao=local)
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    # Buscar todas as solicitações relacionadas ao pet, ordenadas por data
    solicitacoes = SolicitacaoAdocao.objects.filter(pet=pet).select_related(
        'interessado__usuario'
    ).order_by('-data_solicitacao')
    
    # Estatísticas do histórico
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
    """View para confirmar que o pet foi retirado e a adoção foi concluída"""
    try:
        local = request.user.localadocao
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Acesso negado. Apenas locais de adoção podem confirmar adoções.')
        return redirect('home')
    
    # Buscar solicitação sem filtro de status primeiro para dar mensagem específica
    try:
        solicitacao = SolicitacaoAdocao.objects.get(
            id=solicitacao_id, 
            pet__local_adocao=local
        )
    except SolicitacaoAdocao.DoesNotExist:
        messages.error(request, 'Solicitação de adoção não encontrada.')
        return redirect('solicitacoes_adocao')
    
    # Verificar se a adoção já foi concluída
    if solicitacao.status == 'concluida':
        messages.info(request, 'Esta adoção já foi concluída anteriormente.')
        return redirect('solicitacoes_adocao')
    
    # Verificar se a solicitação está em status válido para confirmação
    if solicitacao.status not in ['agendado', 'entrevista_aprovada']:
        messages.error(request, f'Não é possível confirmar esta adoção. Status atual: {solicitacao.get_status_display()}')
        return redirect('solicitacoes_adocao')
    
    if request.method == 'POST':
        # Verificar se o interessado aceitou o termo
        if not solicitacao.termo_aceito:
            messages.error(request, 'Não é possível confirmar a adoção. O interessado ainda não aceitou o termo de responsabilidade.')
            return redirect('solicitacoes_adocao')
        
        solicitacao.status = 'concluida'
        solicitacao.save()
        
        # Marcar pet como adotado
        solicitacao.pet.status = 'adotado'
        solicitacao.pet.save()
        
        # Enviar e-mail de conclusão da adoção
        assunto = f'Parabéns! Adoção Concluída - {solicitacao.pet.nome} ❤️'
        mensagem = f"""Olá {solicitacao.interessado.usuario.first_name},

A adoção do {solicitacao.pet.nome} foi concluída com sucesso! 🎉

Desejamos muita felicidade!

Atenciosamente,
Equipe Harmony Pets"""
        
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
    
    return redirect('solicitacoes_adocao')


# Views para Two-Factor Authentication
@login_required
def setup_2fa(request):
    """Configurar autenticação de dois fatores"""
    user = request.user
    
    # Verificar se já tem 2FA configurado
    try:
        two_factor = user.two_factor_auth
        if two_factor.is_enabled:
            messages.warning(request, 'Autenticação de dois fatores já está ativa.')
            return redirect('profile')
    except TwoFactorAuth.DoesNotExist:
        two_factor = None
    
    # Criar ou obter instância de TwoFactorAuth para gerar QR Code
    if not two_factor:
        two_factor, created = TwoFactorAuth.objects.get_or_create(usuario=user)
    
    if request.method == 'POST':
        form = TwoFactorSetupForm(request.POST, instance=two_factor, user=user)
        if form.is_valid():
            two_factor = form.save()
            two_factor.is_enabled = True
            two_factor.save()
            
            messages.success(request, 'Autenticação de dois fatores configurada com sucesso!')
            return redirect('profile')
    else:
        form = TwoFactorSetupForm(instance=two_factor, user=user)
    
    # Gerar QR Code para o app
    qr_code_base64 = two_factor.get_qr_code()
    backup_codes = two_factor.backup_codes  # Acessar diretamente o campo
    
    return render(request, 'core/setup_2fa.html', {
        'form': form,
        'qr_code': qr_code_base64,
        'backup_codes': backup_codes,
    })


@login_required
def verify_2fa(request):
    """Verificar código 2FA durante login"""
    if request.method == 'POST':
        # Se a ação for enviar código por e-mail, gerar e enviar, sem validar o formulário de token
        if request.POST.get('action') == 'send_email_code':
            # Garante existir um registro de TwoFactorAuth para armazenar preferência/cfg
            two_factor, _ = TwoFactorAuth.objects.get_or_create(usuario=request.user)

            # Gerar código de 6 dígitos e armazenar no cache por 10 minutos
            import secrets
            code = f"{secrets.randbelow(1000000):06d}"
            from django.core.cache import cache
            cache_key = f"email_2fa_code_{request.user.id}"
            cache.set(cache_key, code, timeout=600)  # 10 minutos

            # Enviar e-mail com o código
            from django.core.mail import EmailMultiAlternatives
            from django.template.loader import render_to_string
            subject = 'Seu código de verificação (2FA) - Harmony Pets'
            context = {
                'user': request.user,
                'code': code,
            }
            text_body = render_to_string('core/email_2fa_code.txt', context)
            html_body = render_to_string('core/email_2fa_code.html', context)
            message = EmailMultiAlternatives(subject, text_body, to=[request.user.email])
            message.attach_alternative(html_body, 'text/html')
            try:
                message.send()
                messages.info(request, 'Código enviado por e-mail. Verifique sua caixa de entrada (e também o spam).')
            except Exception:
                messages.error(request, 'Não foi possível enviar o e-mail com o código. Tente novamente mais tarde.')

            form = TwoFactorLoginForm(user=request.user)
        else:
            form = TwoFactorLoginForm(request.POST, user=request.user)
            if form.is_valid():
                # Marcar como verificado na sessão
                request.session['2fa_verified'] = True
                request.session['2fa_verified_at'] = str(timezone.now())
                
                messages.success(request, 'Código verificado com sucesso!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
    else:
        initial = {}
        # Usa preferência persistida para acionar auto-envio
        try:
            tf = request.user.two_factor_auth
            pref = tf.preferred_method
        except Exception:
            pref = None
        if pref == 'email':
            initial['use_email_code'] = True
            # Auto-envio do código por e-mail se ainda não existir no cache
            from django.core.cache import cache
            cache_key = f"email_2fa_code_{request.user.id}"
            if cache.get(cache_key) is None:
                try:
                    # Gera e envia
                    import secrets
                    code = f"{secrets.randbelow(1000000):06d}"
                    cache.set(cache_key, code, timeout=600)
                    from django.core.mail import EmailMultiAlternatives
                    from django.template.loader import render_to_string
                    subject = 'Seu código de verificação (2FA) - Harmony Pets'
                    context = {'user': request.user, 'code': code}
                    text_body = render_to_string('core/email_2fa_code.txt', context)
                    html_body = render_to_string('core/email_2fa_code.html', context)
                    message = EmailMultiAlternatives(subject, text_body, to=[request.user.email])
                    message.attach_alternative(html_body, 'text/html')
                    message.send()
                    messages.info(request, 'Enviamos um código de verificação para o seu e-mail.')
                except Exception:
                    messages.error(request, 'Não foi possível enviar o código por e-mail. Tente novamente.')
        form = TwoFactorLoginForm(user=request.user, initial=initial)
    
    # Determinar preferência para o template
    preferred_method = 'totp'  # padrão
    try:
        tf = request.user.two_factor_auth
        preferred_method = tf.preferred_method
    except Exception:
        pass
    
    return render(request, 'core/verify_2fa.html', {
        'form': form,
        'preferred_method': preferred_method
    })


@login_required
def set_2fa_preference(request):
    """Define preferência do método de 2FA (autenticador ou e-mail) e persiste no modelo do usuário."""
    if request.method == 'POST':
        return redirect('profile')
    else:
        return redirect('core:solicitacoes_adocao')
    if method not in ('totp', 'email'):
        messages.error(request, 'Método inválido.')
        return redirect('profile')
    if method == 'email' and not (request.user.email and '@' in request.user.email):
        messages.error(request, 'Defina um e-mail válido no seu perfil para usar código por e-mail.')
        return redirect('profile')
    # Atualiza/Cria registro de TwoFactorAuth
    tf, _ = TwoFactorAuth.objects.get_or_create(usuario=request.user)
    tf.preferred_method = method
    # Se veio no POST, também atualiza a política de exigir a cada login
    require_every_login = request.POST.get('require_every_login')
    if require_every_login is not None:
        tf.require_every_login = True if str(require_every_login).lower() in ('1', 'true', 'on') else False
    tf.save()
    messages.success(request, 'Preferência de verificação em duas etapas atualizada.')
    return redirect('profile')


@login_required
def disable_2fa(request):
    """Desativar autenticação de dois fatores"""
    try:
        two_factor = request.user.two_factor_auth
    except TwoFactorAuth.DoesNotExist:
        messages.warning(request, 'Autenticação de dois fatores não está configurada.')
        return redirect('profile')
    
    if not two_factor.is_enabled:
        messages.warning(request, 'Autenticação de dois fatores já está desativada.')
        return redirect('profile')
    
    if request.method == 'POST':
        form = DisableTwoFactorForm(request.POST, user=request.user)
        if form.is_valid():
            two_factor.is_enabled = False
            two_factor.save()
            # Limpar verificação da sessão
            if '2fa_verified' in request.session:
                del request.session['2fa_verified']
            if '2fa_verified_at' in request.session:
                del request.session['2fa_verified_at']
            messages.success(request, 'Autenticação de dois fatores desativada com sucesso!')
            return redirect('profile')
    else:
        form = DisableTwoFactorForm(user=request.user)
    
    return render(request, 'core/disable_2fa.html', {'form': form})


def recusar_termos(request):
    """Tela explícita de recusa dos termos de uso.

    Objetivos:
    - Informar consequências da recusa.
    - Permitir ao usuário optar por sair ou voltar para ler novamente.
    - Não registra aceite; apenas reforça política e mantém bloqueio pelo middleware.
    """
    # Mesmo que já tenha aceitado previamente, mantemos esta página acessível
    # para permitir a revogação explícita do aceite, conforme política solicitada.
    return render(request, 'core/recusar_termos.html')


def get_client_ip(request):
    """Função para obter o IP real do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ==================== LOGS PARA ADMINISTRADORES ==================== #
@staff_member_required
def admin_logs(request):
    """Exibe últimas linhas do arquivo de logs para administradores/staff"""
    from django.conf import settings
    log_path = os.path.join(settings.LOG_DIR, 'app.log') if hasattr(settings, 'LOG_DIR') else ''

    # Parâmetros de filtro
    q = request.GET.get('q', '').strip()
    level = request.GET.get('level', '')
    try:
        n = int(request.GET.get('n', '500'))
    except ValueError:
        n = 500
    n = max(50, min(n, 5000))

    lines = []
    error = None
    if log_path and os.path.exists(log_path):
        try:
            # Lê o arquivo e pega as últimas N linhas
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
            lines = all_lines[-n:]
            # Aplica filtros simples
            if level:
                level = level.upper()
                lines = [ln for ln in lines if f" {level} " in ln]
            if q:
                lines = [ln for ln in lines if q.lower() in ln.lower()]
        except Exception as e:
            error = f"Não foi possível ler o arquivo de logs: {e}"
    else:
        error = 'Arquivo de logs não encontrado. A aplicação gravará logs assim que eventos ocorrerem.'

    # ==== AuditLog (banco) com filtro por usuário ====
    audit_user_param = request.GET.get('usuario') or request.GET.get('user') or ''
    audit_user_param = audit_user_param.strip()
    try:
        audit_limit = int(request.GET.get('audit_n', '200'))
    except ValueError:
        audit_limit = 200
    # Permite limites pequenos (ex.: 10) para testes e uso prático
    audit_limit = max(1, min(audit_limit, 1000))

    audit_qs = AuditLog.objects.select_related('usuario').all()
    # filtro adicional por caminho, se fornecido
    audit_path_q = (request.GET.get('audit_path') or '').strip()
    selected_user = None
    if audit_user_param:
        # Tenta interpretar como ID numérico primeiro
        if audit_user_param.isdigit():
            audit_qs = audit_qs.filter(usuario_id=int(audit_user_param))
            selected_user = User.objects.filter(id=int(audit_user_param)).first()
        else:
            audit_qs = audit_qs.filter(usuario__username__iexact=audit_user_param)
            selected_user = User.objects.filter(username__iexact=audit_user_param).first()

    if audit_path_q:
        audit_qs = audit_qs.filter(caminho__icontains=audit_path_q)
    audit_logs = list(audit_qs.order_by('-criado_em')[:audit_limit])
    # Lista de usuários distintos presentes em AuditLog (para dropdown)
    audit_users = User.objects.filter(auditlog__isnull=False).distinct().order_by('username')

    context = {
        'log_path': log_path,
        'lines': lines,
        'q': q,
        'level': level,
        'n': n,
        'error': error,
        # AuditLog extras
        'audit_logs': audit_logs,
        'audit_users': audit_users,
        'audit_user_param': audit_user_param,
        'selected_audit_user': selected_user,
        'audit_limit': audit_limit,
        'audit_path_q': audit_path_q,
    }
    return render(request, 'core/admin_logs.html', context)

# ==================== PAINEL QUALIDADE (Cobertura de Testes) ==================== #
@staff_member_required
def admin_quality(request):
    """Exibe métricas de qualidade simples (cobertura de testes) lendo coverage.xml.

    Requer que coverage.xml tenha sido gerado previamente (ex.: via script run_tests_coverage.sh).
    Mostra line-rate global e por pacote 'core'.
    """
    from django.conf import settings
    coverage_path = os.path.join(settings.BASE_DIR, 'harmony_pets', 'coverage.xml')
    global_rate = None
    core_rate = None
    lines_valid = None
    lines_covered = None
    timestamp_str = None
    error = None
    delta_global = None
    delta_core = None
    history = []
    history_path = os.path.join(settings.BASE_DIR, 'harmony_pets', 'quality_history.json')
    if os.path.exists(coverage_path):
        try:
            tree = ET.parse(coverage_path)
            root = tree.getroot()
            # atributos principais
            global_attr = root.attrib.get('line-rate')
            lines_valid_attr = root.attrib.get('lines-valid')
            lines_covered_attr = root.attrib.get('lines-covered')
            timestamp_attr = root.attrib.get('timestamp')
            if global_attr:
                try:
                    global_rate = round(float(global_attr) * 100, 2)
                except ValueError:
                    global_rate = None
            if lines_valid_attr and lines_covered_attr:
                try:
                    lines_valid = int(lines_valid_attr)
                    lines_covered = int(lines_covered_attr)
                except ValueError:
                    lines_valid = lines_covered = None
            if timestamp_attr and timestamp_attr.isdigit():
                try:
                    # coverage.py timestamp é epoch ms
                    dt = datetime.fromtimestamp(int(timestamp_attr)/1000.0)
                    timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    timestamp_str = None
            # procura pacote 'core'
            for pkg in root.findall('.//package'):
                if pkg.attrib.get('name') == 'core':
                    core_attr = pkg.attrib.get('line-rate')
                    if core_attr:
                        try:
                            core_rate = round(float(core_attr) * 100, 2)
                        except ValueError:
                            core_rate = None
                    break
        except Exception as e:
            error = f'Falha ao ler coverage.xml: {e}'
    else:
        error = 'coverage.xml não encontrado. Gere com o script de cobertura.'

    # Formata como string com ponto decimal independente de locale
    def fmt(rate):
        if rate is None:
            return None
        s = f"{rate:.2f}".rstrip('0').rstrip('.')
        return s
    # Carrega histórico existente
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r', encoding='utf-8') as hf:
                data = json.load(hf)
                history = data.get('history', []) if isinstance(data, dict) else []
        except Exception:
            history = []
    # Atualiza histórico se timestamp diferente do último
    if global_rate is not None and timestamp_str:
        last_ts = history[-1]['timestamp'] if history else None
        if last_ts != timestamp_str:
            entry = {
                'timestamp': timestamp_str,
                'global_rate': global_rate,
                'core_rate': core_rate,
                'lines_valid': lines_valid,
                'lines_covered': lines_covered,
            }
            history.append(entry)
            # mantém somente últimos 30
            history = history[-30:]
            try:
                with open(history_path, 'w', encoding='utf-8') as hf:
                    json.dump({'history': history}, hf, ensure_ascii=False, indent=2)
            except Exception:
                pass
    # Calcula deltas (comparação com penúltimo)
    if len(history) >= 2:
        delta_global = round(history[-1]['global_rate'] - history[-2]['global_rate'], 2)
        if history[-2].get('core_rate') is not None and history[-1].get('core_rate') is not None:
            delta_core = round(history[-1]['core_rate'] - history[-2]['core_rate'], 2)

    threshold_ok = global_rate is not None and global_rate >= 50.0
    missing_lines = None
    if lines_valid is not None and lines_covered is not None:
        missing_lines = lines_valid - lines_covered

    context = {
        'coverage_path': coverage_path,
        'global_rate': fmt(global_rate),
        'core_rate': fmt(core_rate),
        'error': error,
        'lines_valid': lines_valid,
        'lines_covered': lines_covered,
        'missing_lines': missing_lines,
        'timestamp_str': timestamp_str,
        'threshold_ok': threshold_ok,
        'delta_global': delta_global,
        'delta_core': delta_core,
        'history': history,
    }
    return render(request, 'core/admin_quality.html', context)

@staff_member_required
def admin_dashboard(request):
    """Dashboard administrativo consolidando KPIs, cobertura e auditoria.

    Combina estatísticas principais (usuários, pets, solicitações), métricas de 2FA,
    resumo de cobertura de testes (global e pacote core) e últimos eventos/a erros.
    """
    from django.conf import settings
    # KPIs essenciais
    try:
        users_total = User.objects.count()
        interessados_total = InteressadoAdocao.objects.count()
        locais_total = LocalAdocao.objects.count()
        pets_total = Pet.objects.count()
        pets_disponiveis = Pet.objects.filter(status='disponivel').count()
        pets_adotados = Pet.objects.filter(status='adotado').count()
        pets_reservados = Pet.objects.filter(status='reservado').count()
        sol_total = SolicitacaoAdocao.objects.count()
        sol_pendentes = SolicitacaoAdocao.objects.filter(status='pendente').count()
        sol_aprovadas = SolicitacaoAdocao.objects.filter(status='aprovada').count()
        sol_rejeitadas = SolicitacaoAdocao.objects.filter(status='rejeitada').count()
        twofa_total = TwoFactorAuth.objects.count()
        twofa_ativos = TwoFactorAuth.objects.filter(is_enabled=True).count()
        twofa_taxa = round((twofa_ativos / twofa_total) * 100, 1) if twofa_total else 0.0
    except Exception:
        users_total = interessados_total = locais_total = pets_total = 0
        pets_disponiveis = pets_adotados = pets_reservados = 0
        sol_total = sol_pendentes = sol_aprovadas = sol_rejeitadas = 0
        twofa_total = twofa_ativos = 0
        twofa_taxa = 0.0

    # Cobertura de testes (reuso da lógica de admin_quality de forma resumida)
    coverage_path = os.path.join(settings.BASE_DIR, 'harmony_pets', 'coverage.xml')
    global_rate = None
    core_rate = None
    if os.path.exists(coverage_path):
        try:
            tree = ET.parse(coverage_path)
            root = tree.getroot()
            global_attr = root.attrib.get('line-rate')
            if global_attr:
                global_rate = round(float(global_attr) * 100, 2)
            # pacote core
            for pkg in root.findall('packages/package'):
                if pkg.attrib.get('name') == 'core':
                    pr = pkg.attrib.get('line-rate')
                    if pr:
                        core_rate = round(float(pr) * 100, 2)
                    break
        except Exception:
            pass

    # Auditoria
    audit_recent = list(AuditLog.objects.order_by('-criado_em')[:10])
    audit_errors_recent = list(AuditLog.objects.filter(status_code__gte=400).order_by('-criado_em')[:10])

    context = {
        'kpis': {
            'users_total': users_total,
            'interessados_total': interessados_total,
            'locais_total': locais_total,
            'pets_total': pets_total,
            'pets_disponiveis': pets_disponiveis,
            'pets_adotados': pets_adotados,
            'pets_reservados': pets_reservados,
            'sol_total': sol_total,
            'sol_pendentes': sol_pendentes,
            'sol_aprovadas': sol_aprovadas,
            'sol_rejeitadas': sol_rejeitadas,
            'twofa_total': twofa_total,
            'twofa_ativos': twofa_ativos,
            'twofa_taxa': twofa_taxa,
        },
        'coverage_global': global_rate,
        'coverage_core': core_rate,
        'audit_recent': audit_recent,
        'audit_errors_recent': audit_errors_recent,
    }
    return render(request, 'core/admin_dashboard.html', context)

# ==================== API: Sugestão de Emoji ==================== #

@require_GET
def sugerir_emoji(request):
    """Sugere um emoji usando a API Ninjas com base no termo informado.

    Query params:
      - termo: string de busca (ex.: 'dog', 'cat', 'panda')
      - group (opcional): restringe a um grupo (ex.: 'animals_nature')

    Retorna JSON: { ok: bool, emoji: str, error?: str }
    """
    termo = (request.GET.get('termo') or '').strip()
    group = (request.GET.get('group') or '').strip() or None
    if not termo:
        return JsonResponse({'ok': False, 'emoji': '', 'error': 'missing-term'}, status=400)

    # Primeira tentativa: se group veio, tenta com group. Depois, sem group.
    emoji_char = ''
    try:
        if group:
            resultados = buscar_emoji_animais(termo, group=group, limit=1)
            if resultados:
                emoji_char = resultados[0].get('character') or ''
        if not emoji_char:
            # fallback sem grupo
            emoji_char = obter_emoji_animal(termo)
    except EmojiAPIError as e:
        return JsonResponse({'ok': False, 'emoji': '', 'error': str(e)[:200]}, status=200)

    return JsonResponse({'ok': bool(emoji_char), 'emoji': emoji_char})