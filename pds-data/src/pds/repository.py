from sqlalchemy import create_engine, text
import os
import logging
from dotenv import load_dotenv

# Carrega .env
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, "..", "..", "..", ".env")
load_dotenv(dotenv_path)

class PDSRepository:
    def __init__(self):
        user = os.getenv("DB_USER", "postgres")
        pw = os.getenv("DB_PASS", "postgres")
        host = os.getenv("DB_HOST", "127.0.0.1")
        port = os.getenv("DB_PORT", "5432")
        db = os.getenv("DB_NAME", "pds_db")
        
        url = f"postgresql+pg8000://{user}:{pw}@{host}:{port}/{db}"
        self.engine = create_engine(url)

    def get_or_create_project(self, owner, name):
        with self.engine.begin() as conn:
            query = text("""
                INSERT INTO projects (owner, name) VALUES (:owner, :name)
                ON CONFLICT (owner, name) DO UPDATE SET name = EXCLUDED.name 
                RETURNING id
            """)
            result = conn.execute(query, {"owner": owner, "name": name})
            return result.fetchone()[0]

    def get_or_create_release(self, project_id, tag_name, published_at):
        with self.engine.begin() as conn:
            query = text("""
                INSERT INTO releases (project_id, tag_name, published_at) VALUES (:project_id, :tag_name, :published_at)
                ON CONFLICT (project_id, tag_name) DO UPDATE SET published_at = EXCLUDED.published_at 
                RETURNING id
            """)
            result = conn.execute(query, {
                "project_id": project_id, 
                "tag_name": tag_name, 
                "published_at": published_at
            })
            return result.fetchone()[0]

    def is_release_processed(self, release_id):
        with self.engine.connect() as conn:
            query = text("SELECT 1 FROM file_metrics WHERE release_id = :release_id LIMIT 1")
            result = conn.execute(query, {"release_id": release_id})
            return result.fetchone() is not None

    def save_metrics(self, release_id, metrics_list):
        if not metrics_list:
            return

        query = text("""
            INSERT INTO file_metrics 
            (release_id, file_path, loc, com, blk, nof, noc, apf, amc, ner, neh, cyc, mad, build_fail, commit_hash, commit_date)
            VALUES (:release_id, :file_path, :loc, :com, :blk, :nof, :noc, :apf, :amc, :ner, :neh, :cyc, :mad, :build_fail, :commit_hash, :commit_date)
            ON CONFLICT (release_id, file_path) DO NOTHING
        """)
        
        data = [
            {
                "release_id": release_id, "file_path": m['FILE'], "loc": m['LOC'], "com": m['COM'], 
                "blk": m['BLK'], "nof": m['NOF'], "noc": m['NOC'], "apf": m['APF'], 
                "amc": m['AMC'], "ner": m['NER'], "neh": m['NEH'], "cyc": m['CYC'], 
                "mad": m['MAD'], "build_fail": bool(m['BUILD_FAIL']),
                "commit_hash": m.get('COMMIT_HASH'), "commit_date": m.get('COMMIT_DATE')
            }
            for m in metrics_list
        ]
        
        with self.engine.begin() as conn:
            conn.execute(query, data)

    def close(self):
        self.engine.dispose()
