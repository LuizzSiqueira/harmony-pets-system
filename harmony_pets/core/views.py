
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from .forms import (
    InteressadoAdocaoForm, 
    LocalAdocaoForm, 
    PetForm,
    TwoFactorSetupForm,
    TwoFactorLoginForm,
    DisableTwoFactorForm,
    EditUserForm,
    EditInteressadoForm,
    EditLocalForm,
    ChangePasswordForm,
    AppPasswordResetForm,
)
from .models import InteressadoAdocao, LocalAdocao, Pet, SolicitacaoAdocao, TwoFactorAuth, AceitacaoTermos
from django.contrib.auth.models import User
from .utils import calcular_distancia
from .utils import obter_emoji_animal, buscar_emoji_animais, EmojiAPIError
import io
import base64
import os
import logging
logger = logging.getLogger('core')

from django.contrib.auth.views import PasswordResetView

class AppPasswordResetView(PasswordResetView):
    template_name = 'core/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.txt'
    html_email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    form_class = AppPasswordResetForm
    extra_email_context = {
        'site_name': 'Harmony Pets',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.utils import timezone
        context['year'] = timezone.now().year
        context.setdefault('site_name', 'Harmony Pets')
        return context

    def form_valid(self, form):
        logger.info(
            "Password reset: enviando e-mail com templates (txt=%s, html=%s)",
            self.email_template_name,
            self.html_email_template_name,
        )
        return super().form_valid(form)

# View para o interessado ver suas solicitações de adoção

# View administrativa para anonimizar todos os dados sensíveis dos interessados
from django.contrib.admin.views.decorators import staff_member_required
from .utils import anonimizar_dados_interessado

@staff_member_required
def anonimizar_interessados(request):
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado.')
        return redirect('profile')
    interessados = InteressadoAdocao.objects.all()
    for interessado in interessados:
        anonimizar_dados_interessado(interessado)
    messages.success(request, 'Dados sensíveis anonimizados com sucesso!')
    return redirect('admin:index')
@login_required
def minhas_solicitacoes_adocao(request):
    try:
        interessado = request.user.interessadoadocao
        solicitacoes = interessado.solicitacoes.select_related('pet').order_by('-data_solicitacao')
        return render(request, 'core/minhas_solicitacoes_adocao.html', {'solicitacoes': solicitacoes})
    except Exception:
        messages.error(request, 'Não foi possível recuperar suas solicitações de adoção.')
        return redirect('profile')

# View para listar pets adotados pelo usuário interessado
@login_required
def meus_pets_adotados(request):
    try:
        interessado = request.user.interessadoadocao
        pets_adotados = interessado.pets_adotados.all().order_by('-data_adocao')
        return render(request, 'core/pets_adotados.html', {'pets_adotados': pets_adotados})
    except Exception:
        messages.error(request, 'Não foi possível recuperar seus pets adotados.')
        return redirect('profile')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from .forms import (
    InteressadoAdocaoForm, 
    LocalAdocaoForm, 
    PetForm,
    TwoFactorSetupForm,
    TwoFactorLoginForm,
    DisableTwoFactorForm,
    EditUserForm,
    EditInteressadoForm,
    EditLocalForm,
    ChangePasswordForm
)
from .models import InteressadoAdocao, LocalAdocao, Pet, SolicitacaoAdocao, TwoFactorAuth, AceitacaoTermos
from .utils import calcular_distancia
import io
import base64


@login_required
def delete_account_view(request):
    """View para solicitar exclusão da conta do usuário"""
    user = request.user
    if request.method == 'POST':
        # Exclusão imediata e permanente
        username = user.username
        # Log do evento antes da remoção do usuário
        logger.warning(f"Exclusão de conta imediata solicitada por '{username}' (id={user.id})")
        # Efetua logout para limpar sessão e, em seguida, remove o usuário
        logout(request)
        try:
            user.delete()
        except Exception:
            # Em caso de falha inesperada, garante que o usuário ao menos fique inativo
            try:
                user.is_active = False
                user.save()
            except Exception:
                pass
        messages.success(request, f'Sua conta "{username}" foi excluída permanentemente.')
        return redirect('home')
    return redirect('profile')

def login_view(request):
    error_message = None
    blocked_message = None
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        username = request.POST.get('username')
        user_obj = None
        if username:
            try:
                user_obj = User.objects.get(username=username)
            except User.DoesNotExist:
                user_obj = None
        login_attempt = None
        if user_obj:
            from .models import UserLoginAttempt
            login_attempt, _ = UserLoginAttempt.objects.get_or_create(user=user_obj)
            if login_attempt.is_blocked():
                blocked_message = f"Usuário bloqueado por excesso de tentativas. Tente novamente após {login_attempt.blocked_until.strftime('%d/%m/%Y %H:%M:%S')}."
        if login_attempt and login_attempt.is_blocked():
            blocked_message = f"Usuário bloqueado por excesso de tentativas. Tente novamente após {login_attempt.blocked_until.strftime('%d/%m/%Y %H:%M:%S')}."
        elif form.is_valid() and user_obj:
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Resetar tentativas ao logar
                if login_attempt:
                    login_attempt.reset_attempts()
                login(request, user)
                logger.info(f"Login bem-sucedido para usuário '{username}' do IP {get_client_ip(request)}")
                # Limpa flags de 2FA desta sessão, sempre que logar novamente
                request.session.pop('2fa_verified', None)
                request.session.pop('2fa_verified_at', None)
                # Força verificação 2FA se TOTP estiver ativo ou preferência por e-mail estiver configurada
                try:
                    two_factor = user.two_factor_auth
                    totp_enabled = bool(two_factor.is_enabled)
                    pref_email = (two_factor.preferred_method == 'email')
                    require_every_login = bool(two_factor.require_every_login)
                except Exception:
                    totp_enabled = False
                    pref_email = False
                    require_every_login = False
                if totp_enabled or pref_email:
                    # Se política exigir a cada login, já redireciona imediatamente
                    next_url = request.GET.get('next', 'home')
                    return redirect(f"{reverse('verify_2fa')}?next={next_url}")
                return redirect(request.GET.get('next', 'home'))
            else:
                if login_attempt:
                    login_attempt.failed_attempts += 1
                    if login_attempt.failed_attempts >= 5:
                        login_attempt.block()
                        blocked_message = f"Usuário bloqueado por excesso de tentativas. Tente novamente após {login_attempt.blocked_until.strftime('%d/%m/%Y %H:%M:%S')}."
                    login_attempt.save()
                error_message = "Usuário ou senha inválidos."
                logger.warning(f"Falha de login para usuário '{username}' do IP {get_client_ip(request)}")
        elif not form.is_valid() and user_obj and login_attempt:
            # Se o usuário existe, mas o formulário não é válido, conta tentativa
            login_attempt.failed_attempts += 1
            if login_attempt.failed_attempts >= 5:
                login_attempt.block()
                blocked_message = f"Usuário bloqueado por excesso de tentativas. Tente novamente após {login_attempt.blocked_until.strftime('%d/%m/%Y %H:%M:%S')}."
            login_attempt.save()
            error_message = "Usuário ou senha inválidos."
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form, 'error_message': error_message, 'blocked_message': blocked_message})

