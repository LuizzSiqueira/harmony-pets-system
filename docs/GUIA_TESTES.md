# Guia de Testes - Harmony Pets

## 📋 Visão Geral

O projeto Harmony Pets possui uma suíte completa de testes unitários que garantem a qualidade e confiabilidade do código. Os testes cobrem modelos, views, formulários, middleware e utilitários.

## 🧪 Bibliotecas de Teste Utilizadas

### Bibliotecas Principais

#### 1. **Django TestCase** (Padrão)
- **Descrição**: Framework de testes integrado ao Django
- **Uso**: Base para todos os testes unitários
- **Recursos**:
  - Criação automática de banco de dados de teste
  - Transações automáticas (rollback após cada teste)
  - Client para simular requisições HTTP
  - Fixtures e factories para dados de teste

#### 2. **unittest** (Biblioteca Padrão Python)
- **Descrição**: Framework de testes unitários do Python
- **Uso**: Base do Django TestCase
- **Recursos**:
  - Assertions (assertEqual, assertTrue, assertRaises, etc.)
  - Setup e teardown de testes
  - Organização em TestCase e TestSuite

#### 3. **coverage** (Medição de Cobertura)
- **Versão**: Instalada via requirements-dev.txt
- **Descrição**: Mede a cobertura de código pelos testes
- **Uso**: Gera relatórios HTML, XML e console
- **Comando**: `coverage run --source='.' manage.py test`

### Bibliotecas de Desenvolvimento (Opcionais)

Disponíveis em `requirements-dev.txt`:

#### 4. **pytest** + **pytest-django**
- **Descrição**: Framework de testes alternativo mais moderno
- **Recursos**:
  - Sintaxe mais simples que unittest
  - Fixtures poderosas e reutilizáveis
  - Melhor saída de erros
  - Plugins extensíveis

#### 5. **pytest-cov**
- **Descrição**: Plugin de cobertura para pytest
- **Uso**: `pytest --cov=core --cov-report=html`

#### 6. **factory-boy**
- **Descrição**: Biblioteca para criação de dados de teste
- **Uso**: Gera objetos de modelo com dados realistas
- **Vantagem**: Mais flexível que fixtures Django

## 📁 Estrutura de Testes

```
harmony_pets/core/tests/
├── __init__.py
├── test_models_business_rules.py      # Testes de regras de negócio (CPF/CNPJ)
├── test_twofactor_model.py            # Testes de autenticação 2FA
├── test_forms_validation.py           # Testes de validação de formulários
├── test_views_basic.py                # Testes de views básicas (login, home)
├── test_views_pets.py                 # Testes de views de pets
├── test_middleware.py                 # Testes de middleware customizado
├── test_utils_anonymize_and_geo.py    # Testes de utilitários (anonimização, geo)
├── test_utils_mask.py                 # Testes de máscaras (CPF/CNPJ)
├── test_admin_access.py               # Testes de acesso admin
├── test_admin_dashboard.py            # Testes de dashboard admin
├── test_admin_logs_filter.py          # Testes de filtros de logs
├── test_admin_quality_panel.py        # Testes de painel de qualidade
├── test_account_deletion_policy.py    # Testes de política de exclusão
├── test_profile_remocao_termos.py     # Testes de remoção de termos
├── test_recusar_termos.py             # Testes de recusa de termos
└── test_revogar_termos.py             # Testes de revogação de termos
```

## 🚀 Como Executar os Testes

### Método 1: Todos os Testes (Recomendado)

```bash
cd harmony_pets
python manage.py test core.tests -v 2
```

### Método 2: Com Cobertura de Código

```bash
bash scripts/run_tests_coverage.sh
```

**Saída:**
- Console: Relatório resumido
- HTML: `harmony_pets/htmlcov/index.html`
- XML: `harmony_pets/coverage.xml`

### Método 3: Testes Específicos

```bash
# Testar apenas um arquivo
python manage.py test core.tests.test_models_business_rules

# Testar uma classe específica
python manage.py test core.tests.test_models_business_rules.PetModelTestCase

# Testar um método específico
python manage.py test core.tests.test_models_business_rules.PetModelTestCase.test_pet_creation
```

### Método 4: Usando pytest (Opcional)

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Executar testes
pytest

# Com cobertura
pytest --cov=core --cov-report=html --cov-report=term
```

## 📊 Cobertura de Código Atual

### Áreas Testadas

✅ **Modelos (models.py)**
- Validação de CPF/CNPJ únicos
- Criação de pets com dados válidos
- Regras de negócio (status, disponibilidade)
- Relacionamentos entre modelos
- Configurações de 2FA

✅ **Formulários (forms.py)**
- Validação de campos obrigatórios
- Validação de CPF/CNPJ
- Máscaras e formatação
- Mensagens de erro customizadas

✅ **Views (views.py)**
- Requisições GET/POST
- Autenticação e permissões
- Redirecionamentos
- Contexto de templates
- Filtros e paginação

✅ **Middleware (middleware.py)**
- Verificação de termos LGPD
- Verificação de 2FA
- Redirecionamentos automáticos
- Exclusões de URLs

✅ **Utilitários (utils.py)**
- Anonimização de dados LGPD
- Cálculo de distância (Haversine)
- Máscaras de CPF/CNPJ
- Geocodificação

### Áreas para Expandir

⚠️ **Templates**
- Testes de renderização
- Validação de HTML
- JavaScript (se aplicável)

⚠️ **APIs Externas**
- Mocks para Google Maps API
- Mocks para API Ninjas (emojis)

⚠️ **Integrações**
- Testes de email
- Upload de arquivos
- Processamento de imagens

## 🔍 Tipos de Testes Implementados

### 1. Testes Unitários
Testam unidades individuais de código isoladamente.

**Exemplo:**
```python
def test_cpf_validation(self):
    """Testa validação de CPF único"""
    interessado = InteressadoAdocao.objects.create(
        usuario=self.user,
        cpf='12345678901'
    )
    self.assertEqual(interessado.cpf, '12345678901')
