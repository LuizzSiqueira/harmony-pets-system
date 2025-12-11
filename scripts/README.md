# Scripts - Harmony Pets

Esta pasta contém scripts utilitários e ferramentas de automação para o projeto Harmony Pets.

## 📂 Localização

```
harmony-pets-system/
└── scripts/
    ├── populate_pets.py         # População principal de dados
    ├── populate_pets_sp.py      # População específica de São Paulo
    ├── test_email_debug.py      # Teste de configuração de email
    └── run_tests_coverage.sh    # Script de cobertura de testes
```

## 🚀 Scripts Disponíveis

### População de Dados

#### `populate_pets.py`
Script principal para popular o banco de dados com dados de teste completos.

**O que cria:**
- 5 locais de adoção em diferentes bairros de São Paulo
- 3 pets por local (total de 15 pets)
- Coordenadas geográficas reais para testes de geolocalização
- Dados realistas (nomes, raças, idades, características)

**Como executar:**
```bash
# Da pasta harmony_pets
cd harmony_pets
python manage.py shell < ../scripts/populate_pets.py

# OU da raiz do projeto
cd harmony-pets-system
python harmony_pets/manage.py shell < scripts/populate_pets.py
```

**Configurações disponíveis:**
- `LIMPAR_BANCO = True/False` - Remove dados existentes antes de popular
- `QUANTIDADE_PETS_POR_LOCAL = 3` - Número de pets por local

**Credenciais criadas:**
- Usuários: `ong_pinheiros`, `ong_moema`, `ong_tatuape`, `ong_mogi`, `ong_sp_centro`
- Senha: `123`

#### `populate_pets_sp.py`
Script especializado para dados de São Paulo com coordenadas precisas.

**Como executar:**
```bash
cd harmony_pets
python manage.py shell < ../scripts/populate_pets_sp.py
```

### Testes e Cobertura

#### `run_tests_coverage.sh`
Executa todos os testes com relatório de cobertura de código.

**Como executar:**
```bash
# Da raiz do projeto
bash scripts/run_tests_coverage.sh

# OU
cd scripts
bash run_tests_coverage.sh
```

**Saída:**
- Relatório HTML: `harmony_pets/htmlcov/index.html`
- Relatório XML: `harmony_pets/coverage.xml`
- Console: Resumo de cobertura

### Utilitários

#### `test_email_debug.py`
Testa a configuração de envio de emails.

**Como executar:**
```bash
python scripts/test_email_debug.py
```

**Pré-requisitos:**
- Configure as variáveis de ambiente de email em `harmony_pets/.env`
- Consulte `docs/ENV_README.md` para detalhes

## 📋 Pré-requisitos

Antes de executar qualquer script:

1. **Ambiente virtual ativado:**
   ```bash
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

2. **Dependências instaladas:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Banco de dados migrado:**
   ```bash
   cd harmony_pets
   python manage.py migrate
   ```

4. **Variáveis de ambiente configuradas:**
   - Copie `.env.example` para `harmony_pets/.env`
   - Configure as variáveis necessárias
   - Consulte `docs/ENV_README.md`

## ⚠️ Avisos Importantes

- **Não use em produção**: Estes scripts criam dados de teste com credenciais simples
- **Backup**: Scripts de população podem limpar dados existentes (se `LIMPAR_BANCO = True`)
- **Teste primeiro**: Execute em ambiente de desenvolvimento antes de usar em staging

## 🔧 Solução de Problemas

### Erro: "No module named 'core'"
- **Causa**: Script executado fora do contexto Django
- **Solução**: Use `python manage.py shell < script.py`

### Erro: "table core_pet doesn't exist"
- **Causa**: Migrações não executadas
- **Solução**: `python manage.py migrate`

### Erro: "UNIQUE constraint failed"
- **Causa**: Dados já existem no banco
- **Solução**: Configure `LIMPAR_BANCO = True` ou limpe manualmente

## 📚 Documentação Relacionada

- `docs/README.md` - Documentação completa
- `docs/ENV_README.md` - Variáveis de ambiente
- `README.md` (raiz) - Visão geral do projeto

## 🤝 Contribuindo

Para adicionar novos scripts:

1. Adicione na pasta `scripts/`
2. Documente neste README
3. Inclua comentários no código
4. Teste em ambiente limpo
