from django.contrib import admin
from .models import InteressadoAdocao, LocalAdocao, Pet, SolicitacaoAdocao, TwoFactorAuth, AceitacaoTermos

# Register your models here.

@admin.register(InteressadoAdocao)
class InteressadoAdocaoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'cpf', 'telefone', 'data_criacao']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'cpf']
    list_filter = ['data_criacao']
    readonly_fields = ['data_criacao']

@admin.register(LocalAdocao)
class LocalAdocaoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'cnpj', 'nome_fantasia', 'telefone', 'data_criacao']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'cnpj', 'nome_fantasia']
    list_filter = ['data_criacao']
    readonly_fields = ['data_criacao']

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ['nome', 'especie', 'idade', 'sexo', 'status', 'local_adocao', 'data_cadastro']
    list_filter = ['especie', 'sexo', 'porte', 'status', 'castrado', 'vacinado', 'data_cadastro']
    search_fields = ['nome', 'raca', 'local_adocao__usuario__username', 'local_adocao__nome_fantasia']
    readonly_fields = ['data_cadastro']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'especie', 'raca', 'idade', 'sexo', 'porte', 'cor', 'peso')
        }),
        ('Saúde', {
            'fields': ('castrado', 'vacinado', 'vermifugado')
        }),
        ('Personalidade', {
            'fields': ('docil', 'brincalhao', 'calmo')
        }),
        ('Descrição', {
            'fields': ('descricao', 'cuidados_especiais')
        }),
        ('Relacionamentos', {
            'fields': ('local_adocao', 'adotado_por')
        }),
        ('Status', {
            'fields': ('status', 'data_adocao')
        }),
        ('Mídia', {
            'fields': ('foto_url', 'emoji')
        }),
        ('Datas', {
            'fields': ('data_cadastro',),
            'classes': ('collapse',)
        }),
    )

@admin.register(SolicitacaoAdocao)
class SolicitacaoAdocaoAdmin(admin.ModelAdmin):
    list_display = ['pet', 'interessado', 'status', 'data_solicitacao', 'data_resposta']
    list_filter = ['status', 'data_solicitacao', 'pet__especie']
    search_fields = ['pet__nome', 'interessado__usuario__username', 'interessado__usuario__first_name']
    readonly_fields = ['data_solicitacao']
    
    fieldsets = (
        ('Solicitação', {
            'fields': ('pet', 'interessado', 'motivo', 'experiencia_pets', 'situacao_moradia')
        }),
        ('Status', {
            'fields': ('status', 'resposta_local', 'data_resposta')
        }),
        ('Datas', {
            'fields': ('data_solicitacao',),
            'classes': ('collapse',)
        }),
    )


@admin.register(TwoFactorAuth)
class TwoFactorAuthAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'is_enabled', 'created_at', 'last_used_at']
    list_filter = ['is_enabled', 'created_at']
    search_fields = ['usuario__username', 'usuario__email']
    readonly_fields = ['secret_key', 'created_at', 'last_used_at']


@admin.register(AceitacaoTermos)
class AceitacaoTermosAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'termos_aceitos', 'lgpd_aceito', 'data_aceitacao', 'versao_termos']
    list_filter = ['termos_aceitos', 'lgpd_aceito', 'data_aceitacao', 'versao_termos']
    search_fields = ['usuario__username', 'usuario__email', 'ip_aceitacao']
    readonly_fields = ['data_aceitacao', 'ip_aceitacao', 'user_agent']
    
    fieldsets = (
        ('Usuário', {
            'fields': ('usuario',)
        }),
        ('Termos Aceitos', {
            'fields': ('termos_aceitos', 'lgpd_aceito', 'versao_termos')
        }),
        ('Dados de Auditoria', {
            'fields': ('data_aceitacao', 'ip_aceitacao', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
