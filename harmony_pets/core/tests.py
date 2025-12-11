"""
Wrapper module para reexportar os testes definidos no pacote `core.tests`.

Historicamente o repositório teve duplicação (`tests_pkg`) que gerou
conflito no descobridor de testes do Django. Agora deixamos o pacote canônico
em `core/tests/` e este wrapper reexporta seu conteúdo para compatibilidade
com comandos que importem `core.tests`.

Não coloque testes em um módulo `tests.py` simples — use um pacote `tests/`.
"""

from .tests import *  # noqa: F401,F403
