from django.db import models
from django.contrib.auth.models import User
import pyotp
import qrcode
from io import BytesIO
import base64
from django.utils import timezone
from datetime import timedelta

# Create your models here.

# Controle de tentativas de login e bloqueio
class UserLoginAttempt(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='login_attempt')
    failed_attempts = models.PositiveIntegerField(default=0)
    blocked_until = models.DateTimeField(null=True, blank=True)

    def is_blocked(self):
        if self.blocked_until and timezone.now() < self.blocked_until:
            return True
        return False

    def block(self, minutes=15):
        self.blocked_until = timezone.now() + timedelta(minutes=minutes)
        self.save()

    def reset_attempts(self):
        self.failed_attempts = 0
        self.blocked_until = None
        self.save()

class InteressadoAdocao(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=15, blank=True)
    endereco = models.TextField(blank=True)
    # Campos para localização
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude para localização no mapa")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude para localização no mapa")
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.cpf}"
    
    class Meta:
        verbose_name = "Interessado em Adoção"
        verbose_name_plural = "Interessados em Adoção"

class LocalAdocao(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cnpj = models.CharField(max_length=18, unique=True)
    nome_fantasia = models.CharField(max_length=200, blank=True)
    telefone = models.CharField(max_length=15, blank=True)
    endereco = models.TextField(blank=True)
    # Campos para localização
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude para localização no mapa")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude para localização no mapa")
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.cnpj}"
    
    class Meta:
        verbose_name = "Local de Adoção"
        verbose_name_plural = "Locais de Adoção"

