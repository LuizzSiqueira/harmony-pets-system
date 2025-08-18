from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import TwoFactorAuth, AceitacaoTermos


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
                # Verificar se tem 2FA ativo
                two_factor = request.user.two_factor_auth
                if two_factor.is_enabled:
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
                # Usuário não tem 2FA configurado
                pass
        
        response = self.get_response(request)
        return response
