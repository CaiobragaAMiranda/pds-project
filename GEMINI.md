# Guia de Engenharia - PDS Project

## 🏗️ Padrões de Código
- **Estilo:** Seguir PEP 8.
- **Tipagem:** Utilizar Type Hints em todas as novas funções.
- **Módulos:** Manter a separação estrita entre `pds-data`, `pds-model` e `pds-service`.

## 🧪 Estratégia de Testes
- **Unitários:** Cobertura de lógica de extração e processamento.
- **Segurança:** Uso de `bandit` para verificar vulnerabilidades em scripts de rede.
- **Integração:** Validação do fluxo ETL -> PostgreSQL.

## 📝 Ciclo de Documentação
- **PROGRESS.md:** Deve refletir a realidade exata da evolução.
- **bootstrap.md:** Deve ser atualizado sempre que houver mudanças na infraestrutura (DB, dependências, ambiente).
