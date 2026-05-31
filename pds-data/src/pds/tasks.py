from celery import Celery
import os

# Configuração do Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = Celery('pds_tasks', broker=redis_url, backend=redis_url)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_acks_late=True, # Garante que a tarefa só saia da fila após conclusão
    worker_prefetch_multiplier=4 # Aumentado de 1 para 4 para acelerar o processamento
)

# Importações tardias para as tarefas
@app.task(bind=True, max_retries=3)
def analyze_release_task(self, owner, repo_name, tag, risky_files, start_dt):
    from pds.pipeline import analyze_code
    from pds.repository import PDSRepository
    
    repo_db = PDSRepository()
    try:
        project_id = repo_db.get_or_create_project(owner, repo_name)
        release_id = repo_db.get_or_create_release(project_id, tag, start_dt)
        
        if repo_db.is_release_processed(release_id):
            repo_db.update_mining_status(project_id, 'PROCESSING', processed_inc=1, tag=tag)
            return f"SKIP: {repo_name} {tag}"

        data = analyze_code(owner, repo_name, tag, risky_files)
        if data:
            repo_db.save_metrics(release_id, data)
            repo_db.update_mining_status(project_id, 'PROCESSING', processed_inc=1, tag=tag)
            repo_db.refresh_materialized_view()
            return f"SUCCESS: {repo_name} {tag} ({len(data)} metrics)"
        
        repo_db.update_mining_status(project_id, 'PROCESSING', processed_inc=1, tag=tag)
        return f"EMPTY: {repo_name} {tag}"
    except Exception as exc:
        repo_db.update_mining_status(project_id, 'FAILED', error=str(exc))
        raise self.retry(exc=exc, countdown=60)
    finally:
        repo_db.close()
