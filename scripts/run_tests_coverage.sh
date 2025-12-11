#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Script de Cobertura de Testes - Harmony Pets
# ============================================================================
#
# DESCRIÇÃO:
#   Executa todos os testes unitários do projeto com relatório de cobertura
#   de código, gerando relatórios em HTML e XML.
#
# LOCALIZAÇÃO: harmony-pets-system/scripts/run_tests_coverage.sh
#
# COMO EXECUTAR:
#   bash scripts/run_tests_coverage.sh
#
# FUNCIONALIDADES:
#   - Ativa automaticamente o ambiente virtual se disponível
#   - Instala dependências de desenvolvimento (requirements-dev.txt)
#   - Executa todos os testes unitários
#   - Gera relatório de cobertura em HTML (htmlcov/index.html)
#   - Gera relatório de cobertura em XML (coverage.xml)
#   - Exibe relatório resumido no console
#
# BIBLIOTECAS DE TESTE UTILIZADAS:
#   - coverage: Medição de cobertura de código
#   - Django TestCase: Framework de testes do Django
#   - unittest: Biblioteca padrão de testes Python
#
# SAÍDA:
#   - Console: Relatório de cobertura com percentuais
#   - HTML: harmony_pets/htmlcov/index.html (navegável)
#   - XML: harmony_pets/coverage.xml (para CI/CD)
#
# ============================================================================

ROOT_DIR="$(dirname "$(dirname "$0")")"
HARMONY_DIR="$ROOT_DIR/harmony_pets"

echo "Entrando em $HARMONY_DIR"
cd "$HARMONY_DIR"

# Ativa venv relativo se existir
if [ -f "../venv/bin/activate" ]; then
  echo "Ativando ../venv/bin/activate"
  # shellcheck source=/dev/null
  source ../venv/bin/activate
fi

echo "Instalando dependências de desenvolvimento (requirements-dev.txt) se existir..."
if [ -f "requirements-dev.txt" ]; then
  python -m pip install --upgrade pip
  python -m pip install -r requirements-dev.txt
else
  echo "Aviso: requirements-dev.txt não encontrado no root do repositório. Pulando instalação."
fi

echo "Assegurando coverage esté instalado..."
python -m pip install coverage >/dev/null 2>&1 || true

echo "Rodando testes com coverage (pacote alvo: core.tests)..."
coverage run --source='harmony_pets,core' manage.py test core.tests

echo "Gerando relatórios..."
coverage xml -o coverage.xml || true
coverage html -d htmlcov || true
coverage report -m

echo "Coverage gerado em htmlcov/ e coverage.xml"
