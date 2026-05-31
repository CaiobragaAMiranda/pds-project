import os
import time
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pds.train import train

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carrega .env
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, "..", "..", "..", ".env")
load_dotenv(dotenv_path)

# Configurações do Loop
TRAIN_THRESHOLD_RELEASES = 100 # Treina a cada 100 novas releases processadas
CHECK_INTERVAL_SECONDS = 300 # Verifica o banco a cada 5 minutos

class PDSOrchestrator:
    def __init__(self):
        user = os.getenv("DB_USER", "postgres")
        pw = os.getenv("DB_PASS", "postgres")
        host = os.getenv("DB_HOST", "127.0.0.1")
        port = os.getenv("DB_PORT", "5433")
        db = os.getenv("DB_NAME", "pds_db")
        url = f"postgresql+pg8000://{user}:{pw}@{host}:{port}/{db}"
        self.engine = create_engine(url)

    def get_metadata(self, key):
        with self.engine.connect() as conn:
            query = text("SELECT value FROM system_metadata WHERE key = :key")
            result = conn.execute(query, {"key": key}).fetchone()
            return result[0] if result else None

    def update_metadata(self, key, value):
        with self.engine.begin() as conn:
            query = text("""
                INSERT INTO system_metadata (key, value, updated_at) 
                VALUES (:key, :value, CURRENT_TIMESTAMP)
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
            """)
            conn.execute(query, {"key": key, "value": str(value)})

    def get_total_processed_releases(self):
        with self.engine.connect() as conn:
            query = text("SELECT SUM(processed_releases) FROM mining_progress")
            result = conn.execute(query).fetchone()
            return int(result[0]) if result and result[0] else 0

    def run(self):
        logging.info("Iniciando Orquestrador de Treinamento Contínuo PDS.")
        
        while True:
            try:
                current_count = self.get_total_processed_releases()
                last_count = int(self.get_metadata('last_trained_release_count') or 0)
                
                diff = current_count - last_count
                logging.info(f"Status: {current_count} releases processadas. {diff} novas desde o último treino.")

                if diff >= TRAIN_THRESHOLD_RELEASES:
                    logging.info(f"Threshold atingido ({TRAIN_THRESHOLD_RELEASES}). Iniciando Online Learning...")
                    # Executa o treino (20k steps para fine-tuning)
                    train(steps=20000, is_continual=True)
                    
                    # Atualiza metadados
                    self.update_metadata('last_trained_release_count', current_count)
                    logging.info("Modelo atualizado e metadados sincronizados.")
                else:
                    logging.info(f"Aguardando mais dados ({diff}/{TRAIN_THRESHOLD_RELEASES}).")

            except Exception as e:
                logging.error(f"Erro no loop do Orquestrador: {e}")

            time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    orchestrator = PDSOrchestrator()
    orchestrator.run()
