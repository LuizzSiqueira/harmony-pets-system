# 🐾 Harmony Pets - Sistema de Adoção de Pets

![Django](https://img.shields.io/badge/Django-5.2.5-green)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

Sistema completo de adoção de pets desenvolvido com Django, incluindo autenticação de dois fatores, localização com Google Maps e conformidade com a LGPD.

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

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 5.2.5, Python 3.12
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Banco de dados**: PostgreSQL
- **Autenticação**: Microsoft Authenticator (TOTP)
- **Mapas**: Google Maps API
- **Validações**: CPF/CNPJ, e-mail, telefone
- **Segurança**: Middleware personalizado, LGPD compliance

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

### 7. Execute o servidor
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

## 🗂️ Estrutura do Projeto

```
harmony-pets-system/
├── harmony_pets/
│   ├── core/                    # App principal
│   │   ├── models.py           # Modelos de dados
│   │   ├── views.py            # Lógica de negócio
│   │   ├── forms.py            # Formulários e validações
│   │   ├── urls.py             # URLs da aplicação
│   │   ├── middleware.py       # Middleware personalizado
│   │   ├── templates/          # Templates HTML
│   │   └── static/             # Arquivos estáticos
│   ├── harmony_pets/           # Configurações do projeto
│   ├── manage.py               # Gerenciador Django
│   └── populate_pets.py        # Script para popular dados
├── venv/                       # Ambiente virtual
├── README.md                   # Este arquivo
└── .gitignore                  # Arquivos ignorados pelo Git
```

## 🔒 Segurança e LGPD

- **Termos de uso** em conformidade com a LGPD
- **Coleta de dados** transparente e consentida
- **Direitos do usuário** respeitados (acesso, retificação, exclusão)
- **Autenticação robusta** com 2FA obrigatório
- **Validação de dados** rigorosa

## 📋 Modelos de Dados

- **User**: Usuários do sistema (Django padrão)
- **InteressadoAdocao**: Pessoas interessadas em adotar
- **LocalAdocao**: Organizações/locais que oferecem pets
- **Pet**: Animais disponíveis para adoção
- **SolicitacaoAdocao**: Solicitações de adoção
- **TwoFactorAuth**: Configurações de 2FA
- **AceitacaoTermos**: Controle de aceitação LGPD

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
