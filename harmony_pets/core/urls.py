# Namespace para rotas do app core
app_name = 'core'
# Pets adotados pelo usuário
from django.urls import path
from django.contrib.auth import views as auth_views
from django.utils import timezone
from .views_auth import AppPasswordResetView
from .views_home import home
from .views_pets import pets_list_view, pet_detail_view, pets_proximos, pets_mapa_api
from .views_adocao import solicitar_adocao_view
from .views_profile import profile_view, edit_profile_view, change_password_view
from .views_auth import delete_account_view
from .views_admin import admin_dashboard, admin_logs, admin_quality
from .views_auth import login_view, logout_view
from .views_terms import termos_uso, politica_privacidade, contato

from .views_adocao import (
    minhas_solicitacoes_adocao, meus_pets_adotados, solicitacoes_adocao, responder_solicitacao,
    agendar_entrevista, responder_entrevista, agendar_retirada, aceitar_termo, cancelar_solicitacao,
    confirmar_adocao, historico_pet
)
from .views_gerenciamento import gerenciar_pets, adicionar_pet, editar_pet, excluir_pet, alterar_status_pet
from .views_cadastro import register_view, register_interessado_view, register_local_view
from .views_2fa import setup_2fa, verify_2fa, set_2fa_preference, disable_2fa
from .views_legais import aceitar_termos, recusar_termos, revogar_termos
from .views_api import sugerir_emoji

urlpatterns = [
    # API utilitária
    path('api/emoji/sugerir/', sugerir_emoji, name='sugerir_emoji'),
    path('minhas-solicitacoes-adocao/', minhas_solicitacoes_adocao, name='minhas_solicitacoes_adocao'),
    path('meus-pets-adotados/', meus_pets_adotados, name='meus_pets_adotados'),
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('register/', register_view, name='register'),
    path('register/interessado/', register_interessado_view, name='register_interessado'),
    path('register/local/', register_local_view, name='register_local'),
    # URLs para adoções
    path('pets/', pets_list_view, name='pets_list'),
    path('pets/<int:pet_id>/', pet_detail_view, name='pet_detail'),
    path('pets/<int:pet_id>/solicitar/', solicitar_adocao_view, name='solicitar_adocao'),
    # URLs para localização e mapa
    path('pets/proximos/', pets_proximos, name='pets_proximos'),
    path('api/pets/mapa/', pets_mapa_api, name='pets_mapa_api'),
    # URLs para gerenciamento de pets (organizações)
    path('meus-pets/', gerenciar_pets, name='gerenciar_pets'),
    path('meus-pets/adicionar/', adicionar_pet, name='adicionar_pet'),
    path('meus-pets/<int:pet_id>/editar/', editar_pet, name='editar_pet'),
    path('meus-pets/<int:pet_id>/excluir/', excluir_pet, name='excluir_pet'),
    path('meus-pets/<int:pet_id>/status/', alterar_status_pet, name='alterar_status_pet'),
    path('meus-pets/<int:pet_id>/historico/', historico_pet, name='historico_pet'),
    # URLs para solicitações de adoção
    path('solicitacoes/', solicitacoes_adocao, name='solicitacoes_adocao'),
    path('solicitacoes/<int:solicitacao_id>/responder/', responder_solicitacao, name='responder_solicitacao'),
    path('solicitacoes/<int:solicitacao_id>/agendar-entrevista/', agendar_entrevista, name='agendar_entrevista'),
    path('solicitacoes/<int:solicitacao_id>/responder-entrevista/', responder_entrevista, name='responder_entrevista'),
    path('solicitacoes/<int:solicitacao_id>/agendar-retirada/', agendar_retirada, name='agendar_retirada'),
    path('solicitacoes/<int:solicitacao_id>/aceitar-termo/', aceitar_termo, name='aceitar_termo'),
    path('solicitacoes/<int:solicitacao_id>/cancelar/', cancelar_solicitacao, name='cancelar_solicitacao'),
    path('solicitacoes/<int:solicitacao_id>/confirmar-adocao/', confirmar_adocao, name='confirmar_adocao'),
    # URLs para 2FA
    path('2fa/setup/', setup_2fa, name='setup_2fa'),
    path('2fa/verify/', verify_2fa, name='verify_2fa'),
    path('2fa/disable/', disable_2fa, name='disable_2fa'),
    path('2fa/preference/', set_2fa_preference, name='set_2fa_preference'),
    # URLs para edição de perfil
    path('profile/edit/', edit_profile_view, name='edit_profile'),
    path('profile/change-password/', change_password_view, name='change_password'),
    path('profile/delete/', delete_account_view, name='delete_account'),
    # URLs para páginas legais
    path('termos-de-uso/', termos_uso, name='termos_uso'),
    path('politica-de-privacidade/', politica_privacidade, name='politica_privacidade'),
    path('aceitar-termos/', aceitar_termos, name='aceitar_termos'),
    path('recusar-termos/', recusar_termos, name='recusar_termos'),
    path('revogar-termos/', revogar_termos, name='revogar_termos'),
    path('contato/', contato, name='contato'),
    # URLs de redefinição de senha por e-mail (Django auth)
    path('password_reset/', AppPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), name='password_reset_complete'),
    # Logs da aplicação (somente staff)
    path('admin-logs/', admin_logs, name='admin_logs'),
    path('admin-quality/', admin_quality, name='admin_quality'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
]