def logout_view(request):
    """View para fazer logout do usuário"""
    logout(request)
    messages.success(request, 'Você saiu da sua conta com sucesso!')
    logger.info(f"Logout realizado para usuário '{request.user.username if request.user.is_authenticated else 'desconhecido'}'")
    return redirect('home')

def home(request):
    # Mostrar alguns pets em destaque na página inicial
    pets_destaque = Pet.objects.filter(status='disponivel')[:6]
    return render(request, 'core/home.html', {'pets_destaque': pets_destaque})

@login_required
def profile_view(request):
    """View para exibir o perfil do usuário"""
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
    
    # Anonimizar dados sensíveis para exibição
    import copy
    user_anon = copy.copy(user)
    interessado_anon = copy.copy(interessado) if interessado else None
    local_anon = copy.copy(local) if local else None

    # Dados sensíveis anonimizados usando máscara
    from .utils import mask_sensitive
    # manter primeiro nome e username reais para identificação visual, anonimizar sobrenome e email parcialmente
    user_anon.last_name = mask_sensitive(user.last_name)
    user_anon.email = mask_sensitive(user.email)
    if interessado_anon:
        interessado_anon.cpf = mask_sensitive(interessado.cpf, preserve_chars='.-')
        interessado_anon.telefone = mask_sensitive(interessado.telefone, preserve_chars='()- +')
        interessado_anon.endereco = mask_sensitive(interessado.endereco, preserve_chars=',. -/')
        interessado_anon.latitude = mask_sensitive(interessado.latitude)
        interessado_anon.longitude = mask_sensitive(interessado.longitude)
    if local_anon:
        local_anon.cnpj = mask_sensitive(local.cnpj, preserve_chars='.-/')
        local_anon.telefone = mask_sensitive(local.telefone, preserve_chars='()- +')
        local_anon.endereco = mask_sensitive(local.endereco, preserve_chars=',. -/')
        local_anon.latitude = mask_sensitive(local.latitude)
        local_anon.longitude = mask_sensitive(local.longitude)

    # Mock para IP, localização e logs
    ip_real = request.META.get('REMOTE_ADDR', '127.0.0.1')
    ip_anon = "***.***.***.***"
    geo_real = f"{interessado.latitude}, {interessado.longitude}" if interessado else "-"
    geo_anon = "***"
    logs_real = "Acesso em 08/10/2025, alteração de senha, login realizado"
    logs_anon = "***"

    # Preferências de 2FA persistidas
    two_factor_pref = 'totp'
    two_factor_require_every_login = True
    two_factor_enabled = False
    try:
        tf = request.user.two_factor_auth
        two_factor_pref = tf.preferred_method
        two_factor_require_every_login = tf.require_every_login
        two_factor_enabled = tf.is_enabled
    except Exception:
        pass

    context = {
        'user': user_anon,
        'user_real': user,
        'interessado': interessado_anon,
        'interessado_real': interessado,
        'local': local_anon,
        'local_real': local,
        'ip_real': ip_real,
        'ip_anon': ip_anon,
        'geo_real': geo_real,
        'geo_anon': geo_anon,
        'logs_real': logs_real,
        'logs_anon': logs_anon,
        'two_factor_preference': two_factor_pref,
        'two_factor_require_every_login': two_factor_require_every_login,
        'two_factor_enabled': two_factor_enabled,
    }
    return render(request, 'core/profile.html', context)


