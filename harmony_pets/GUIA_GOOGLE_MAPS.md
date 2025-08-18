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
   Substitua "SUA_CHAVE_API_GOOGLE_MAPS" nos seguintes arquivos:
   - core/config_maps.py
   - core/templates/core/pets_proximos.html
   - core/utils.py (função geocodificar_endereco)

### 3. INSTALAR BIBLIOTECA REQUESTS
   pip install requests

### 4. ATUALIZAR FORMULÁRIOS PARA INCLUIR LOCALIZAÇÃO
   - Adicionar campo de endereço detalhado
   - Implementar geocodificação automática no backend
   - Validar coordenadas antes de salvar

### 5. POPULAR DADOS DE TESTE
   - Adicionar coordenadas para usuários existentes
   - Criar pets em locais diferentes para testar

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
