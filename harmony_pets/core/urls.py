from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    path('register/interessado/', views.register_interessado_view, name='register_interessado'),
    path('register/local/', views.register_local_view, name='register_local'),
    
    # URLs para adoções
    path('pets/', views.pets_list_view, name='pets_list'),
    path('pets/<int:pet_id>/', views.pet_detail_view, name='pet_detail'),
    path('pets/<int:pet_id>/solicitar/', views.solicitar_adocao_view, name='solicitar_adocao'),
    
    # URLs para localização e mapa
    path('pets/proximos/', views.pets_proximos, name='pets_proximos'),
    path('api/pets/mapa/', views.pets_mapa_api, name='pets_mapa_api'),
    
    # URLs para gerenciamento de pets (organizações)
    path('meus-pets/', views.gerenciar_pets, name='gerenciar_pets'),
    path('meus-pets/adicionar/', views.adicionar_pet, name='adicionar_pet'),
    path('meus-pets/<int:pet_id>/editar/', views.editar_pet, name='editar_pet'),
    path('meus-pets/<int:pet_id>/excluir/', views.excluir_pet, name='excluir_pet'),
    path('meus-pets/<int:pet_id>/status/', views.alterar_status_pet, name='alterar_status_pet'),
    
    # URLs para solicitações de adoção
    path('solicitacoes/', views.solicitacoes_adocao, name='solicitacoes_adocao'),
    path('solicitacoes/<int:solicitacao_id>/responder/', views.responder_solicitacao, name='responder_solicitacao'),
    
    # URLs para 2FA
    path('2fa/setup/', views.setup_2fa, name='setup_2fa'),
    path('2fa/verify/', views.verify_2fa, name='verify_2fa'),
    path('2fa/disable/', views.disable_2fa, name='disable_2fa'),
    
    # URLs para edição de perfil
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
    
    # URLs para páginas legais
    path('termos-de-uso/', views.termos_uso, name='termos_uso'),
    path('aceitar-termos/', views.aceitar_termos, name='aceitar_termos'),
]