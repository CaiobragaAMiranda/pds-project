import requests
import time
from datetime import datetime
import math
import csv
from operator import itemgetter
import re
import git
import logging
import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Configura carregamento do .env
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, "..", "..", "..", ".env")
load_dotenv(dotenv_path)

from pds.repository import PDSRepository

# --- CONFIGURAÇÃO ---
TARGET_REPOS = [
    {"owner": "scikit-learn", "repo": "scikit-learn"},
    {"owner": "numpy", "repo": "numpy"},
    {"owner": "keras-team", "repo": "keras"}
]

N_WINDOWS = None  # Processar todas as releases
DELTA = 1

# --- FUNÇÃO DE REDE INTELIGENTE (Rate Limit Handler) ---

def make_github_request(url: str, token: str, params: dict = None):
    """
    Faz requisições à API gerenciando o Rate Limit.
    Se o limite acabar, o script dorme até renovar.
    """
    headers = {
        "Accept": "application/vnd.github+json", 
        "Authorization": f"Bearer {token}"
    }
    
    while True:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            # Verifica limites no header
            remaining = int(response.headers.get('X-RateLimit-Remaining', 1))
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 403 or response.status_code == 429:
                # Limite excedido!
                now = time.time()
                sleep_seconds = reset_time - now + 10 # +10s de margem de segurança
                
                if sleep_seconds < 0: sleep_seconds = 60 # Fallback
                
                print(f"\n[!!!] RATE LIMIT ATINGIDO. Pausando por {sleep_seconds/60:.1f} minutos...")
                print(f"      Vai tomar um café. O script volta às {datetime.fromtimestamp(reset_time).strftime('%H:%M:%S')}")
                time.sleep(sleep_seconds)
                continue # Tenta de novo
            
            else:
                print(f"   [Erro API] Status {response.status_code} para {url}")
                return None

        except Exception as e:
            print(f"   [Erro Conexão] {e}. Tentando novamente em 5s...")
            time.sleep(5)

# --- FUNÇÕES CORE ---

def extract_releases(token, owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    releases = []
    
    # Busca até 5 páginas de releases para garantir histórico suficiente
    for page in range(1, 6):
        data = make_github_request(url, token, params={'per_page': 100, 'page': page})
        if not data or not isinstance(data, list): break
        
        for r in data:
            if not r.get('draft') and not r.get('prerelease'):
                releases.append(r)
    
    # Filtra Tags Válidas
    valid = []
    pattern = re.compile(r'^v?(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)')
    for r in releases:
        if pattern.match(r.get("tag_name", "")):
            valid.append({
                "tag_name": r.get("tag_name"),
                "published_at": r.get("published_at")
            })
            
    return sorted(valid, key=itemgetter('published_at'), reverse=True)

def get_timelines(releases, delta=1, limit=None):
    timelines = []
    if not releases: return []
    
    max_idx = len(releases) - delta
    if limit and max_idx > limit: max_idx = limit

    for i in range(max_idx):
        target = releases[i+delta]
        last = releases[i] # Janela inversa cronologica
        
        timelines.append((
            target['tag_name'],
            target['published_at'], # Start (mais antigo, na verdade a API aceita isoformat)
            last['published_at']    # End (mais novo)
        ))
    return timelines

def get_failed_commits(token, owner, repo, since, until):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    commits = make_github_request(url, token, params={'since': since, 'until': until, 'per_page': 100})
    
    failed_shas = []
    if not commits or not isinstance(commits, list): return []
    
    # Limite para não queimar tokens à toa em janelas gigantes
    # Se uma janela tem 100 commits, analisamos os 100.
    for c in commits:
        sha = c.get("sha")
        status_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}/status"
        status = make_github_request(status_url, token)
        
        if status and status.get("state") in ["failure", "error"]:
            failed_shas.append(sha)
            
    return list(set(failed_shas))

