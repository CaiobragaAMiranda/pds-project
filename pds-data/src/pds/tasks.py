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
    worker_prefetch_multiplier=1 # Uma tarefa por vez por worker para evitar sobrecarga
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
            return f"SKIP: {repo_name} {tag}"

        data = analyze_code(owner, repo_name, tag, risky_files)
        if data:
            repo_db.save_metrics(release_id, data)
            return f"SUCCESS: {repo_name} {tag} ({len(data)} metrics)"
        
        return f"EMPTY: {repo_name} {tag}"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
    finally:
        repo_db.close()
