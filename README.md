# 🐾 Harmony Pets - Sistema de Adoção de Pets

![Django](https://img.shields.io/badge/Django-5.2.5-green)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

Sistema completo de adoção de pets em Django, incluindo autenticação de dois fatores (2FA), localização com Google Maps e conformidade com a LGPD. Testes automatizados garantem regras de negócio (CPF/CNPJ, fluxo de adoção, 2FA, termos).

> Resumo rápido:
> - Servidor: `python manage.py runserver`
> - Testes: `python manage.py test core.tests -v 2`
> - Coverage: `bash scripts/run_tests_coverage.sh`
> - Banco: selecione com `USE_DB=local` (SQLite) ou `USE_DB=web` (Postgres); testes usam SQLite automaticamente.

## ✨ Funcionalidades

### 🔐 Autenticação e Segurança
- **Login/Logout** com validação robusta
- **Autenticação de Dois Fatores (2FA)** com Microsoft Authenticator
- **Termos de uso LGPD-compliant** obrigatórios
- **Edição completa de perfil** e alteração de senha
- **Middleware de segurança** personalizado

### 👥 Gestão de Usuários
- **Cadastro diferenciado**: Interessados em adoção e Locais de adoção
- **Perfis personalizados** com dados específicos
- **Validação de CPF/CNPJ** com verificação de duplicatas
- **Sistema de permissões** baseado em tipo de usuário

### 🐕 Gestão de Pets
- **CRUD completo** para pets disponíveis para adoção
- **Filtros avançados** por espécie, porte, sexo e localização
- **Upload de fotos** e descrições detalhadas
- **Status de adoção** (disponível, em processo, adotado)
- **Emoji inteligente**: preenchimento automático por espécie e sugestão via API Ninjas

### 📍 Localização e Mapa
- **Integração com Google Maps API**
- **Busca por pets próximos** com cálculo de distância
- **Visualização em mapa** dos pets disponíveis
- **Geolocalização automática** do usuário

### 💌 Sistema de Adoção
- **Solicitações de adoção** com processo estruturado
- **Comunicação entre interessados e locais**
- **Histórico de solicitações** e status
- **Notificações e feedback** do processo

## 🏗️ Arquitetura do Projeto

Este projeto segue o padrão **MVT (Model-View-Template)** do Django:

- **Model (Modelo)**: Define a estrutura de dados e regras de negócio
  - Localização: `harmony_pets/core/models.py`
  - Exemplos: `Pet`, `InteressadoAdocao`, `LocalAdocao`, `SolicitacaoAdocao`, `TwoFactorAuth`
  - Responsabilidades: Validações, relacionamentos, métodos de negócio

- **View (Visão)**: Contém a lógica de processamento e controle
  - Localização: `harmony_pets/core/views.py`
  - Exemplos: `login_view`, `listar_pets`, `solicitar_adocao`, `dashboard_admin`
  - Responsabilidades: Receber requisições, processar dados, retornar respostas

- **Template (Modelo de apresentação)**: Define a interface do usuário
  - Localização: `harmony_pets/core/templates/`
  - Exemplos: `base.html`, `pets_list.html`, `login.html`, `perfil.html`
  - Responsabilidades: Renderização HTML, apresentação de dados

### Componentes Adicionais

- **Forms**: Validação e processamento de formulários (`forms.py`)
- **URLs**: Roteamento de requisições (`urls.py`)
- **Middleware**: Interceptadores de requisição/resposta (`middleware.py`)
- **Static Files**: CSS, JavaScript, imagens (`static/`)
- **Template Tags**: Filtros e tags customizadas (`templatetags/`)

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 5.2.5, Python 3.12
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Banco de dados**: PostgreSQL (produção), SQLite (desenvolvimento/testes)
- **Autenticação**: Microsoft Authenticator (TOTP)
- **Mapas**: Google Maps API
- **Emojis**: API Ninjas (opcional)
- **Validações**: CPF/CNPJ, e-mail, telefone
- **Segurança**: Middleware personalizado, LGPD compliance
- **Testes**: Django TestCase, unittest, coverage, pytest

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.12+
- PostgreSQL
- Git

### 1. Clone o repositório
```bash
git clone https://github.com/LuizzSiqueira/harmony-pets-system.git
cd harmony-pets-system
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install django psycopg2-binary pillow qrcode[pil] pyotp
```

### 4. Configure o banco de dados
```bash
# Configure PostgreSQL e ajuste as credenciais em settings.py
cd harmony_pets
python manage.py migrate
```

### 5. Crie um superusuário
```bash
python manage.py createsuperuser
```

### 6. Configure Google Maps (opcional)
- Obtenha uma API key do Google Maps
- Adicione em `core/config_maps.py`

### 7. Variáveis de ambiente (.env) básicas

Crie um arquivo `.env` dentro de `harmony_pets/` (mesmo nível de `manage.py`, não versione) com ao menos:
```
SECRET_KEY=defina-uma-chave-segura
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
# Para Google Maps (opcional)
GOOGLE_MAPS_API_KEY=
# Sugestão de emoji (opcional)
API_NINJAS_KEY=
# Seleção de banco: local=SQLite, web=Postgres
USE_DB=local
# Se for usar Postgres externo (não coloque credenciais em commits)
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432
```
Nunca faça commit de credenciais reais. Para produção, use secret manager ou variáveis injetadas pelo ambiente.

### 8. Execute o servidor
```bash
python manage.py runserver
```

## 📱 Como Usar

### Para Interessados em Adoção:
1. **Cadastre-se** como interessado
2. **Configure 2FA** para maior segurança
3. **Aceite os termos LGPD**
4. **Explore pets** disponíveis
5. **Use o mapa** para encontrar pets próximos
6. **Solicite adoção** dos pets de interesse

### Para Locais de Adoção:
1. **Cadastre-se** como local de adoção
2. **Configure 2FA** e aceite os termos
3. **Adicione pets** para adoção
4. **Gerencie solicitações** recebidas
5. **Atualize status** dos pets
6. **Comunique-se** com interessados

## 📚 Documentação e Scripts

### Documentação (`docs/`)
Todos os guias e documentação técnica estão organizados na pasta `docs/`:
- Guias de configuração (2FA, Google Maps, variáveis de ambiente)
- Lista de implementações e funcionalidades
- Consulte `docs/README.md` para mais detalhes

### Scripts (`scripts/`)
Scripts utilitários e ferramentas de automação estão na pasta `scripts/`:
- Scripts de população de dados
- Scripts de teste e cobertura
- Ferramentas de debug e manutenção
- Consulte `scripts/README.md` para instruções de uso

## 🗂️ Estrutura do Projeto (MVT)

```
harmony-pets-system/
├── harmony_pets/               # Projeto Django principal
│   ├── core/                   # App principal (MVT)
│   │   ├── models.py           # 📊 MODEL: Modelos de dados e regras de negócio
│   │   ├── views.py            # 🎯 VIEW: Lógica de controle e processamento
│   │   ├── forms.py            # 📝 Formulários e validações
│   │   ├── urls.py             # 🔗 Roteamento de URLs
│   │   ├── middleware.py       # 🛡️ Interceptadores de requisição
│   │   ├── templates/          # 🎨 TEMPLATE: Interface do usuário (HTML)
│   │   │   ├── core/           # Templates da aplicação
│   │   │   └── registration/   # Templates de autenticação
│   │   ├── static/             # 📁 Arquivos estáticos (CSS, JS, imagens)
│   │   │   └── core/
│   │   │       ├── css/        # Estilos CSS
│   │   │       ├── js/         # Scripts JavaScript
│   │   │       └── img/        # Imagens
│   │   ├── tests/              # 🧪 Testes automatizados (15 arquivos)
│   │   ├── templatetags/       # 🏷️ Filtros e tags customizadas
│   │   └── management/         # ⚙️ Comandos Django customizados
│   │       └── commands/
│   ├── harmony_pets/           # ⚙️ Configurações do projeto Django
│   │   ├── settings.py         # Configurações principais
│   │   ├── urls.py             # URLs do projeto
│   │   └── wsgi.py             # Interface WSGI
│   ├── manage.py               # 🔧 Gerenciador Django
│   ├── logs/                   # 📋 Logs do sistema
│   ├── htmlcov/                # 📊 Relatório HTML de coverage (gerado)
│   └── coverage.xml            # 📊 Relatório XML de coverage (gerado)
├── scripts/                    # 🛠️ Scripts utilitários
│   ├── populate_pets.py        # Popular banco com dados de teste
│   ├── populate_pets_sp.py     # Popular com dados geográficos SP
│   ├── test_email_debug.py     # Teste de configuração de email
│   └── run_tests_coverage.sh   # Execução de testes com cobertura
├── docs/                       # 📚 Documentação e guias
│   ├── GUIA_2FA.md            # Guia de autenticação 2FA
│   ├── GUIA_GOOGLE_MAPS.md    # Guia de configuração do Maps
│   ├── GUIA_TESTES.md         # Guia completo de testes
│   ├── ENV_README.md          # Documentação de variáveis de ambiente
│   ├── implementacoes.txt     # Lista de implementações
│   └── README.md              # Índice da documentação
├── .venv/                      # 🐍 Ambiente virtual Python
├── README.md                   # 📖 Este arquivo
├── requirements.txt            # 📦 Dependências principais
├── requirements-dev.txt        # 📦 Dependências de desenvolvimento
├── Makefile                    # ⚡ Comandos úteis make
└── .gitignore                  # 🚫 Arquivos ignorados pelo Git
```

### Fluxo MVT no Projeto

1. **Requisição do usuário** → `urls.py` (roteamento)
2. **View processa** → `views.py` (lógica de negócio)
3. **Model consulta/salva** → `models.py` (banco de dados)
4. **View prepara contexto** → Dados para o template
5. **Template renderiza** → `templates/` (HTML final)
6. **Resposta HTTP** → Enviada ao navegador

## 🔒 Segurança e LGPD

- **Termos de uso** em conformidade com a LGPD
- **Coleta de dados** transparente e consentida
- **Direitos do usuário** respeitados (acesso, retificação, exclusão)
- **Autenticação robusta** com 2FA opcional (ativável pelo usuário, middleware exige quando configurado)
- **Validação de dados** rigorosa

## 📋 Modelos de Dados (Model - MVT)

### Principais Models em `core/models.py`

- **User**: Usuários do sistema (Django padrão - `django.contrib.auth`)
  - Base para autenticação e permissões

- **InteressadoAdocao**: Pessoas interessadas em adotar pets
  - Campos: CPF, telefone, endereço, latitude, longitude
  - Relacionamento: OneToOne com User

- **LocalAdocao**: Organizações/locais que oferecem pets para adoção
  - Campos: CNPJ, telefone, endereço, latitude, longitude
  - Relacionamento: OneToOne com User

- **Pet**: Animais disponíveis para adoção
  - Campos: nome, espécie, porte, sexo, idade, descrição, foto, emoji, coordenadas
  - Status: disponível, em processo, adotado
  - Relacionamento: ForeignKey com LocalAdocao

- **SolicitacaoAdocao**: Registro de solicitações de adoção
  - Campos: motivo, status, data_solicitacao
  - Relacionamentos: ForeignKey com Pet e InteressadoAdocao

- **TwoFactorAuth**: Configurações de autenticação 2FA
  - Campos: secret_key, método preferido (authenticator/sms), códigos de backup
  - Relacionamento: OneToOne com User

- **AceitacaoTermos**: Controle de aceitação LGPD
  - Campos: data_aceitacao, ip_address, versao_termos
  - Relacionamento: ForeignKey com User

- **UserLoginAttempt**: Registro de tentativas de login (segurança)
  - Campos: username, ip_address, success, timestamp

- **AuditLog**: Logs de auditoria de ações críticas
  - Campos: user, action, model, timestamp, details

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add: Amazing Feature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**LuizzSiqueira**
- GitHub: [@LuizzSiqueira](https://github.com/LuizzSiqueira)
- Email: luizvalente.siqueira@gmail.com

## 🙏 Agradecimentos

- Projeto desenvolvido como Trabalho Final de Curso
- Inspirado na necessidade de facilitar adoções responsáveis
- Contribuições da comunidade Django e Bootstrap

---

⭐ **Se este projeto foi útil, considere dar uma estrela!**

## 🧪 Testes e Cobertura

Executar todos os testes (usa SQLite automaticamente, não requer Postgres):
```bash
cd harmony_pets
python manage.py test core.tests -v 2
```

Gerar cobertura (HTML + XML):
```bash
bash scripts/run_tests_coverage.sh
```
Saída:
- HTML: `harmony_pets/htmlcov/index.html`
- XML:  `harmony_pets/coverage.xml`

Principais áreas cobertas: modelos (CPF/CNPJ, Pets, 2FA), formulários, views básicas, middleware (termos/2FA). Espaço para ampliar cobertura em views avançadas e templatetags.

## 🛠 Troubleshooting

| Problema | Possível causa | Solução rápida |
|----------|----------------|----------------|
| Erro de conexão Postgres (IPv6 unreachable) | Rede sem rota IPv6 para host Supabase | Usar IPv4 explícito em `DB_HOST` ou VPN; ajustar DNS local. |
| Testes tentando usar Postgres | Execução fora de `manage.py test` ou variável ambiente interferindo | Execute exatamente `python manage.py test core.tests`; verifique se `test` está em `sys.argv`. |
| Cobertura abaixo do esperado | Faltam testes de views/paginação | Criar casos adicionais em `core/tests/test_views_*`. |
| QR Code 2FA não aparece | Falta Pillow ou qrcode | Instalar via `pip install -r requirements.txt` novamente. |

## 🧩 Próximos Passos (Sugestões)

- Adicionar testes para AuditLog (middleware) mascarando payload sensível.
- Criar teste de expiração de sessão 2FA (>4h) para garantir revalidação.
- Testar filtros personalizados em `templatetags/formatters.py`.
- Adicionar `README_EN.md` para internacionalização.
- Criar testes para o endpoint `/api/emoji/sugerir/` (mock da API e fallback local).

## 😊 Emojis Inteligentes

- No formulário de pet, ao selecionar a espécie, o sistema tenta sugerir um emoji via API Ninjas e, se indisponível, usa mapeamento local (🐶, 🐱, 🐰, 🐹, 🐦, 🐾).
- Há um botão "Sugerir" ao lado do campo de emoji que consulta a API com base no nome do pet e/ou espécie.
- Endpoint utilitário público: `GET /api/emoji/sugerir/?termo=dog` → `{ ok: true|false, emoji: "..." }`.

