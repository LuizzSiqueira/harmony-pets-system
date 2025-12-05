# *** GUIA DE IMPLEMENTAÇÃO - GOOGLE MAPS API ***
# Funcionalidade: Encontrar pets próximos usando localização

## PASSOS PARA IMPLEMENTAÇÃO COMPLETA:

### 1. OBTER CHAVE DA API DO GOOGLE MAPS
   - Acesse: https://console.cloud.google.com/
   - Crie um projeto ou selecione um existente
   - Ative as APIs:
     * Maps JavaScript API
     * Geocoding API
   - Gere uma chave de API
   - Configure restrições de segurança

### 2. CONFIGURAR A CHAVE NO PROJETO
   Crie um arquivo `.env` em `harmony_pets/.env` (mesmo nível do manage.py) e adicione:
   ```
   GOOGLE_MAPS_API_KEY=sua_chave_aqui
   ```
   
   A chave será carregada automaticamente nos arquivos:
   - harmony_pets/core/config_maps.py
   - harmony_pets/core/templates/core/pets_proximos.html
   - harmony_pets/core/utils.py (função geocodificar_endereco)
   
   Consulte `docs/ENV_README.md` para mais detalhes sobre variáveis de ambiente.

### 3. INSTALAR DEPENDÊNCIAS
   ```bash
   pip install -r requirements.txt
   ```
   
   Isso instalará todas as dependências necessárias, incluindo requests para a API do Google Maps.

### 4. ATUALIZAR FORMULÁRIOS PARA INCLUIR LOCALIZAÇÃO
   - Adicionar campo de endereço detalhado
   - Implementar geocodificação automática no backend
   - Validar coordenadas antes de salvar

### 5. POPULAR DADOS DE TESTE
   Use os scripts disponíveis em `scripts/`:
   ```bash
   # Popular com dados de exemplo
   python manage.py shell < scripts/populate_pets.py
   
   # Ou popular com dados específicos de São Paulo
   python manage.py shell < scripts/populate_pets_sp.py
   ```
   
   Consulte `scripts/README.md` para mais opções de população de dados.

## ARQUIVOS IMPLEMENTADOS:

✅ models.py - Campos latitude/longitude adicionados
✅ views.py - Views pets_proximos e pets_mapa_api criadas
✅ urls.py - URLs para funcionalidades de mapa
✅ utils.py - Função calcular_distancia implementada
✅ templates/core/pets_proximos.html - Interface do mapa
✅ templates/core/base.html - Navegação atualizada
✅ templates/core/home.html - Botão pets próximos

## FUNCIONALIDADES IMPLEMENTADAS:

1. **Cálculo de Distância**: Fórmula de Haversine para precisão
2. **API JSON**: Endpoint para dados dos pets no mapa
3. **Interface Responsiva**: Template Bootstrap para visualização
4. **Filtros Inteligentes**: Apenas pets disponíveis na região
5. **Navegação Intuitiva**: Botões contextuais baseados no tipo de usuário

---
**Filtro por Localização via API JSON:**
O endpoint da API JSON aceita parâmetros de latitude, longitude e raio (em km) na query string (ex: `/api/pets_mapa/?lat=-23.5&lng=-46.6&raio=10`). Assim, retorna apenas os pets disponíveis próximos à localização informada, otimizando o uso do mapa e dos filtros inteligentes.

## PRÓXIMOS PASSOS:

1. Configurar chave da API do Google Maps
2. Testar com dados reais
3. Implementar geocodificação automática
4. Adicionar filtros avançados (raio de busca)
5. Otimizar performance com cache

## RASCUNHO DE TESTE RÁPIDO:

Para testar sem API do Google Maps:
1. Adicione coordenadas manualmente no admin
2. Acesse /pets/proximos/ 
3. Veja a lista de pets com distâncias calculadas
4. O mapa mostrará placeholder até configurar a API

## Permissões de geolocalização (importante)

- Navegadores só permitem `navigator.geolocation` em contextos seguros: HTTPS ou `http://localhost`.
- Em produção, ative HTTPS; em desenvolvimento, use `localhost` (não `127.0.0.1`) para que o prompt de permissão apareça.
- Não há headers de bloqueio no projeto (Permissions-Policy/Feature-Policy). Se necessário, confira permissões do navegador e limpe permissões negadas anteriormente.
