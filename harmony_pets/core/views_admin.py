from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import AuditLog, User, Pet, InteressadoAdocao, LocalAdocao, SolicitacaoAdocao, TwoFactorAuth

@staff_member_required
def admin_dashboard(request):
    users_total = User.objects.count()
    interessados_total = InteressadoAdocao.objects.count()
    locais_total = LocalAdocao.objects.count()
    pets_total = Pet.objects.count()
    pets_disponiveis = Pet.objects.filter(status='disponivel').count()
    pets_adotados = Pet.objects.filter(status='adotado').count()
    pets_reservados = Pet.objects.filter(status='reservado').count()
    sol_total = SolicitacaoAdocao.objects.count()
    sol_pendentes = SolicitacaoAdocao.objects.filter(status='pendente').count()
    sol_aprovadas = SolicitacaoAdocao.objects.filter(status='entrevista_aprovada').count()
    sol_rejeitadas = SolicitacaoAdocao.objects.filter(status__in=['rejeitada', 'entrevista_rejeitada']).count()
    twofa_total = TwoFactorAuth.objects.count()
    twofa_ativos = TwoFactorAuth.objects.filter(is_enabled=True).count()
    twofa_taxa = round((twofa_ativos / twofa_total * 100) if twofa_total else 0, 2)
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
        'audit_recent': audit_recent,
        'audit_errors_recent': audit_errors_recent,
    }
    return render(request, 'core/admin_dashboard.html', context)

@staff_member_required
def admin_logs(request):
    logs = AuditLog.objects.all().order_by('-criado_em')
    context = {
        'logs': logs,
    }
    return render(request, 'core/admin_logs.html', context)

@staff_member_required
def admin_quality(request):
    qualidade_metric = {}  

    context = {
        'qualidade_metric': qualidade_metric,
    }
    return render(request, 'core/admin_quality.html', context)