@login_required
def edit_profile_view(request):
    """View para editar o perfil do usuário"""
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
    
    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=user)
        interessado_form = None
        local_form = None
        
        if interessado:
            interessado_form = EditInteressadoForm(request.POST, instance=interessado)
        elif local:
            local_form = EditLocalForm(request.POST, instance=local)
        
        forms_valid = user_form.is_valid()
        
        if interessado_form:
            forms_valid = forms_valid and interessado_form.is_valid()
        elif local_form:
            forms_valid = forms_valid and local_form.is_valid()
        
        if forms_valid:
            user_form.save()
            if interessado_form:
                interessado_form.save()
            elif local_form:
                local_form.save()
            
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('profile')
    else:
        user_form = EditUserForm(instance=user)
        interessado_form = EditInteressadoForm(instance=interessado) if interessado else None
        local_form = EditLocalForm(instance=local) if local else None
    
    context = {
        'user_form': user_form,
        'interessado_form': interessado_form,
        'local_form': local_form,
        'interessado': interessado,
        'local': local,
    }
    
    return render(request, 'core/edit_profile.html', context)


@login_required
def change_password_view(request):
    """View para alterar senha"""
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            request.user.set_password(new_password)
            request.user.save()
            
            # Atualizar sessão para não deslogar o usuário
            update_session_auth_hash(request, request.user)
            
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('profile')
    else:
        form = ChangePasswordForm(user=request.user)
    
    return render(request, 'core/change_password.html', {'form': form})