class Pet(models.Model):
    # Localização individual do pet (opcional)
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude do pet (opcional)")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude do pet (opcional)")
    ESPECIES_CHOICES = [
        ('cao', 'Cão'),
        ('gato', 'Gato'),
        ('coelho', 'Coelho'),
        ('passaro', 'Pássaro'),
        ('hamster', 'Hamster'),
        ('outro', 'Outro'),
    ]
    
    PORTES_CHOICES = [
        ('pequeno', 'Pequeno'),
        ('medio', 'Médio'),
        ('grande', 'Grande'),
    ]
    
    SEXOS_CHOICES = [
        ('macho', 'Macho'),
        ('femea', 'Fêmea'),
    ]
    
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('adotado', 'Adotado'),
        ('reservado', 'Reservado'),
    ]
    
    nome = models.CharField(max_length=100)
    especie = models.CharField(max_length=20, choices=ESPECIES_CHOICES)
    raca = models.CharField(max_length=100, blank=True)
    idade = models.PositiveIntegerField(help_text="Idade em meses")
    sexo = models.CharField(max_length=10, choices=SEXOS_CHOICES)
    porte = models.CharField(max_length=10, choices=PORTES_CHOICES)
    cor = models.CharField(max_length=50, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Peso em kg")
    
    # Informações médicas e comportamentais
    castrado = models.BooleanField(default=False)
    vacinado = models.BooleanField(default=False)
    vermifugado = models.BooleanField(default=False)
    docil = models.BooleanField(default=True)
    brincalhao = models.BooleanField(default=False)
    calmo = models.BooleanField(default=False)
    
    # Descrição e cuidados especiais
    descricao = models.TextField(help_text="Descrição detalhada do pet")
    cuidados_especiais = models.TextField(blank=True, help_text="Cuidados médicos ou especiais necessários")
    
    # Relacionamentos
    local_adocao = models.ForeignKey(LocalAdocao, on_delete=models.CASCADE, related_name='pets')
    adotado_por = models.ForeignKey(InteressadoAdocao, on_delete=models.SET_NULL, null=True, blank=True, related_name='pets_adotados')
    
    # Status e datas
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_adocao = models.DateTimeField(null=True, blank=True)
    
    # Foto (upload seguro e/ou URL)
    foto = models.ImageField(upload_to='pets/', blank=True, null=True, help_text="Foto do pet (upload)")
    foto_url = models.URLField(blank=True, help_text="URL da foto do pet (opcional)")
    emoji = models.CharField(max_length=10, default='🐕', help_text="Emoji representativo do pet")
    
    class Meta:
        verbose_name = "Pet"
        verbose_name_plural = "Pets"
        ordering = ['-data_cadastro']
    
    def __str__(self):
        return f"{self.nome} - {self.get_especie_display()}"
    
    def get_idade_display(self):
        if self.idade < 12:
            return f"{self.idade} meses"
        else:
            anos = self.idade // 12
            meses = self.idade % 12
            if meses == 0:
                return f"{anos} ano{'s' if anos > 1 else ''}"
            else:
                return f"{anos} ano{'s' if anos > 1 else ''} e {meses} meses"

class SolicitacaoAdocao(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('cancelada', 'Cancelada'),
    ]
    
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='solicitacoes')
    interessado = models.ForeignKey(InteressadoAdocao, on_delete=models.CASCADE, related_name='solicitacoes')
    
    motivo = models.TextField(help_text="Por que você quer adotar este pet?")
    experiencia_pets = models.TextField(help_text="Conte sobre sua experiência com pets")
    situacao_moradia = models.TextField(help_text="Descreva sua situação de moradia (casa, apartamento, quintal, etc.)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_resposta = models.DateTimeField(null=True, blank=True)
    resposta_local = models.TextField(blank=True, help_text="Resposta do local de adoção")
    
    class Meta:
        verbose_name = "Solicitação de Adoção"
        verbose_name_plural = "Solicitações de Adoção"
        ordering = ['-data_solicitacao']
        unique_together = ['pet', 'interessado']  # Evita múltiplas solicitações para o mesmo pet
    
    def __str__(self):
        return f"{self.interessado.usuario.username} - {self.pet.nome}"

class TwoFactorAuth(models.Model):
    """Modelo para autenticação de 2 fatores"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor_auth')
    secret_key = models.CharField(max_length=32, help_text="Chave secreta para TOTP")
    is_enabled = models.BooleanField(default=False, help_text="Se o 2FA está ativo")
    backup_codes = models.JSONField(default=list, blank=True, help_text="Códigos de backup")
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Autenticação de 2 Fatores"
        verbose_name_plural = "Autenticações de 2 Fatores"
    
    def __str__(self):
        return f"2FA para {self.usuario.username} ({'Ativo' if self.is_enabled else 'Inativo'})"
    
    def save(self, *args, **kwargs):
        if not self.secret_key:
            self.secret_key = pyotp.random_base32()
        super().save(*args, **kwargs)
    
    def get_totp_uri(self):
        """Gera URI para o QR Code"""
        return pyotp.totp.TOTP(self.secret_key).provisioning_uri(
            name=self.usuario.email or self.usuario.username,
            issuer_name="Harmony Pets"
        )
    
    def get_qr_code(self):
        """Gera QR Code em base64"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.get_totp_uri())
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_token(self, token):
        """Verifica se o token está correto"""
        if not token or len(token) != 6:
            return False
        
        try:
            totp = pyotp.TOTP(self.secret_key)
            return totp.verify(token, valid_window=1)  # Permite 30s de tolerância
        except:
            return False
    
    def verify_backup_code(self, code):
        """Verifica e remove código de backup usado"""
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False
    
    def generate_backup_codes(self):
        """Gera novos códigos de backup"""
        import secrets
        self.backup_codes = [secrets.token_hex(8).upper() for _ in range(10)]
        self.save()
        return self.backup_codes

class AceitacaoTermos(models.Model):
    """Modelo para rastrear aceitação dos termos de uso e LGPD"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='aceitacao_termos')
    termos_aceitos = models.BooleanField(default=False, help_text="Se o usuário aceitou os termos de uso")
    lgpd_aceito = models.BooleanField(default=False, help_text="Se o usuário aceitou os termos da LGPD")
    data_aceitacao = models.DateTimeField(auto_now_add=True)
    ip_aceitacao = models.GenericIPAddressField(help_text="IP do usuário no momento da aceitação")
    user_agent = models.TextField(help_text="User Agent do navegador no momento da aceitação")
    versao_termos = models.CharField(max_length=10, default="1.0", help_text="Versão dos termos aceitos")
    
    class Meta:
        verbose_name = "Aceitação de Termos"
        verbose_name_plural = "Aceitações de Termos"
    
    def __str__(self):
        return f"Termos aceitos por {self.usuario.username} em {self.data_aceitacao.strftime('%d/%m/%Y')}"
    
    @property
    def termos_completos_aceitos(self):
        """Verifica se todos os termos necessários foram aceitos"""
        return self.termos_aceitos and self.lgpd_aceito
