# core/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import InteressadoAdocao, LocalAdocao, Pet, TwoFactorAuth
import re

def validar_cpf(cpf):
    """Valida CPF"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * len(cpf):
        return False
    
    # Calcula primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    if resto < 2:
        digito1 = 0
    else:
        digito1 = 11 - resto
    
    # Calcula segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    if resto < 2:
        digito2 = 0
    else:
        digito2 = 11 - resto
    
    return cpf[9] == str(digito1) and cpf[10] == str(digito2)

def validar_cnpj(cnpj):
    """Valida CNPJ"""
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * len(cnpj):
        return False
    
    # Calcula primeiro dígito verificador
    soma = 0
    peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for i in range(12):
        soma += int(cnpj[i]) * peso[i]
    resto = soma % 11
    if resto < 2:
        digito1 = 0
    else:
        digito1 = 11 - resto
    
    # Calcula segundo dígito verificador
    soma = 0
    peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for i in range(13):
        soma += int(cnpj[i]) * peso[i]
    resto = soma % 11
    if resto < 2:
        digito2 = 0
    else:
        digito2 = 11 - resto
    
    return cnpj[12] == str(digito1) and cnpj[13] == str(digito2)

class InteressadoAdocaoForm(UserCreationForm):
    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        widget=forms.TextInput(attrs={
            'placeholder': '000.000.000-00',
            'class': 'form-control'
        })
    )
    telefone = forms.CharField(
        label='Telefone',
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '(11) 99999-9999',
            'class': 'form-control'
        })
    )
    endereco = forms.CharField(
        label='Endereço',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Rua, número, bairro, cidade, estado'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionando classes CSS aos campos do UserCreationForm
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
        
        # Tornando alguns campos obrigatórios
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        
        # Adicionando placeholders
        self.fields['username'].widget.attrs.update({'placeholder': 'Nome de usuário'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Primeiro nome'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Último nome'})
        self.fields['email'].widget.attrs.update({'placeholder': 'seu@email.com'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Senha'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirme a senha'})

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf and not validar_cpf(cpf):
            raise forms.ValidationError('CPF inválido.')
        
        # Remove formatação para salvar no banco
        cpf_numeros = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica se já existe outro usuário com este CPF
        if InteressadoAdocao.objects.filter(cpf=cpf_numeros).exists():
            raise forms.ValidationError('Já existe um usuário cadastrado com este CPF.')
            
        return cpf_numeros

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Já existe um usuário cadastrado com este e-mail.')
        return email

class LocalAdocaoForm(UserCreationForm):
    cnpj = forms.CharField(
        label='CNPJ',
        max_length=18,
        widget=forms.TextInput(attrs={
            'placeholder': '00.000.000/0000-00',
            'class': 'form-control'
        })
    )
    nome_fantasia = forms.CharField(
        label='Nome Fantasia',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome do estabelecimento',
            'class': 'form-control'
        })
    )
    telefone = forms.CharField(
        label='Telefone',
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '(11) 99999-9999',
            'class': 'form-control'
        })
    )
    endereco = forms.CharField(
        label='Endereço',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Rua, número, bairro, cidade, estado'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionando classes CSS aos campos do UserCreationForm
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
        
        # Tornando alguns campos obrigatórios
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        
        # Adicionando placeholders
        self.fields['username'].widget.attrs.update({'placeholder': 'Nome de usuário'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Primeiro nome'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Último nome'})
        self.fields['email'].widget.attrs.update({'placeholder': 'seu@email.com'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Senha'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirme a senha'})

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj and not validar_cnpj(cnpj):
            raise forms.ValidationError('CNPJ inválido.')
        
        # Remove formatação para salvar no banco
        cnpj_numeros = re.sub(r'[^0-9]', '', cnpj)
        
        # Verifica se já existe outro usuário com este CNPJ
        if LocalAdocao.objects.filter(cnpj=cnpj_numeros).exists():
            raise forms.ValidationError('Já existe um usuário cadastrado com este CNPJ.')
            
        return cnpj_numeros

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Já existe um usuário cadastrado com este e-mail.')
        return email

class PetForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        local_adocao = getattr(self.instance, 'local_adocao', None)
        # Permite: ou localização individual do pet, ou local de adoção válido
        if not (latitude and longitude):
            # Se não informou localização do pet, exige local_adocao válido
            if not local_adocao:
                local_adocao = self.initial.get('local_adocao') or self.data.get('local_adocao')
                if hasattr(local_adocao, 'latitude') and hasattr(local_adocao, 'longitude'):
                    pass
                else:
                    from .models import LocalAdocao
                    try:
                        local_adocao = LocalAdocao.objects.get(pk=local_adocao)
                    except Exception:
                        local_adocao = None
            if local_adocao:
                if not (local_adocao.latitude and local_adocao.longitude):
                    raise forms.ValidationError('O local de adoção selecionado precisa ter latitude e longitude cadastradas.')
            else:
                raise forms.ValidationError('Informe a localização do pet ou selecione um local de adoção válido.')
        # Emoji automático se não informado
        especie = cleaned_data.get('especie')
        emoji = cleaned_data.get('emoji')
        especie_emoji = {
            'cao': '🐕',
            'gato': '🐱',
            'coelho': '🐰',
            'passaro': '🐦',
            'hamster': '🐹',
            'outro': '🐾',
        }
        if not emoji:
            cleaned_data['emoji'] = especie_emoji.get(especie, '🐾')
        return cleaned_data
    """Formulário para cadastro e edição de pets"""
    
    class Meta:
        model = Pet
        fields = [
            'nome', 'especie', 'raca', 'idade', 'sexo', 'porte', 'cor', 'peso',
            'castrado', 'vacinado', 'vermifugado', 'docil', 'brincalhao', 'calmo',
            'descricao', 'cuidados_especiais', 'foto', 'foto_url', 'emoji',
            'latitude', 'longitude'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do pet'}),
            'especie': forms.Select(attrs={'class': 'form-select'}),
            'raca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Raça (opcional)'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Latitude (opcional)'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Longitude (opcional)'}),
            'idade': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '240', 'placeholder': 'Idade em meses'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'porte': forms.Select(attrs={'class': 'form-select'}),
            'cor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cor/coloração'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Peso em kg'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva o pet, seu comportamento, características especiais...'}),
            'cuidados_especiais': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Medicamentos, dieta especial, limitações... (opcional)'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'foto_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL da foto (opcional)'}),
            'emoji': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '�', 'maxlength': '10'}),
        }
        labels = {
            'nome': 'Nome do Pet',
            'especie': 'Espécie',
            'raca': 'Raça',
            'idade': 'Idade (em meses)',
            'sexo': 'Sexo',
            'porte': 'Porte',
            'cor': 'Cor/Coloração',
            'peso': 'Peso (kg)',
            'castrado': 'Castrado',
            'vacinado': 'Vacinado',
            'vermifugado': 'Vermifugado',
            'docil': 'Dócil',
            'brincalhao': 'Brincalhão',
            'calmo': 'Calmo',
            'descricao': 'Descrição',
            'cuidados_especiais': 'Cuidados Especiais',
            'foto': 'Foto do Pet',
            'foto_url': 'URL da Foto',
            'emoji': 'Emoji Representativo',
        }
    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if foto:
            # Validação de tipo de arquivo
            valid_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if hasattr(foto, 'content_type') and foto.content_type not in valid_types:
                raise forms.ValidationError("Apenas arquivos de imagem (JPEG, PNG, GIF, WebP) são permitidos.")
            # Limite de tamanho (opcional, ex: 5MB)
            if foto.size > 5 * 1024 * 1024:
                raise forms.ValidationError("A imagem deve ter no máximo 5MB.")
        return foto

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar checkboxes com classes Bootstrap
        checkbox_fields = ['castrado', 'vacinado', 'vermifugado', 'docil', 'brincalhao', 'calmo']
        for field_name in checkbox_fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-check-input'})
        
        # Tornar alguns campos obrigatórios
        self.fields['nome'].required = True
        self.fields['especie'].required = True
        self.fields['idade'].required = True
        self.fields['sexo'].required = True
        self.fields['porte'].required = True
        self.fields['descricao'].required = True

    def clean_idade(self):
        idade = self.cleaned_data.get('idade')
        if idade is not None and (idade < 0 or idade > 240):
            raise forms.ValidationError('A idade deve estar entre 0 e 240 meses (20 anos).')
        return idade

    def clean_peso(self):
        peso = self.cleaned_data.get('peso')
        if peso is not None and (peso < 0 or peso > 100):
            raise forms.ValidationError('O peso deve estar entre 0 e 100 kg.')
        return peso

class TwoFactorSetupForm(forms.Form):
    """Formulário para configurar 2FA"""
    verification_code = forms.CharField(
        max_length=6,
        min_length=6,
        label='Código de Verificação',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'maxlength': '6',
            'style': 'font-size: 1.5rem; letter-spacing: 0.5rem;'
        }),
        help_text='Digite o código de 6 dígitos do Microsoft Authenticator'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.instance = kwargs.pop('instance', None)  # Aceitar instance para compatibilidade
        super().__init__(*args, **kwargs)
    
    def clean_verification_code(self):
        code = self.cleaned_data.get('verification_code')
        if not code:
            raise forms.ValidationError('Digite o código de verificação.')
        
        if not code.isdigit():
            raise forms.ValidationError('O código deve conter apenas números.')
        
        if len(code) != 6:
            raise forms.ValidationError('O código deve ter exatamente 6 dígitos.')
        
        return code
    
    def save(self):
        """Criar ou atualizar o registro de 2FA"""
        if not self.user:
            raise ValueError('Usuário é obrigatório')
        
        code = self.cleaned_data['verification_code']
        
        # Criar ou obter instância de TwoFactorAuth
        if self.instance:
            two_factor = self.instance
        else:
            two_factor, created = TwoFactorAuth.objects.get_or_create(usuario=self.user)
        
        # Verificar o código
        if not two_factor.verify_token(code):
            raise forms.ValidationError('Código inválido ou expirado.')
        
        return two_factor

class TwoFactorLoginForm(forms.Form):
    """Formulário para login com 2FA"""
    token = forms.CharField(
        max_length=6,
        min_length=6,
        label='Código de Verificação',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'maxlength': '6',
            'style': 'font-size: 1.5rem; letter-spacing: 0.5rem;',
            'autofocus': True
        }),
        help_text='Digite o código de 6 dígitos do Microsoft Authenticator'
    )
    
    use_backup_code = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Usar código de backup'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_token(self):
        token = self.cleaned_data.get('token')
        use_backup = self.cleaned_data.get('use_backup_code', False)
        
        if not token:
            raise forms.ValidationError('Digite o código de verificação.')
        
        if self.user:
            try:
                two_factor = self.user.two_factor_auth
                
                if use_backup:
                    # Validar código de backup
                    if len(token) != 16:
                        raise forms.ValidationError('Código de backup deve ter 16 caracteres.')
                    if not two_factor.verify_backup_code(token.upper()):
                        raise forms.ValidationError('Código de backup inválido ou já utilizado.')
                else:
                    # Validar token TOTP
                    if not token.isdigit() or len(token) != 6:
                        raise forms.ValidationError('O código deve ter exatamente 6 dígitos.')
                    if not two_factor.verify_token(token):
                        raise forms.ValidationError('Código inválido ou expirado.')
                        
            except TwoFactorAuth.DoesNotExist:
                raise forms.ValidationError('2FA não configurado para este usuário.')
        
        return token

class DisableTwoFactorForm(forms.Form):
    """Formulário para desabilitar 2FA"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha atual'
        }),
        label='Senha Atual',
        help_text='Por segurança, confirme sua senha para desabilitar o 2FA'
    )
    
    token = forms.CharField(
        max_length=6,
        min_length=6,
        label='Código de Verificação',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'maxlength': '6',
            'style': 'font-size: 1.5rem; letter-spacing: 0.5rem;'
        }),
        help_text='Digite o código atual do Microsoft Authenticator'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if self.user and not self.user.check_password(password):
            raise forms.ValidationError('Senha incorreta.')
        return password
    
    def clean_token(self):
        token = self.cleaned_data.get('token')
        if not token or not token.isdigit() or len(token) != 6:
            raise forms.ValidationError('Digite um código válido de 6 dígitos.')
        
        if self.user:
            try:
                two_factor = self.user.two_factor_auth
                if not two_factor.verify_token(token):
                    raise forms.ValidationError('Código inválido ou expirado.')
            except TwoFactorAuth.DoesNotExist:
                raise forms.ValidationError('2FA não está configurado.')
        
        return token


