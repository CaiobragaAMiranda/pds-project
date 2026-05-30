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
- [ ] **Task 3.5:** Descoberta Automática de Repositórios (Top Python Projects).
- [ ] **Task 3.6:** Implementar Fila de Processamento (Celery + Redis) para resiliência.
- [ ] **Task 3.7:** Dashboard de Monitoramento de Captura (Metabase ou similar).

## 🧠 Fase 4: Inteligência de Dados
- [ ] **Task 4.1:** Refatorar `pds-model` para consumir dados do PostgreSQL.
- [ ] **Task 4.2:** Treinamento de modelo sobre base histórica.
