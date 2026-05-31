# Plano de Evolução (Tasks)

## 🏁 Fase 1: Fundação & Harness
- [x] **Task 1.1:** Inicializar Documentação (`GEMINI.md`, `PROGRESS.md`, `bootstrap.md`).
- [x] **Task 1.2:** Refatorar `pds-data/src/pds/pymetrix.py` (Isolar lógica de AST para testes).
- [x] **Task 1.3:** Criar suite de testes unitários para métricas.
- [x] **Task 1.4:** Implementar análise de segurança estática. (Auditado: Vulnerabilidade de Pickle identificada em pds-service).
- [x] **Task 1.5:** Criar script de limpeza para remover repositórios clonados e arquivos temporários.
- [x] **Task 1.6:** Blindagem para Repositório Público (Segredos, .gitignore, caminhos relativos).
- [x] **Task 1.7:** Limpeza de arquivos obsoletos (.csv, .ipynb, .log).

## 🗄️ Fase 2: Escala & Persistência (PostgreSQL)
- [x] **Task 2.1:** Configurar PostgreSQL via Docker.
- [x] **Task 2.2:** Desenvolver schema de banco de dados para métricas históricas.
- [x] **Task 2.3:** Implementar ingestão automatizada para o banco (SQLAlchemy + pg8000).

## 🔄 Fase 3: ETL de Todas as Releases
- [x] **Task 3.1:** Automatizar captura total de releases via API GitHub.
- [x] **Task 3.2:** Implementar controle de duplicidade.
- [x] **Task 3.3:** Paralelização da análise de código (Multiprocessing).
- [x] **Task 3.4:** Dockerização do Worker de ETL.
- [x] **Task 3.5:** Descoberta Automática de Repositórios (Top Python Projects).
- [x] **Task 3.6:** Implementar Fila de Processamento (Celery + Redis) para resiliência.
- [x] **Task 3.7:** Dashboard de Monitoramento de Captura (Streamlit + Plotly).
- [x] **Task 3.8:** Engenharia de Features de Série Temporal (Deltas, Z-Scores, Cíclicas) via SQL.
- [x] **Task 3.9:** Suporte a GPU (VRAM) e CUDA via Docker para aceleração de IA.

## 🧠 Fase 4: Inteligência de Dados (Reinforcement Learning)
- [x] **Task 4.1:** Implementar Environment PDS (Wrapper Gymnasium para PostgreSQL).
- [x] **Task 4.2:** Treinamento Inicial e Validação de Métricas de Detecção (Migrado para DB).
- [x] **Task 4.3:** Implementar Loop de Treinamento Contínuo (Online Learning).
- [x] **Task 4.4:** Integração do Agente de RL no `pds-service` para Identificação de Bugs em Tempo Real.
- [x] **Task 4.5:** Implementar manutenção automática de Materialized Views (vw_rl_features).
