# 🔍 Monitoramento e Troubleshooting - Harmony Pets no Render

## 📊 Dashboard de Monitoramento

### Métricas Principais (Render Dashboard)

1. **Memória RAM**
   - ✅ Ideal: 150-300MB
   - ⚠️ Atenção: 300-450MB
   - ❌ Crítico: >450MB
   
2. **CPU**
   - ✅ Ideal: <30%
   - ⚠️ Atenção: 30-60%
   - ❌ Crítico: >60%
   
3. **Tempo de Resposta**
   - ✅ Ideal: <500ms
   - ⚠️ Atenção: 500ms-2s
   - ❌ Crítico: >2s
   
4. **Uptime**
   - ✅ Ideal: >99%
   - ⚠️ Atenção: 95-99%
   - ❌ Crítico: <95%

---

## 🔎 Análise de Logs

### Como Acessar Logs

```bash
# Via Dashboard do Render
1. Acesse seu Web Service
2. Clique em "Logs"
3. Use os filtros para buscar erros

# Via CLI (se instalado)
render logs --tail
render logs --tail -n 100  # Últimas 100 linhas
```

### Padrões de Logs Importantes

#### ✅ Logs Normais (OK)

```
[INFO] Starting gunicorn
[INFO] Booting worker with pid: 123
[INFO] Server is ready to handle requests
```

#### ⚠️ Avisos (Investigar)

```
[WARNING] Connection pool exhausted
[WARNING] Slow query detected (>1s)
[WARNING] Cache miss rate high (>50%)
```

**Ação:**
- Verificar número de conexões simultâneas
- Adicionar índices no banco
- Aumentar cache timeout

#### ❌ Erros Críticos

##### Erro 1: Memória Insuficiente
```
[ERROR] MemoryError
[ERROR] killed (signal 9)
```

**Solução:**
1. Upgrade para plano com mais RAM
2. Reduzir MAX_ENTRIES do cache:
   ```python
   CACHES['default']['OPTIONS']['MAX_ENTRIES'] = 200
   ```
3. Desabilitar features pesadas temporariamente

##### Erro 2: Timeout de Banco
```
[ERROR] psycopg2.OperationalError: timeout
[ERROR] could not connect to server
```

**Solução:**
1. Aumentar timeouts:
   ```python
   connect_timeout=15
   statement_timeout=20000
   ```
2. Verificar status do banco no Render
3. Adicionar índices nas tabelas

##### Erro 3: Too Many Connections
```
[ERROR] psycopg2.OperationalError: FATAL: too many connections
```

**Solução:**
1. Verificar CONN_MAX_AGE (deve ser 60)
2. Reduzir número de workers do Gunicorn:
   ```bash
   # Em Procfile ou Start Command
   gunicorn harmony_pets.wsgi:application --workers 2
   ```
3. Usar connection pooler (PgBouncer)

##### Erro 4: Static Files 404
```
[ERROR] 404 /static/core/css/style.css
```

**Solução:**
1. Rodar collectstatic:
   ```bash
   python manage.py collectstatic --noinput
   ```
2. Verificar STATIC_ROOT e STATIC_URL
3. Confirmar Whitenoise no MIDDLEWARE

---

## 🛠️ Comandos de Diagnóstico

### No Shell do Render

```bash
# Acessar shell
# Dashboard → Shell

# 1. Verificar variáveis de ambiente
env | grep -E "DATABASE_URL|SECRET_KEY|DEBUG"

# 2. Testar conexão com banco
python harmony_pets/manage.py dbshell

# 3. Verificar migrações
python harmony_pets/manage.py showmigrations

# 4. Teste de cache
python harmony_pets/manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 60)
>>> cache.get('test')
'value'

# 5. Verificar queries lentas
python harmony_pets/manage.py shell
>>> from django.db import connection, reset_queries
>>> from core.models import Pet
>>> reset_queries()
>>> list(Pet.objects.filter(status='disponivel')[:10])
>>> len(connection.queries)
# Deve retornar 1-2
```

### Localmente

```bash
# 1. Verificar otimizações
python check_performance.py

# 2. Simular ambiente de produção
export DEBUG=False
export DATABASE_URL=postgresql://...
python harmony_pets/manage.py runserver

# 3. Profile de queries
python harmony_pets/manage.py shell
>>> from django.db import connection
>>> from django.test.utils import override_settings
>>> with override_settings(DEBUG=True):
...     # Suas queries aqui
...     print(len(connection.queries))
```