def pets_list_view(request):
    """View para listar todos os pets disponíveis para adoção"""
    pets = Pet.objects.filter(status='disponivel')
    
    # Filtros
    especie = request.GET.get('especie')
    porte = request.GET.get('porte')
    sexo = request.GET.get('sexo')
    search = request.GET.get('search')
    
    if especie:
        pets = pets.filter(especie=especie)
    if porte:
        pets = pets.filter(porte=porte)
    if sexo:
        pets = pets.filter(sexo=sexo)
    if search:
        pets = pets.filter(
            Q(nome__icontains=search) | 
            Q(raca__icontains=search) | 
            Q(descricao__icontains=search)
        )
    
    # Paginação
    paginator = Paginator(pets, 12)  # 12 pets por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'especie_atual': especie,
        'porte_atual': porte,
        'sexo_atual': sexo,
        'search_atual': search,
        'especies_choices': Pet.ESPECIES_CHOICES,
        'portes_choices': Pet.PORTES_CHOICES,
        'sexos_choices': Pet.SEXOS_CHOICES,
    }
    
    return render(request, 'core/pets_list.html', context)

def pet_detail_view(request, pet_id):
    """View para exibir detalhes de um pet específico"""
    pet = get_object_or_404(Pet, id=pet_id)
    
    # Verificar se o usuário é um interessado em adoção
    interessado = None
    ja_solicitou = False
    
    if request.user.is_authenticated:
        try:
            interessado = InteressadoAdocao.objects.get(usuario=request.user)
            # Verificar se já existe uma solicitação de adoção
            ja_solicitou = SolicitacaoAdocao.objects.filter(
                pet=pet, interessado=interessado
            ).exists()
        except InteressadoAdocao.DoesNotExist:
            pass
    
    context = {
        'pet': pet,
        'interessado': interessado,
        'ja_solicitou': ja_solicitou,
    }
    
    return render(request, 'core/pet_detail.html', context)

@login_required
def solicitar_adocao_view(request, pet_id):
    """View para solicitar adoção de um pet"""
    pet = get_object_or_404(Pet, id=pet_id, status='disponivel')
    
    # Verificar se o usuário é um interessado em adoção
    try:
        interessado = InteressadoAdocao.objects.get(usuario=request.user)
    except InteressadoAdocao.DoesNotExist:
        messages.error(request, 'Apenas interessados em adoção podem solicitar a adoção de pets.')
        return redirect('pet_detail', pet_id=pet_id)
    
    # Verificar se já existe uma solicitação
    if SolicitacaoAdocao.objects.filter(pet=pet, interessado=interessado).exists():
        messages.warning(request, 'Você já solicitou a adoção deste pet.')
        return redirect('pet_detail', pet_id=pet_id)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        experiencia_pets = request.POST.get('experiencia_pets')
        situacao_moradia = request.POST.get('situacao_moradia')
        
        if motivo and experiencia_pets and situacao_moradia:
            SolicitacaoAdocao.objects.create(
                pet=pet,
                interessado=interessado,
                motivo=motivo,
                experiencia_pets=experiencia_pets,
                situacao_moradia=situacao_moradia
            )
            messages.success(request, 'Solicitação de adoção enviada com sucesso!')
            return redirect('pet_detail', pet_id=pet_id)
        else:
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
    
    return render(request, 'core/solicitar_adocao.html', {'pet': pet})

def register_view(request):
    """View principal de registro que permite escolher o tipo de usuário"""
    # Verificar se os termos foram aceitos na sessão
    termos_aceitos = request.session.get('termos_aceitos')
    if not termos_aceitos:
        messages.info(request, 'Primeiro você precisa aceitar nossos termos de uso.')
        return redirect('aceitar_termos')
    
    return render(request, 'core/register.html')

