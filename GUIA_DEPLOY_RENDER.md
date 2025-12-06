# 🚀 Guia Rápido de Deploy no Render

## Checklist Pré-Deploy

Antes de fazer o deploy, certifique-se de que:

- [ ] As otimizações foram aplicadas (execute `python check_performance.py`)
- [ ] Variáveis de ambiente estão configuradas
- [ ] Banco de dados está configurado (PostgreSQL recomendado)
- [ ] Branch `deploy-render` está atualizada

## 📋 Passo a Passo

### 1. Preparar Repositório

```bash
# Certifique-se de estar na branch correta
git checkout deploy-render

# Commitar as otimizações
git add .
git commit -m "feat: adicionar otimizações de performance para Render"
git push origin deploy-render
```

### 2. Criar Web Service no Render

1. Acesse [https://dashboard.render.com](https://dashboard.render.com)
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: `harmony-pets-system`
   - **Branch**: `deploy-render`
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python harmony_pets/manage.py collectstatic --noinput && python harmony_pets/manage.py migrate
     ```
   - **Start Command**: 
     ```bash
     cd harmony_pets && gunicorn harmony_pets.wsgi:application -c ../gunicorn_config.py
     ```
     Ou simplesmente (se o arquivo de config não funcionar):
     ```bash
     cd harmony_pets && gunicorn harmony_pets.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120
     ```
   - **Plan**: Starter (ou superior)

### 3. Configurar Variáveis de Ambiente

Adicione estas variáveis no Render Dashboard (Environment):

```bash
# Django
SECRET_KEY=seu-secret-key-super-seguro-aqui
DEBUG=False
ALLOWED_HOSTS=.onrender.com

# Banco de Dados (crie um PostgreSQL no Render)
DATABASE_URL=postgresql://user:password@host:5432/database

# PostgreSQL específico (opcional, se não usar DATABASE_URL)
DB_NAME=seu_banco
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=seu_host.render.com
DB_PORT=5432

# Email (Gmail exemplo)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
DEFAULT_FROM_EMAIL=seu-email@gmail.com

# Google Maps (opcional)
GOOGLE_MAPS_API_KEY=sua-chave-api

# Performance
CONN_MAX_AGE=60
LOG_LEVEL=WARNING
PGBOUNCER_PREPARED_STATEMENTS=False

# Features (opcional)
ACCOUNT_DELETION_ENABLED=True
POPULATE_PETS_WITH_IMAGES=False
```

### 4. Criar Banco de Dados PostgreSQL

1. No Render Dashboard: **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `harmony-pets-db`
   - **Plan**: Free (para testes) ou Starter
3. Copie a **Internal Database URL**
4. Cole em `DATABASE_URL` no Web Service

### 5. Deploy

1. Clique em **"Create Web Service"**
2. Aguarde o build (pode levar 5-10 minutos)
3. Acesse os logs para verificar erros

### 6. Pós-Deploy

#### Criar Superusuário

```bash
# No Render Dashboard → Shell
python harmony_pets/manage.py createsuperuser
```

#### Verificar Health

```bash
# Teste a aplicação
curl https://seu-app.onrender.com/

# Deve retornar status 200
```

## ⚠️ Troubleshooting

### App crashando por memória

```bash
# Opção 1: Upgrade para plano com mais RAM
# Opção 2: Reduzir cache
# Em settings.py:
CACHES['default']['OPTIONS']['MAX_ENTRIES'] = 200
```

### Erros de conexão com banco

```bash
# Verificar DATABASE_URL
echo $DATABASE_URL

# Testar conexão
python harmony_pets/manage.py dbshell
```

### Static files não carregam

```bash
# Rodar collectstatic manualmente
python harmony_pets/manage.py collectstatic --noinput

# Verificar STATIC_ROOT e STATIC_URL
```

### Timeout em queries

```bash
# Aumentar timeout (em .env ou Render)
DB_CONNECT_TIMEOUT=15
```

## 📊 Monitoramento

### Logs em Tempo Real

```bash
# No Render Dashboard → Logs
# Ou via CLI:
render logs --tail
```

### Métricas Importantes

- **Memória**: Deve ficar < 400MB
- **CPU**: Média < 40%
- **Tempo de resposta**: < 1s

### Alertas

Configure no Render Dashboard:
- Email quando app reiniciar
- Webhook para Slack/Discord

## 🔄 Atualizações

### Deploy Automático

O Render faz deploy automático ao fazer push na branch:

```bash
git add .
git commit -m "sua mensagem"
git push origin deploy-render
```

### Deploy Manual

No Render Dashboard:
1. Clique em **"Manual Deploy"**
2. Selecione a branch
3. Clique em **"Deploy"**

## 🎯 Otimizações Aplicadas

✅ Connection pooling (60s)  
✅ Cache local em memória  
✅ Queries otimizadas com select_related  
✅ Logs reduzidos (2MB, WARNING)  
✅ Sessões em cache híbrido  
✅ Middleware de audit otimizado  
✅ Timeouts configurados  

## 📚 Recursos

- [Documentação do Render](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Otimizações Detalhadas](./OTIMIZACOES_RENDER.md)

## 🆘 Suporte

Se encontrar problemas:

1. Verifique os logs no Render
2. Execute `python check_performance.py` localmente
3. Consulte `OTIMIZACOES_RENDER.md`
4. Abra uma issue no GitHub

---

**Boa sorte com o deploy! 🚀**