```

### 2. Testes de Integração
Testam interação entre componentes.

**Exemplo:**
```python
def test_solicitar_adocao_flow(self):
    """Testa fluxo completo de solicitação de adoção"""
    self.client.login(username='interessado', password='senha')
    response = self.client.post('/pets/1/solicitar/', data={
        'motivo': 'Quero adotar',
        # ... outros campos
    })
    self.assertEqual(response.status_code, 302)
    self.assertEqual(SolicitacaoAdocao.objects.count(), 1)
```

### 3. Testes de Validação
Testam regras de validação de dados.

**Exemplo:**
```python
def test_cnpj_invalido(self):
    """Testa rejeição de CNPJ inválido"""
    form = LocalAdocaoForm(data={'cnpj': '00000000000000'})
    self.assertFalse(form.is_valid())
    self.assertIn('cnpj', form.errors)
```

### 4. Testes de Permissões
Testam controle de acesso.

**Exemplo:**
```python
def test_admin_access_required(self):
    """Testa que apenas admins acessam painel"""
    self.client.login(username='usuario', password='senha')
    response = self.client.get('/admin/dashboard/')
    self.assertEqual(response.status_code, 403)
```

## 🛠️ Boas Práticas Implementadas

### 1. Nomenclatura Clara
```python
# ✅ Bom
def test_pet_creation_with_valid_data(self):
    pass

# ❌ Ruim
def test1(self):
    pass
```

### 2. Arrange-Act-Assert (AAA)
```python
def test_exemplo(self):
    # Arrange: Preparar dados
    user = User.objects.create_user('test', 'test@test.com', 'senha')
    
    # Act: Executar ação
    response = self.client.login(username='test', password='senha')
    
    # Assert: Verificar resultado
    self.assertTrue(response)
```

### 3. Isolamento de Testes
- Cada teste é independente
- Rollback automático de transações
- Sem efeitos colaterais entre testes

### 4. Dados de Teste Realistas
```python
def setUp(self):
    self.user = User.objects.create_user(
        username='joao_silva',
        email='joao@example.com',
        first_name='João',
        last_name='Silva'
    )
```

## 📈 Métricas de Qualidade

### Cobertura de Código
- **Meta**: > 80%
- **Atual**: Verificar com `bash scripts/run_tests_coverage.sh`
- **Visualizar**: Abrir `harmony_pets/htmlcov/index.html`

### Tempo de Execução
- **Todos os testes**: ~10-30 segundos
- **Objetivo**: Manter < 1 minuto

### Quantidade de Testes
- **Total**: 50+ testes
- **Por arquivo**: Média de 5-10 testes

## 🐛 Debugging de Testes

### Ver Saída Detalhada
```bash
python manage.py test core.tests -v 2
```

### Testar com pdb (Python Debugger)
```python
import pdb; pdb.set_trace()  # Adicionar no teste
```

### Ver Queries SQL
```python
from django.test.utils import override_settings

@override_settings(DEBUG=True)
def test_com_queries(self):
    from django.db import connection
    # ... código do teste
    print(connection.queries)
```

## 📚 Recursos Adicionais

### Documentação Oficial
- [Django Testing](https://docs.djangoproject.com/en/5.2/topics/testing/)
- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [Coverage.py](https://coverage.readthedocs.io/)
- [pytest](https://docs.pytest.org/)

### Comandos Úteis

```bash
# Executar testes em paralelo (mais rápido)
python manage.py test --parallel

# Manter banco de dados entre execuções (mais rápido)
python manage.py test --keepdb

# Executar apenas testes que falharam anteriormente
python manage.py test --failfast

# Ver warnings
python manage.py test --warning=all
```

## 🔄 Integração Contínua (CI/CD)

### GitHub Actions (Sugestão)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install coverage
      - name: Run tests
        run: |
          cd harmony_pets
          coverage run manage.py test core.tests
          coverage report
```

## 🎯 Próximos Passos

1. **Aumentar cobertura para 90%+**
   - Adicionar testes para templates
   - Testar edge cases

2. **Adicionar testes de performance**
   - Medir tempo de resposta
   - Testar com grandes volumes de dados

3. **Implementar testes E2E**
   - Usar Selenium para testes de interface
   - Testar fluxos completos de usuário

4. **Adicionar testes de segurança**
   - SQL Injection
   - XSS
   - CSRF

## 🤝 Contribuindo com Testes

Ao adicionar novas funcionalidades, sempre inclua testes:

1. Crie arquivo `test_nome_funcionalidade.py` em `core/tests/`
2. Herde de `django.test.TestCase`
3. Use nomenclatura descritiva
4. Siga padrão AAA (Arrange-Act-Assert)
5. Verifique cobertura antes do commit

**Exemplo de novo arquivo de teste:**
```python
from django.test import TestCase
from core.models import MinhaNovaModel

class MinhaNovaModelTestCase(TestCase):
    def setUp(self):
        # Preparar dados
        pass
    
    def test_criacao_basica(self):
        # Testar criação
        pass
    
    def test_validacao_campo(self):
        # Testar validação
        pass
```

---

**Mantido por**: Equipe Harmony Pets  
**Última atualização**: Dezembro 2025