---

## 📈 Otimizações Adicionais (Se Necessário)

### 1. Migrar para Redis Cache

Se o cache local não for suficiente:

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

No Render:
- Adicionar Redis (Add-on)
- Configurar REDIS_URL

### 2. Adicionar Índices no Banco

```sql
-- Conectar ao banco via Shell
python harmony_pets/manage.py dbshell

-- Criar índices
CREATE INDEX idx_pet_status ON core_pet(status);
CREATE INDEX idx_pet_ativo ON core_pet(ativo);
CREATE INDEX idx_pet_local ON core_pet(local_adocao_id);
CREATE INDEX idx_solicitacao_status ON core_solicitacaoadocao(status);
CREATE INDEX idx_solicitacao_pet ON core_solicitacaoadocao(pet_id);

-- Verificar índices criados
\di core_*
```

### 3. Reduzir Workers do Gunicorn

Se ainda houver problemas de memória:

```bash
# Start Command no Render
cd harmony_pets && gunicorn harmony_pets.wsgi:application --workers 2 --threads 2
```

### 4. Paginação Menor

```python
# views.py
paginator = Paginator(pets, 8)  # Reduzir de 12 para 8
```

### 5. Lazy Loading de Imagens

Nos templates HTML:

```html
<img src="..." loading="lazy" alt="...">
```

---

## 🚨 Alertas e Notificações

### Configurar no Render

1. **Email Alerts**
   - Dashboard → Settings → Notifications
   - Ativar: Deploy failures, Service down

2. **Webhook (Slack/Discord)**
   ```
   Webhook URL: https://hooks.slack.com/...
   Events: Deploy, Restart, Error
   ```

### Script de Health Check

Criar arquivo `health_check.py`:

```python
import requests
import time

URL = "https://seu-app.onrender.com"

while True:
    try:
        response = requests.get(URL, timeout=10)
        if response.status_code == 200:
            print(f"✅ OK - {time.ctime()}")
        else:
            print(f"⚠️ Status {response.status_code} - {time.ctime()}")
    except Exception as e:
        print(f"❌ ERROR: {e} - {time.ctime()}")
    
    time.sleep(300)  # Check a cada 5 minutos
```

---

## 📱 Monitoramento Externo

### Opções Gratuitas

1. **UptimeRobot** (https://uptimerobot.com)
   - Monitora uptime
   - Alertas por email/SMS
   - Status page público

2. **Better Uptime** (https://betteruptime.com)
   - Monitoramento de performance
   - Heartbeat monitoring
   - Incident management

3. **New Relic** (plano free)
   - APM completo
   - Monitoring de queries
   - Error tracking

### Configuração Básica

```python
# Para New Relic
# requirements.txt
newrelic

# Adicionar ao Start Command
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn harmony_pets.wsgi:application
```

---

## 🔧 Checklist de Troubleshooting

Quando algo der errado, siga esta ordem:

- [ ] 1. Verificar logs do Render
- [ ] 2. Verificar status do banco de dados
- [ ] 3. Verificar variáveis de ambiente
- [ ] 4. Testar conexão com banco (dbshell)
- [ ] 5. Verificar uso de memória e CPU
- [ ] 6. Executar `check_performance.py` localmente
- [ ] 7. Verificar queries lentas (connection.queries)
- [ ] 8. Verificar cache funcionando
- [ ] 9. Validar static files
- [ ] 10. Revisar últimas mudanças no código

---

## 📞 Suporte

### Render Support
- Dashboard → Help → Contact Support
- Documentação: https://render.com/docs

### Comunidade
- Forum: https://community.render.com
- Discord: https://discord.gg/render

### GitHub Issues
- Abra uma issue com:
  - Logs do erro
  - Output de `check_performance.py`
  - Configurações de ambiente (sem senhas!)

---

## 📚 Referências

- [Render Monitoring Guide](https://render.com/docs/monitoring)
- [Django Performance Tips](https://docs.djangoproject.com/en/stable/topics/performance/)
- [PostgreSQL Performance](https://www.postgresql.org/docs/current/performance-tips.html)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)

---

**Última atualização**: Dezembro 2025