def register_interessado_view(request):
    """View para registro de interessados em adoção"""
    # Verificar se os termos foram aceitos
    termos_aceitos = request.session.get('termos_aceitos')
    if not termos_aceitos:
        messages.warning(request, 'Você precisa aceitar os termos de uso antes de se cadastrar.')
        return redirect('aceitar_termos')
    
    if request.method == 'POST':
        form = InteressadoAdocaoForm(request.POST)
        if form.is_valid():
            # Criar o usuário
            user = form.save()
            
            # Criar o perfil de interessado
            interessado = InteressadoAdocao.objects.create(
                usuario=user,
                cpf=form.cleaned_data['cpf'],
                telefone=form.cleaned_data.get('telefone', ''),
                endereco=form.cleaned_data.get('endereco', '')
            )
            
            # Criar aceitação dos termos
            AceitacaoTermos.objects.create(
                usuario=user,
                termos_aceitos=True,
                lgpd_aceito=True,
                ip_aceitacao=termos_aceitos.get('ip', ''),
                user_agent=termos_aceitos.get('user_agent', ''),
                versao_termos='1.0'
            )
            
            # Limpar termos da sessão
            if 'termos_aceitos' in request.session:
                del request.session['termos_aceitos']
            
            # Fazer login automático
            login(request, user)
            messages.success(request, 'Conta criada com sucesso! Bem-vindo ao Harmony Pets!')
            return redirect('home')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = InteressadoAdocaoForm()
    
    return render(request, 'core/register_interessado.html', {'form': form})

def register_local_view(request):
    """View para registro de locais de adoção"""
    # Verificar se os termos foram aceitos
    termos_aceitos = request.session.get('termos_aceitos')
    if not termos_aceitos:
        messages.warning(request, 'Você precisa aceitar os termos de uso antes de se cadastrar.')
        return redirect('aceitar_termos')
    
    if request.method == 'POST':
        form = LocalAdocaoForm(request.POST)
        if form.is_valid():
            # Criar o usuário
            user = form.save()
            
            # Criar o perfil de local de adoção
            local = LocalAdocao.objects.create(
                usuario=user,
                cnpj=form.cleaned_data['cnpj'],
                nome_fantasia=form.cleaned_data.get('nome_fantasia', ''),
                telefone=form.cleaned_data.get('telefone', ''),
                endereco=form.cleaned_data.get('endereco', '')
            )
            
            # Criar aceitação dos termos
            AceitacaoTermos.objects.create(
                usuario=user,
                termos_aceitos=True,
                lgpd_aceito=True,
                ip_aceitacao=termos_aceitos.get('ip', ''),
                user_agent=termos_aceitos.get('user_agent', ''),
                versao_termos='1.0'
            )
            
            # Limpar termos da sessão
            if 'termos_aceitos' in request.session:
                del request.session['termos_aceitos']
            
            # Fazer login automático
            login(request, user)
            messages.success(request, 'Conta criada com sucesso! Bem-vindo ao Harmony Pets!')
            return redirect('home')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = LocalAdocaoForm()
    
    return render(request, 'core/register_local.html', {'form': form})

