Política: centralizar variáveis de ambiente

Onde manter o arquivo `.env` (atual):
- Utilize um único arquivo `.env` em `harmony_pets/.env` (mesmo nível de `manage.py`).
- Esse caminho é o que o Django carrega via `dotenv` nas settings: `load_dotenv(os.path.join(BASE_DIR, '.env'))`, em que `BASE_DIR` aponta para a pasta `harmony_pets/`.

Por que não usar `.env` na raiz do repo?
- O projeto foi configurado para ler especificamente `harmony_pets/.env`. Manter apenas esse arquivo evita ambiguidade.

Como aplicar as variáveis de ambiente:
- Ao rodar via `manage.py`, o Django carrega automaticamente `harmony_pets/.env`.
- Opcionalmente, você pode exportar variáveis no shell antes de rodar comandos (ex.: `USE_DB=local`).

Boas práticas:
- Garanta que `.env` esteja no `.gitignore` (já configurado) para não versionar segredos.
- Em produção, prefira um secret manager (Azure Key Vault, AWS Secrets Manager, etc.) ou variáveis de ambiente do host.

Campos úteis no `.env`:
```
SECRET_KEY=defina-uma-chave-segura
DEBUG=True

# E-mail (para reset de senha e 2FA por e-mail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

# Google Maps (opcional)
GOOGLE_MAPS_API_KEY=

# Banco (quando usar Postgres)
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432

# Emoji API (API Ninjas)
API_NINJAS_KEY=

# Seleção de banco ("local" = SQLite, "web" = Postgres)
USE_DB=local
```