def get_files_from_commits(token, owner, repo, shas):
    files = []
    for sha in shas:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
        data = make_github_request(url, token)
        if data:
            for f in data.get('files', []):
                if str(f.get('filename')).endswith('.py'):
                    files.append(f.get('filename'))
    return list(set(files))

def analyze_code(owner, repo_name, tag, risky_files):
    repo_dir = f"./{repo_name}"
    
    # Clone/Setup
    if os.path.isdir(repo_dir):
        repo = git.Repo(repo_dir)
    else:
        print(f"   Clonando {repo_name}...")
        repo = git.Repo.clone_from(f"https://github.com/{owner}/{repo_name}.git", repo_dir)
    
    # Checkout Seguro
    try:
        repo.git.reset('--hard')
        repo.git.clean('-fdx')
        repo.git.checkout(tag, force=True)
    except Exception as e:
        print(f"   [Git Error] {e}")
        return []
    
    # Métricas
    from pds import pymetrix # Import tardio para garantir path
    metrics = list(pymetrix.scan_directory(repo_dir))
    
    # Labeling
    risky_norm = [os.path.normpath(f) for f in risky_files]
    
    labeled_data = []
    for row in metrics:
        # Filtros básicos de limpeza (LOC > 0 e ignorar docs/testes)
        fpath = row['FILE']
        if row['LOC'] == 0: continue
        if any(x in fpath for x in ['/doc/', '/tests/', '/examples/', 'benchmarks']): continue
        
        # Check Label
        label = 0
        fpath_norm = os.path.normpath(fpath)
        for r in risky_norm:
            if fpath_norm.endswith(r):
                label = 1
                break
        
        # Monta linha final
        new_row = {
            'PROJECT': repo_name,
            'FILE': fpath,
            'LOC': row['LOC'], 'COM': row['COM'], 'BLK': row['BLK'],
            'NOF': row['NOF'], 'NOC': row['NOC'], 'APF': row['APF'],
            'AMC': row['AMC'], 'NER': row['NER'], 'NEH': row['NEH'],
            'CYC': row['CYC'], 'MAD': row['MAD'],
            'BUILD_FAIL': label
        }
        labeled_data.append(new_row)
        
    return labeled_data

def start(token=None):
    # Prioriza token passado por argumento, depois variável de ambiente
    token = token or os.getenv("GITHUB_TOKEN")
    
    if not token:
        print("Erro: GITHUB_TOKEN não configurado. Adicione ao arquivo .env ou passe como argumento.")
        sys.exit(1)

    print(f"--- PIPELINE RESILIENTE (N={N_WINDOWS}) ---")
    
    repo_db = PDSRepository()

    for target in TARGET_REPOS:
        owner, repo = target['owner'], target['repo']
        print(f"\n>>> REPO: {repo}")
        
        project_id = repo_db.get_or_create_project(owner, repo)
        
        releases = extract_releases(token, owner, repo)
        timelines = get_timelines(releases, delta=DELTA, limit=N_WINDOWS)
        
        print(f"   {len(timelines)} janelas para analisar.")
        
        for i, (tag, start_dt, end_dt) in enumerate(timelines):
            print(f"   Win [{i+1}/{len(timelines)}] Tag: {tag}")
            
            release_id = repo_db.get_or_create_release(project_id, tag, start_dt)
            
            # CHECKPOINT: Pula se já processado
            if repo_db.is_release_processed(release_id):
                print(f"      > Release já processada. Pulando...")
                continue
            
            fails = get_failed_commits(token, owner, repo, start_dt, end_dt)
            if not fails: 
                print(f"      - Sem falhas de build na janela.")
                continue
            
            risky = get_files_from_commits(token, owner, repo, fails)
            data = analyze_code(owner, repo, tag, risky)
            
            if data:
                repo_db.save_metrics(release_id, data)
                print(f"      + {len(data)} métricas salvas no Banco de Dados.")
            
    repo_db.close()
    print(f"\n>>> CONCLUÍDO! Dados sincronizados com PostgreSQL.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        start(sys.argv[1])
    else:
        start()