@login_required
def pets_proximos(request):
    """View para mostrar pets próximos ao usuário"""
    try:
        interessado = request.user.interessadoadocao
        # Se receber latitude/longitude via POST, salvar no perfil
        if request.method == 'POST' and 'latitude' in request.POST and 'longitude' in request.POST:
            try:
                interessado.latitude = float(request.POST['latitude'])
                interessado.longitude = float(request.POST['longitude'])
                interessado.save()
            except Exception:
                messages.error(request, 'Não foi possível salvar sua localização. Tente novamente.')
                return redirect('profile')

        # Verificar se o interessado tem localização
        if not interessado.latitude or not interessado.longitude:
            messages.warning(request, 'Para encontrar pets próximos, você precisa definir sua localização no perfil.')
            return redirect('profile')

        pets_disponiveis = Pet.objects.filter(status='disponivel')
        pets_com_distancia = []
        for pet in pets_disponiveis:
            # Prioriza localização individual do pet
            lat = pet.latitude if pet.latitude is not None else (pet.local_adocao.latitude if pet.local_adocao else None)
            lng = pet.longitude if pet.longitude is not None else (pet.local_adocao.longitude if pet.local_adocao else None)
            local = pet.local_adocao
            if lat is not None and lng is not None:
                distancia = calcular_distancia(
                    interessado.latitude, interessado.longitude,
                    lat, lng
                )
                pets_com_distancia.append({
                    'pet': pet,
                    'local': local,
                    'distancia': round(distancia, 2)
                })
        pets_com_distancia.sort(key=lambda x: x['distancia'])
        pets_proximos = pets_com_distancia[:20]
        from django.conf import settings
        context = {
            'pets_proximos': pets_proximos,
            'user_lat': interessado.latitude,
            'user_lng': interessado.longitude,
            'total_encontrados': len(pets_proximos),
            'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, 'core/pets_proximos.html', context)
    except InteressadoAdocao.DoesNotExist:
        messages.error(request, 'Apenas interessados em adoção podem usar esta funcionalidade.')
        return redirect('home')

def pets_mapa_api(request):
    """API para retornar dados dos pets para o mapa"""
    pets_data = []
    
    if request.user.is_authenticated and hasattr(request.user, 'interessadoadocao'):
        interessado = request.user.interessadoadocao
        
        if interessado.latitude and interessado.longitude:
            pets_disponiveis = Pet.objects.filter(status='disponivel')
            
            for pet in pets_disponiveis:
                local = pet.local_adocao
                if local.latitude and local.longitude:
                    distancia = calcular_distancia(
                        interessado.latitude, interessado.longitude,
                        local.latitude, local.longitude
                    )
                    
                    pets_data.append({
                        'id': pet.id,
                        'nome': pet.nome,
                        'especie': pet.get_especie_display(),
                        'emoji': pet.emoji,
                        'lat': local.latitude,
                        'lng': local.longitude,
                        'distancia': round(distancia, 2),
                        'local_nome': local.nome_fantasia or local.usuario.username,
                        'url_detalhes': f'/pets/{pet.id}/'
                    })
            
            # Ordenar por distância
            pets_data.sort(key=lambda x: x['distancia'])
            pets_data = pets_data[:20]  # Limitar a 20 pets
    
    return JsonResponse({
        'pets': pets_data,
        'user_location': {
            'lat': interessado.latitude if 'interessado' in locals() else None,
            'lng': interessado.longitude if 'interessado' in locals() else None
        } if request.user.is_authenticated and hasattr(request.user, 'interessadoadocao') else None
    })

# ==================== VIEWS PARA GERENCIAMENTO DE PETS ==================== #

@login_required
def gerenciar_pets(request):
    """View para listar pets do local de adoção"""
    try:
        local = request.user.localadocao
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Apenas organizações podem gerenciar pets.')
        return redirect('home')
    
    # Buscar pets do local com paginação
    pets = Pet.objects.filter(local_adocao=local).order_by('-data_cadastro')
    
    # Estatísticas
    total_pets = pets.count()
    pets_disponiveis = pets.filter(status='disponivel').count()
    pets_adotados = pets.filter(status='adotado').count()
    pets_reservados = pets.filter(status='reservado').count()
    
    # Paginação
    paginator = Paginator(pets, 12)  # 12 pets por página
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
    """View para adicionar novo pet"""
    try:
        local = request.user.localadocao
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Apenas organizações podem adicionar pets.')
        return redirect('home')
    
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.local_adocao = local
            pet.save()
            messages.success(request, f'Pet {pet.nome} cadastrado com sucesso!')
            logger.info(f"Pet criado: id={pet.id} nome='{pet.nome}' por '{request.user.username}'")
            return redirect('gerenciar_pets')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PetForm()
    
    return render(request, 'core/pet_form.html', {
        'form': form,
        'title': 'Adicionar Novo Pet',
        'button_text': 'Cadastrar Pet'
    })

@login_required
def editar_pet(request, pet_id):
    """View para editar pet existente"""
    try:
        local = request.user.localadocao
        pet = get_object_or_404(Pet, id=pet_id, local_adocao=local)
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Apenas organizações podem editar pets.')
        return redirect('home')
    
    if request.method == 'POST':
        form = PetForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, f'Pet {pet.nome} atualizado com sucesso!')
            logger.info(f"Pet atualizado: id={pet.id} nome='{pet.nome}' por '{request.user.username}'")
            return redirect('gerenciar_pets')
        else:
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
    """View para excluir pet"""
    try:
        local = request.user.localadocao
        pet = get_object_or_404(Pet, id=pet_id, local_adocao=local)
    except LocalAdocao.DoesNotExist:
        messages.error(request, 'Apenas organizações podem excluir pets.')
        return redirect('home')
    
    if request.method == 'POST':
        nome_pet = pet.nome
        pet.delete()
        messages.success(request, f'Pet {nome_pet} removido com sucesso.')
        logger.warning(f"Pet excluído: id={pet_id} nome='{nome_pet}' por '{request.user.username}'")
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
    if status_filtro and status_filtro in ['pendente', 'aprovada', 'rejeitada', 'cancelada']:
        solicitacoes = solicitacoes.filter(status=status_filtro)
    
    # Paginação
    paginator = Paginator(solicitacoes, 10)
    page_number = request.GET.get('page')
    solicitacoes_page = paginator.get_page(page_number)
    
    # Estatísticas
    stats = {
        'total': SolicitacaoAdocao.objects.filter(pet__local_adocao=local).count(),
        'pendentes': SolicitacaoAdocao.objects.filter(pet__local_adocao=local, status='pendente').count(),
        'aprovadas': SolicitacaoAdocao.objects.filter(pet__local_adocao=local, status='aprovada').count(),
        'rejeitadas': SolicitacaoAdocao.objects.filter(pet__local_adocao=local, status='rejeitada').count(),
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
    
    return render(request, 'core/verify_2fa.html', {'form': form})


@login_required
def set_2fa_preference(request):
    """Define preferência do método de 2FA (autenticador ou e-mail) e persiste no modelo do usuário."""
    if request.method != 'POST':
        return redirect('profile')
    method = request.POST.get('method')
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


def termos_uso(request):
    """View para exibir os termos de uso"""
    return render(request, 'core/termos_uso.html')


def aceitar_termos(request):
    """View para aceitar os termos de uso e LGPD"""
    if request.method == 'POST':
        termos_uso_aceito = request.POST.get('termos_uso') == 'on'
        lgpd_aceito = request.POST.get('lgpd') == 'on'
        
        if not termos_uso_aceito or not lgpd_aceito:
            messages.error(request, 'Você deve aceitar todos os termos para continuar.')
            return render(request, 'core/aceitar_termos.html')
        
        if request.user.is_authenticated:
            # Usuário logado - atualizar ou criar aceitação
            aceitacao, created = AceitacaoTermos.objects.get_or_create(
                usuario=request.user,
                defaults={
                    'termos_aceitos': True,
                    'lgpd_aceito': True,
                    'ip_aceitacao': get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
                    'versao_termos': '1.0'
                }
            )
            
            if not created:
                # Atualizar aceitação existente
                aceitacao.termos_aceitos = True
                aceitacao.lgpd_aceito = True
                aceitacao.ip_aceitacao = get_client_ip(request)
                aceitacao.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
                aceitacao.data_aceitacao = timezone.now()
                aceitacao.save()
            
            messages.success(request, 'Termos aceitos com sucesso! Agora você pode usar a plataforma.')
            return redirect('home')
        else:
            # Usuário não logado - salvar na sessão e redirecionar para registro
            request.session['termos_aceitos'] = {
                'termos_uso': True,
                'lgpd': True,
                'ip': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
                'timestamp': timezone.now().isoformat()
            }
            messages.success(request, 'Termos aceitos! Agora você pode se cadastrar.')
            return redirect('register')
    
    return render(request, 'core/aceitar_termos.html')


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

    context = {
        'log_path': log_path,
        'lines': lines,
        'q': q,
        'level': level,
        'n': n,
        'error': error,
    }
    return render(request, 'core/admin_logs.html', context)

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