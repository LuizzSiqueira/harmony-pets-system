# Guia de Deploy no Render - Harmony Pets

Este guia explica como fazer o deploy da aplicação Harmony Pets no Render.

## 📋 Pré-requisitos

1. Conta no [Render](https://render.com)
2. Repositório Git com o código (GitHub, GitLab ou Bitbucket)
3. Configurações de e-mail (Gmail ou outro SMTP)
4. Google Maps API Key (opcional, mas recomendado)

## 🚀 Passo a Passo

### 1. Preparação do Repositório

Certifique-se de que os seguintes arquivos estão no repositório:
- ✅ `build.sh` - Script de build
- ✅ `render.yaml` - Configuração do Render
- ✅ `requirements.txt` - Dependências Python (incluindo gunicorn e whitenoise)

### 2. Criar Novo Web Service no Render

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório Git
4. Selecione o repositório `harmony-pets-system`

### 3. Configurar o Web Service

**Configurações Básicas:**
- **Name:** `harmony-pets` (ou nome de sua preferência)
- **Region:** Escolha a região mais próxima (ex: Oregon, US)
- **Branch:** `ajustes-melhorias-projeto` (ou `main`)
- **Root Directory:** (deixe em branco)
- **Runtime:** `Python 3`
- **Build Command:** `./build.sh`
- **Start Command:** `cd harmony_pets && gunicorn harmony_pets.wsgi:application`

### 4. Configurar Variáveis de Ambiente

Adicione as seguintes variáveis de ambiente no Render:

#### 🔐 Configurações Essenciais

```bash
# Django
SECRET_KEY=<gere uma chave secreta forte>
DEBUG=False
ALLOWED_HOSTS=<seu-app>.onrender.com

# Banco de Dados (será fornecido pelo Render PostgreSQL)
USE_DB=web
DB_NAME=<seu-db-name>
DB_USER=<seu-db-user>
DB_PASSWORD=<seu-db-password>
DB_HOST=<seu-db-host>
DB_PORT=5432
DB_SSLMODE=require
```

#### 📧 Configurações de E-mail (Gmail)

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<seu-email>@gmail.com
EMAIL_HOST_PASSWORD=<senha-app-gmail>
DEFAULT_FROM_EMAIL=<seu-email>@gmail.com
```

**⚠️ Importante:** Para Gmail, você precisa criar uma **Senha de App**:
1. Acesse [Conta Google](https://myaccount.google.com)
2. Segurança → Verificação em duas etapas (ative se não estiver)
3. Senhas de app → Criar nova senha
4. Use essa senha no `EMAIL_HOST_PASSWORD`

#### 🗺️ Configurações Opcionais

```bash
GOOGLE_MAPS_API_KEY=<sua-api-key>
ACCOUNT_DELETION_ENABLED=True
POPULATE_PETS_WITH_IMAGES=True
```

### 5. Criar Banco de Dados PostgreSQL

**Opção A: Banco Interno do Render (Recomendado)**

1. No Dashboard do Render, clique em **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name:** `harmony-pets-postgres`
   - **Database:** `harmonypets`
   - **User:** (gerado automaticamente)
   - **Region:** Mesma do Web Service
   - **Plan:** `Starter` (gratuito por 90 dias)

3. Após criar, copie as credenciais:
   - Internal Database URL
   - Hostname
   - Port
   - Database
   - Username
   - Password

4. Cole essas informações nas variáveis de ambiente do Web Service

**Opção B: Banco Externo (Supabase, Neon, etc.)**

Use as credenciais fornecidas pelo serviço escolhido.

### 6. Deploy

1. Clique em **"Create Web Service"**
2. Aguarde o build e deploy (pode levar 5-10 minutos)
3. Acompanhe os logs para verificar se há erros

### 7. Pós-Deploy

#### Criar Superusuário

Acesse o Shell do Render:

```bash
cd harmony_pets
python manage.py createsuperuser
```

Ou através do Dashboard:
1. Vá para o seu Web Service
2. **Shell** → Execute os comandos acima

#### Verificar Aplicação

1. Acesse `https://<seu-app>.onrender.com`
2. Teste o login e registro
3. Acesse o admin: `https://<seu-app>.onrender.com/admin`

## 🔧 Comandos Úteis

### Executar Migrações Manualmente
```bash
cd harmony_pets && python manage.py migrate
```

### Coletar Arquivos Estáticos
```bash
cd harmony_pets && python manage.py collectstatic --no-input
```

### Ver Logs
No Dashboard do Render → Seu Web Service → **Logs**

### Reiniciar Aplicação
No Dashboard do Render → Seu Web Service → **Manual Deploy** → **Clear build cache & deploy**

## ⚠️ Problemas Comuns

### 1. Erro de SECRET_KEY
```
django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty.
```
**Solução:** Adicione `SECRET_KEY` nas variáveis de ambiente.

Gere uma nova chave:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Erro de ALLOWED_HOSTS
```
Invalid HTTP_HOST header: '<seu-app>.onrender.com'
```
**Solução:** Adicione `ALLOWED_HOSTS=<seu-app>.onrender.com` nas variáveis de ambiente.

### 3. Erro de Conexão com Banco de Dados
```
django.db.utils.OperationalError: could not connect to server
```
**Solução:** Verifique se todas as credenciais do banco (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD) estão corretas.

### 4. Arquivos Estáticos Não Carregam
```
GET /static/core/css/style.css 404
```
**Solução:** Execute `python manage.py collectstatic` manualmente ou force um rebuild.

### 5. E-mails Não São Enviados
**Solução:** 
- Verifique se `EMAIL_HOST_USER` e `EMAIL_HOST_PASSWORD` estão corretos
- Use Senha de App do Gmail, não a senha normal
- Confirme que `EMAIL_USE_TLS=True` e `EMAIL_PORT=587`

## 📊 Monitoramento

### Health Checks
O Render faz health checks automáticos. Se a aplicação não responder em 30 segundos, ela será reiniciada.

### Logs
Monitore os logs regularmente:
```bash
# No Dashboard
Web Service → Logs → Live Logs
```

### Métricas
- **CPU Usage**
- **Memory Usage**
- **Response Time**
- **Request Count**

## 💰 Custos

**Plano Gratuito do Render:**
- ✅ Web Service: 750 horas/mês (suficiente para 1 app rodando 24/7)
- ✅ PostgreSQL Starter: Gratuito por 90 dias
- ⚠️ Aplicação entra em "sleep" após 15 minutos de inatividade
- ⚠️ Primeiro acesso após sleep pode levar 30-50 segundos

**Upgrade Recomendado (Produção):**
- **Web Service Starter:** $7/mês
- **PostgreSQL Starter:** $7/mês após período gratuito

## 🔒 Segurança

### Checklist de Segurança
- ✅ `DEBUG=False` em produção
- ✅ `SECRET_KEY` forte e única
- ✅ `ALLOWED_HOSTS` configurado corretamente
- ✅ Senha de App para e-mail (não senha principal)
- ✅ SSL/TLS habilitado (automático no Render)
- ✅ Variáveis sensíveis em Environment Variables (não no código)

## 📚 Recursos Adicionais

- [Documentação do Render](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Whitenoise Documentation](http://whitenoise.evans.io/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs no Dashboard do Render
2. Consulte a documentação oficial
3. Verifique as configurações de variáveis de ambiente
4. Teste localmente com as mesmas configurações de produção

---

**Boa sorte com seu deploy! 🚀**
