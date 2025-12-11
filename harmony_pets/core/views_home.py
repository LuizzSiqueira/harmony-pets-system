from django.shortcuts import render
from .models import Pet, InteressadoAdocao, SolicitacaoAdocao

def home(request):
    pets_destaque = Pet.objects.filter(status='disponivel', ativo=True)[:6]
    context = {'pets_destaque': pets_destaque}
    if request.user.is_authenticated:
        try:
            interessado = InteressadoAdocao.objects.get(usuario=request.user)
            solicitacoes = SolicitacaoAdocao.objects.filter(interessado=interessado).order_by('-data_solicitacao')[:3]
            solicitacoes_concluidas = SolicitacaoAdocao.objects.filter(
                interessado=interessado,
                status='concluida'
            ).select_related('pet')
            pets_adotados = [sol.pet for sol in solicitacoes_concluidas if sol.pet]
            context['interessado'] = interessado
            context['solicitacoes_recentes'] = solicitacoes
            context['pets_adotados'] = pets_adotados
            context['total_solicitacoes'] = SolicitacaoAdocao.objects.filter(interessado=interessado).count()
        except InteressadoAdocao.DoesNotExist:
            pass
    return render(request, 'core/home.html', context)
