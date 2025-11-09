from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import TwoFactorAuth, AceitacaoTermos
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
from django.urls import resolve
from .models import AuditLog
from .utils import sanitize_payload


class TermsAcceptanceMiddleware:
    """
    Middleware para verificar se o usuário aceitou os termos de uso e LGPD
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs que não precisam de verificação de termos
        self.excluded_urls = [
            '/admin/',
            reverse('login'),
            reverse('logout'),
            reverse('termos_uso'),
            reverse('aceitar_termos'),
            reverse('register'),
            reverse('register_interessado'),
            reverse('register_local'),
        ]
    
    def __call__(self, request):
        # Se o usuário está autenticado
        if request.user.is_authenticated:
            # Verificar se a URL atual precisa de verificação
            url_needs_check = True
            for excluded_url in self.excluded_urls:
                if request.path.startswith(excluded_url):
                    url_needs_check = False
                    break
            
            if url_needs_check:
                try:
                    # Verificar se o usuário aceitou os termos
                    aceitacao = request.user.aceitacao_termos
                    if not aceitacao.termos_completos_aceitos:
                        return redirect('aceitar_termos')
                except AceitacaoTermos.DoesNotExist:
                    # Usuário não aceitou os termos ainda
                    return redirect('aceitar_termos')
        
        response = self.get_response(request)
        return response


class TwoFactorMiddleware:
    """
    Middleware para verificar se o usuário precisa completar a autenticação 2FA
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs que não precisam de verificação 2FA
        self.excluded_urls = [
            reverse('login'),
            reverse('logout'),
            reverse('verify_2fa'),
            reverse('setup_2fa'),
            reverse('disable_2fa'),
            reverse('register'),
            reverse('register_interessado'),
            reverse('register_local'),
            reverse('termos_uso'),
            reverse('aceitar_termos'),
        ]
    
    def __call__(self, request):
        # Se o usuário está autenticado
        if request.user.is_authenticated:
            try:
                # Verificar se tem 2FA ativo OU preferência persistida por e-mail
                two_factor = request.user.two_factor_auth
                pref_email = (two_factor.preferred_method == 'email')
                requires_2fa = two_factor.is_enabled or pref_email
                if requires_2fa:
                    # Verificar se já foi verificado nesta sessão
                    is_verified = request.session.get('2fa_verified', False)
                    verified_at = request.session.get('2fa_verified_at')
                    
                    # Verificar se a verificação não expirou (4 horas)
                    if verified_at:
                        verified_time = timezone.datetime.fromisoformat(verified_at)
                        if timezone.now() - verified_time > timedelta(hours=4):
                            is_verified = False
                            request.session.pop('2fa_verified', None)
                            request.session.pop('2fa_verified_at', None)
                    
                    # Se não foi verificado e não está em uma URL excluída
                    if not is_verified and request.path not in self.excluded_urls:
                        return redirect(f"{reverse('verify_2fa')}?next={request.path}")
                        
            except TwoFactorAuth.DoesNotExist:
                # Usuário não tem 2FA configurado; sem preferência persistida, não exige 2FA
                pass
        
        response = self.get_response(request)
        return response


class AuditLogMiddleware(MiddlewareMixin):
    """Middleware para registrar ações (auditoria) em banco.

    Registra apenas métodos de escrita (POST, PUT, PATCH, DELETE) para evitar ruído.
    """

    WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    def process_request(self, request: HttpRequest):
        request._auditlog_start = timezone.now()
        return None

    def process_response(self, request: HttpRequest, response):
        try:
            if request.method in self.WRITE_METHODS:
                # Ignora endpoints estáticos
                path = request.path or ''
                if path.startswith('/static/'):
                    return response

                view_name = ''
                try:
                    match = resolve(path)
                    view_name = match.view_name or f"{match.func.__module__}.{getattr(match.func, '__name__', 'view')}"
                except Exception:
                    pass

                user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
                ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or request.META.get('REMOTE_ADDR')
                user_agent = (request.META.get('HTTP_USER_AGENT') or '')[:500]
                params = dict(request.GET) if request.GET else {}
                try:
                    # request.POST pode ser QueryDict; converte para dict simples
                    body = sanitize_payload({k: request.POST.getlist(k)[0] if len(request.POST.getlist(k)) == 1 else request.POST.getlist(k) for k in request.POST.keys()})
                except Exception:
                    body = {}

                duracao_ms = 0
                try:
                    start = getattr(request, '_auditlog_start', None)
                    if start:
                        duracao_ms = int((timezone.now() - start).total_seconds() * 1000)
                except Exception:
                    pass

                AuditLog.objects.create(
                    usuario=user,
                    metodo=request.method,
                    caminho=path[:512],
                    view_name=view_name[:255],
                    status_code=getattr(response, 'status_code', 0),
                    ip=ip,
                    user_agent=user_agent,
                    params=params,
                    body=body,
                    mensagem='',
                    duracao_ms=duracao_ms,
                )
        except Exception:
            # Evita quebrar a requisição se algo falhar na auditoria
            pass
        return response
