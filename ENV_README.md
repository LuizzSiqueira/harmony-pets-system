Policy: centralizar variáveis de ambiente

Onde manter o arquivo `.env`:
- Coloque um único arquivo `.env` na raiz do projeto: `/home/luizsiqueira/Documents/ProjetoFinalDeCurso/Sistema_de_Adocao/.env`.
- Não mantenha outros arquivos `.env` dentro de `venv/` ou em subpastas — isso evita duplicação/confusão.

Como o venv carrega o .env agora:
- Ao ativar o venv (`source venv/bin/activate`), o script de ativação procura por `../.env` (o `.env` na raiz do projeto) e exporta as variáveis. Se não existir, ele busca `venv/.env`.

Boas práticas:
- Adicione as entradas relevantes ao `.gitignore` (já configurado) para garantir que `.env` não seja versionado.
- Em produção, use um secret manager (Azure Key Vault, AWS Secrets Manager, etc.) em vez do `.env` no filesystem.

Remoção de duplicatas:
- Se existir `venv/.env`, remova-o para evitar duplicatas. O script de ativação prioriza o `.env` na raiz do projeto.
