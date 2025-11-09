from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from django.http import HttpResponse
import csv
import json
from datetime import timedelta
from .models import InteressadoAdocao, LocalAdocao, Pet, SolicitacaoAdocao, TwoFactorAuth, AceitacaoTermos, UserLoginAttempt, AuditLog
# Admin para tentativas de login
@admin.register(UserLoginAttempt)
class UserLoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'failed_attempts', 'blocked_until', 'is_blocked_now']
    search_fields = ['user__username', 'user__email']
    list_filter = ['blocked_until', 'failed_attempts']
    readonly_fields = ['user']

    actions = ['reset_attempts']

    def is_blocked_now(self, obj):
        return obj.is_blocked()
    is_blocked_now.short_description = 'Bloqueado?' 
    is_blocked_now.boolean = True

    def reset_attempts(self, request, queryset):
        for attempt in queryset:
            attempt.reset_attempts()
        self.message_user(request, "Tentativas e bloqueio resetados com sucesso.")
    reset_attempts.short_description = "Resetar tentativas/bloqueio selecionados"

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


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['criado_em', 'usuario', 'metodo', 'caminho', 'status_code', 'duracao_ms']
    search_fields = ['caminho', 'view_name', 'usuario__username', 'mensagem', 'ip', 'user_agent']
    readonly_fields = ['criado_em']
    date_hierarchy = 'criado_em'
    ordering = ('-criado_em',)
    list_per_page = 50
    list_select_related = ('usuario',)

    class StatusClassFilter(SimpleListFilter):
        title = 'Classe do status'
        parameter_name = 'status_class'

        def lookups(self, request, model_admin):
            return (
                ('2xx', '2xx Sucesso'),
                ('3xx', '3xx Redirecionamento'),
                ('4xx', '4xx Erro do Cliente'),
                ('5xx', '5xx Erro do Servidor'),
            )

        def queryset(self, request, queryset):
            val = self.value()
            if val == '2xx':
                return queryset.filter(status_code__gte=200, status_code__lt=300)
            if val == '3xx':
                return queryset.filter(status_code__gte=300, status_code__lt=400)
            if val == '4xx':
                return queryset.filter(status_code__gte=400, status_code__lt=500)
            if val == '5xx':
                return queryset.filter(status_code__gte=500, status_code__lt=600)
            return queryset

    class PeriodoFilter(SimpleListFilter):
        title = 'Período'
        parameter_name = 'periodo'

        def lookups(self, request, model_admin):
            return (
                ('24h', 'Últimas 24h'),
                ('7d', 'Últimos 7 dias'),
                ('30d', 'Últimos 30 dias'),
            )

        def queryset(self, request, queryset):
            val = self.value()
            now = timezone.now()
            if val == '24h':
                return queryset.filter(criado_em__gte=now - timedelta(hours=24))
            if val == '7d':
                return queryset.filter(criado_em__gte=now - timedelta(days=7))
            if val == '30d':
                return queryset.filter(criado_em__gte=now - timedelta(days=30))
            return queryset

    list_filter = ['metodo', 'status_code', StatusClassFilter, PeriodoFilter, 'criado_em']

    actions = ['exportar_csv']

    def exportar_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="auditlog.csv"'
        writer = csv.writer(response)
        headers = ['criado_em', 'usuario', 'metodo', 'caminho', 'view_name', 'status_code', 'ip', 'user_agent', 'params', 'body', 'mensagem', 'duracao_ms']
        writer.writerow(headers)
        for obj in queryset.iterator():
            writer.writerow([
                timezone.localtime(obj.criado_em).strftime('%Y-%m-%d %H:%M:%S') if obj.criado_em else '',
                obj.usuario.username if obj.usuario else '',
                obj.metodo,
                obj.caminho,
                obj.view_name,
                obj.status_code,
                obj.ip or '',
                (obj.user_agent or '')[:200],
                json.dumps(obj.params, ensure_ascii=False)[:10000] if obj.params is not None else '{}',
                json.dumps(obj.body, ensure_ascii=False)[:10000] if obj.body is not None else '{}',
                (obj.mensagem or '')[:10000],
                obj.duracao_ms,
            ])
        return response
    exportar_csv.short_description = 'Exportar selecionados como CSV'
