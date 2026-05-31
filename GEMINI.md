# Guia de Engenharia - PDS Project

## 🏗️ Padrões de Arquitetura
- **ETL:** Processamento distribuído via Celery/Redis. Workers limitados a 1GB de RAM e 4 processos simultâneos (`MAX_ANALYZE_PROCS`) para análise AST.
- **Persistência:** Proibido o uso de arquivos CSV para armazenamento ou treino de modelos. Toda a comunicação deve ser via PostgreSQL.
- **Engenharia de Features:** Priorizar cálculos no banco de dados (SQL Window Functions) e Materialized Views para garantir consistência em séries temporais.
- **Inteligência Artificial:** Abordagem de Reinforcement Learning (RL) contínuo. Ambientes devem seguir o padrão Gymnasium.

## 🧪 Estratégia de Testes
...
- **IA/RL:** Validação de Precision/Recall de detecção de bugs em ambientes de teste controlados.

## 📝 Ciclo de Documentação
- **PROGRESS.md:** Deve refletir a realidade exata da evolução.
- **bootstrap.md:** Deve ser atualizado sempre que houver mudanças na infraestrutura (DB, dependências, ambiente).


## Observações:

**NUNCA**: acessar diretamente as chaves de API, Permita vazamento de dados, Nem acesse diretórios sem permissão.

**Sempre**: Integração continua, atualização da documentação, francionar as demandas/tasks, Entrega e Implantação Contínuas, utilize principais tecnicas de Devops e MLops, Harness engineering