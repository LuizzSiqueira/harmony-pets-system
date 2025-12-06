"""
Script para verificar otimizações de performance do Harmony Pets
Execute: python check_performance.py

Este script verifica se as otimizações foram aplicadas corretamente.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'harmony_pets'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'harmony_pets.settings')
django.setup()

from django.conf import settings
from django.core.cache import cache
from django.db import connection

def check_database_config():
    """Verifica configurações do banco de dados"""
    print("\n" + "="*50)
    print("🔍 VERIFICANDO CONFIGURAÇÕES DO BANCO DE DADOS")
    print("="*50)
    
    db_config = settings.DATABASES['default']
    
    # Connection pooling
    conn_max_age = db_config.get('CONN_MAX_AGE', 0)
    print(f"\n✓ Connection Pooling: {'✅ Ativado' if conn_max_age > 0 else '❌ Desativado'} (CONN_MAX_AGE={conn_max_age}s)")
    
    # Health checks
    conn_health = db_config.get('CONN_HEALTH_CHECKS', False)
    print(f"✓ Health Checks: {'✅ Ativado' if conn_health else '❌ Desativado'}")
    
    # Options
    options = db_config.get('OPTIONS', {})
    print(f"✓ Timeout configurado: {'✅ Sim' if 'statement_timeout' in str(options) else '❌ Não'}")
    
    return conn_max_age > 0 and conn_health

def check_cache_config():
    """Verifica configurações de cache"""
    print("\n" + "="*50)
    print("💾 VERIFICANDO CONFIGURAÇÕES DE CACHE")
    print("="*50)
    
    cache_backend = settings.CACHES['default']['BACKEND']
    print(f"\n✓ Backend: {cache_backend}")
    
    # Testar cache
    try:
        cache.set('test_key', 'test_value', 10)
        value = cache.get('test_key')
        cache_works = value == 'test_value'
        print(f"✓ Cache funcionando: {'✅ Sim' if cache_works else '❌ Não'}")
        cache.delete('test_key')
    except Exception as e:
        print(f"❌ Erro ao testar cache: {e}")
        cache_works = False
    
    # Session cache
    session_engine = getattr(settings, 'SESSION_ENGINE', '')
    uses_cache = 'cache' in session_engine
    print(f"✓ Sessões em cache: {'✅ Sim' if uses_cache else '❌ Não'} ({session_engine})")
    
    return cache_works

def check_logging_config():
    """Verifica configurações de logging"""
    print("\n" + "="*50)
    print("📝 VERIFICANDO CONFIGURAÇÕES DE LOGS")
    print("="*50)
    
    logging_config = settings.LOGGING
    handlers = logging_config.get('handlers', {})
    
    if 'app_file' in handlers:
        handler = handlers['app_file']
        max_bytes = handler.get('maxBytes', 0)
        backup_count = handler.get('backupCount', 0)
        level = handler.get('level', 'INFO')
        
        print(f"\n✓ Tamanho máximo: {max_bytes / (1024*1024):.1f}MB")
        print(f"✓ Backups: {backup_count}")
        print(f"✓ Nível: {level}")
        
        optimized = max_bytes <= 1024*1024*3 and backup_count <= 3
        print(f"✓ Logs otimizados: {'✅ Sim' if optimized else '⚠️ Pode melhorar'}")
        return optimized
    
    return False

def check_session_config():
    """Verifica configurações de sessão"""
    print("\n" + "="*50)
    print("🔐 VERIFICANDO CONFIGURAÇÕES DE SESSÃO")
    print("="*50)
    
    save_every = getattr(settings, 'SESSION_SAVE_EVERY_REQUEST', True)
    cookie_age = getattr(settings, 'SESSION_COOKIE_AGE', 1209600)
    
    print(f"\n✓ Salvar a cada request: {'❌ Não (otimizado)' if not save_every else '⚠️ Sim (pode melhorar)'}")
    print(f"✓ Duração do cookie: {cookie_age / 3600:.0f}h")
    
    return not save_every

def check_query_optimization():
    """Verifica se queries estão otimizadas"""
    print("\n" + "="*50)
    print("🔎 VERIFICANDO OTIMIZAÇÃO DE QUERIES")
    print("="*50)
    
    from django.db import reset_queries
    from core.models import Pet, SolicitacaoAdocao
    
    # Resetar contador de queries
    reset_queries()
    
    # Buscar pets (deve usar select_related)
    pets = list(Pet.objects.filter(status='disponivel')[:5].select_related('local_adocao'))
    query_count_pets = len(connection.queries)
    
    print(f"\n✓ Queries para 5 pets: {query_count_pets} {'✅ Otimizado' if query_count_pets <= 2 else '⚠️ Pode melhorar'}")
    
    # Resetar para próximo teste
    reset_queries()
    
    # Buscar solicitações (deve usar select_related)
    solicitacoes = list(SolicitacaoAdocao.objects.all()[:5].select_related('pet', 'interessado'))
    query_count_sol = len(connection.queries)
    
    print(f"✓ Queries para 5 solicitações: {query_count_sol} {'✅ Otimizado' if query_count_sol <= 2 else '⚠️ Pode melhorar'}")
    
    return query_count_pets <= 2 and query_count_sol <= 2

def check_production_settings():
    """Verifica configurações de produção"""
    print("\n" + "="*50)
    print("🚀 VERIFICANDO CONFIGURAÇÕES DE PRODUÇÃO")
    print("="*50)
    
    debug = settings.DEBUG
    print(f"\n✓ DEBUG: {'⚠️ True (desenvolvimento)' if debug else '✅ False (produção)'}")
    
    allowed_hosts = settings.ALLOWED_HOSTS
    print(f"✓ ALLOWED_HOSTS: {'✅ Configurado' if allowed_hosts else '❌ Vazio'}")
    
    secret_key = settings.SECRET_KEY
    print(f"✓ SECRET_KEY: {'✅ Configurado' if secret_key else '❌ Não configurado'}")
    
    # Whitenoise
    staticfiles_storage = getattr(settings, 'STATICFILES_STORAGE', '')
    uses_whitenoise = 'whitenoise' in staticfiles_storage.lower()
    print(f"✓ Whitenoise: {'✅ Ativado' if uses_whitenoise else '❌ Desativado'}")
    
    return not debug and allowed_hosts and uses_whitenoise

def generate_report():
    """Gera relatório completo"""
    print("\n" + "="*50)
    print("📊 RELATÓRIO DE OTIMIZAÇÕES")
    print("="*50)
    
    checks = {
        "Banco de Dados": check_database_config(),
        "Cache": check_cache_config(),
        "Logs": check_logging_config(),
        "Sessões": check_session_config(),
        "Queries": check_query_optimization(),
        "Produção": check_production_settings(),
    }
    
    print("\n" + "="*50)
    print("📋 RESUMO")
    print("="*50 + "\n")
    
    total = len(checks)
    passed = sum(checks.values())
    percentage = (passed / total) * 100
    
    for name, result in checks.items():
        status = "✅ OK" if result else "⚠️ Precisa atenção"
        print(f"{name:20} {status}")
    
    print("\n" + "-"*50)
    print(f"Total: {passed}/{total} ({percentage:.0f}%) otimizações aplicadas")
    print("-"*50)
    
    if percentage >= 80:
        print("\n🎉 Excelente! Aplicação bem otimizada para o Render!")
    elif percentage >= 60:
        print("\n👍 Bom! Algumas melhorias podem ser feitas.")
    else:
        print("\n⚠️ Atenção! Várias otimizações precisam ser aplicadas.")
    
    print("\n💡 Consulte OTIMIZACOES_RENDER.md para mais detalhes.\n")

if __name__ == '__main__':
    try:
        print("\n🔧 HARMONY PETS - VERIFICAÇÃO DE PERFORMANCE\n")
        generate_report()
    except Exception as e:
        print(f"\n❌ Erro ao executar verificação: {e}")
        import traceback
        traceback.print_exc()