# Formulários para edição de perfil
class EditUserForm(forms.ModelForm):
    """Formulário para editar dados básicos do usuário"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu sobrenome'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu e-mail'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verificar se o email já existe para outro usuário
            existing_user = User.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise forms.ValidationError('Este e-mail já está sendo usado por outro usuário.')
        return email


class EditInteressadoForm(forms.ModelForm):
    """Formulário para editar dados do interessado"""
    class Meta:
        model = InteressadoAdocao
        fields = ['cpf', 'telefone', 'endereco']
        labels = {
            'cpf': 'CPF',
            'telefone': 'Telefone',
            'endereco': 'Endereço',
        }
        widgets = {
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00',
                'maxlength': '14'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000',
                'maxlength': '15'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu endereço completo',
                'rows': 3
            }),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            if not validar_cpf(cpf):
                raise forms.ValidationError('CPF inválido.')
            
            # Verificar se o CPF já existe para outro interessado
            existing_interessado = InteressadoAdocao.objects.filter(cpf=cpf).exclude(pk=self.instance.pk).first()
            if existing_interessado:
                raise forms.ValidationError('Este CPF já está cadastrado.')
        return cpf


class EditLocalForm(forms.ModelForm):
    """Formulário para editar dados do local de adoção"""
    class Meta:
        model = LocalAdocao
        fields = ['cnpj', 'nome_fantasia', 'telefone', 'endereco']
        labels = {
            'cnpj': 'CNPJ',
            'nome_fantasia': 'Nome Fantasia',
            'telefone': 'Telefone',
            'endereco': 'Endereço',
        }
        widgets = {
            'cnpj': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00.000.000/0000-00',
                'maxlength': '18'
            }),
            'nome_fantasia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome fantasia da empresa'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000',
                'maxlength': '15'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o endereço completo',
                'rows': 3
            }),
        }

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj:
            if not validar_cnpj(cnpj):
                raise forms.ValidationError('CNPJ inválido.')
            
            # Verificar se o CNPJ já existe para outro local
            existing_local = LocalAdocao.objects.filter(cnpj=cnpj).exclude(pk=self.instance.pk).first()
            if existing_local:
                raise forms.ValidationError('Este CNPJ já está cadastrado.')
        return cnpj


class ChangePasswordForm(forms.Form):
    """Formulário para alterar senha"""
    current_password = forms.CharField(
        label='Senha Atual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha atual'
        })
    )
    new_password1 = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a nova senha'
        }),
        help_text='Sua senha deve conter pelo menos 8 caracteres.'
    )
    new_password2 = forms.CharField(
        label='Confirmar Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a nova senha novamente'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if self.user and not self.user.check_password(current_password):
            raise forms.ValidationError('Senha atual incorreta.')
        return current_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não coincidem.')
        
        if password1 and len(password1) < 8:
            raise forms.ValidationError('A senha deve ter pelo menos 8 caracteres.')
        
        return password2