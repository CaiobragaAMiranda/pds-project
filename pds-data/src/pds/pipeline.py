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
from pds.tasks import analyze_release_task

# --- CONFIGURAÇÃO ---
MIN_STARS = 5000 

def make_github_request(url: str, token: str, params: dict = None):
    headers = {
        "Accept": "application/vnd.github+json", 
        "Authorization": f"Bearer {token}"
    }
    while True:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10) # Reduzido de 15 para 10
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
                sleep_time = max(0, reset_time - int(time.time())) + 2 # Reduzido buffer de espera
                print(f"   [Rate Limit] Aguardando {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                return None
        except Exception as e:
            time.sleep(5) # Reduzido tempo de retentativa
            return None

def discover_repositories(token, limit=200): # Aumentado de 120 para 200
    url = "https://api.github.com/search/repositories"
    params = {
        "q": f"language:python stars:>{MIN_STARS}",
        "sort": "stars",
        "order": "desc",
        "per_page": 100 # Max per page
    }
    # Faremos duas páginas para chegar em 200
    repos = []
    for page in [1, 2]:
        params["page"] = page
        data = make_github_request(url, token, params=params)
        if data and "items" in data:
            repos.extend([{"owner": item["owner"]["login"], "repo": item["name"]} for item in data["items"]])
    return repos

def extract_releases(token, owner, repo_name):
    url = f"https://api.github.com/repos/{owner}/{repo_name}/releases"
    return make_github_request(url, token)

def get_timelines(releases, delta=1, limit=None):
    if not releases: return []
    sorted_rel = sorted(releases, key=lambda x: x['published_at'], reverse=True)
    if limit: sorted_rel = sorted_rel[:limit+1]
    
    timelines = []
    for i in range(len(sorted_rel) - 1):
        tag = sorted_rel[i]['tag_name']
        end_dt = sorted_rel[i]['published_at']
        start_dt = sorted_rel[i+1]['published_at']
        timelines.append((tag, start_dt, end_dt))
    return timelines

def get_failed_commits(token, owner, repo_name, start_date, end_date):
    url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
    params = {"since": start_date, "until": end_date, "per_page": 100}
    commits = make_github_request(url, token, params=params)
    if not commits: return []
    
    failed_shas = []
    for c in commits:
        sha = c['sha']
        check_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits/{sha}/status"
        status = make_github_request(check_url, token)
        if status and status.get("state") in ["failure", "error"]:
            failed_shas.append(sha)
    return list(set(failed_shas))

def get_files_from_commits(token, owner, repo_name, commit_shas):
    files_info = []
    for sha in commit_shas:
        url = f"https://api.github.com/repos/{owner}/{repo_name}/commits/{sha}"
        data = make_github_request(url, token)
        if data:
            c_date = data.get('commit', {}).get('committer', {}).get('date')
            for f in data.get('files', []):
                fname = f.get('filename')
                if fname and fname.endswith('.py'):
                    files_info.append({'file': fname, 'hash': sha, 'date': c_date})
    return files_info

def analyze_code(owner, repo_name, tag, risky_files):
    repo_dir = f"./{repo_name}"
    if not os.path.isdir(repo_dir):
        git.Repo.clone_from(f"https://github.com/{owner}/{repo_name}.git", repo_dir)
    repo = git.Repo(repo_dir)
    try:
        repo.git.reset('--hard')
        repo.git.clean('-fdx')
        repo.git.checkout(tag, force=True)
    except:
        return []
    from pds import pymetrix
    metrics = pymetrix.scan_directory_parallel(repo_dir)
    fail_map = {os.path.normpath(f['file']): f for f in risky_files}
    labeled_data = []
    EXCLUDE_PATTERNS = ['/doc/', '/tests/', '/test/', '/examples/', '/benchmarks/', '__init__.py', 'setup.py', 'conftest.py', 'tox.ini']
    for row in metrics:
        fpath = row['FILE']
        if row['LOC'] < 5 or any(p in fpath.replace('\\', '/') for p in EXCLUDE_PATTERNS): continue
        label, c_hash, c_date = 0, None, None
        fpath_norm = os.path.normpath(fpath)
        for fail_path, info in fail_map.items():
            if fpath_norm.endswith(fail_path):
                label, c_hash, c_date = 1, info['hash'], info['date']
                break
        labeled_data.append({
            'PROJECT': repo_name, 'FILE': fpath, 'LOC': row['LOC'], 'COM': row['COM'], 'BLK': row['BLK'],
            'NOF': row['NOF'], 'NOC': row['NOC'], 'APF': row['APF'], 'AMC': row['AMC'], 'NER': row['NER'],
            'NEH': row['NEH'], 'CYC': row['CYC'], 'MAD': row['MAD'], 'BUILD_FAIL': label,
            'COMMIT_HASH': c_hash, 'COMMIT_DATE': c_date
        })
    return labeled_data

def start(token=None):
    token = token or os.getenv("GITHUB_TOKEN")
    if not token:
        print("Erro: GITHUB_TOKEN não configurado.")
        sys.exit(1)
    targets = discover_repositories(token, limit=120)
    print(f"--- {len(targets)} projetos identificados ---")
    for target in targets:
        owner, repo = target['owner'], target['repo']
        releases = extract_releases(token, owner, repo)
        timelines = get_timelines(releases, delta=1, limit=None)
        for tag, start_dt, end_dt in timelines:
            fails = get_failed_commits(token, owner, repo, start_dt, end_dt)
            if not fails: continue
            risky = get_files_from_commits(token, owner, repo, fails)
            analyze_release_task.delay(owner, repo, tag, risky, start_dt)
    print(f"\n>>> CONCLUÍDO! Tarefas enfileiradas.")

if __name__ == "__main__":
    if len(sys.argv) > 1: start(sys.argv[1])
    else: start()
