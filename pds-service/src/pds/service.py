import pickle
import pandas as pd
import os
from stable_baselines3 import PPO
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega configurações do ambiente
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, "..", "..", "..", ".env")
load_dotenv(dotenv_path)

class PDSService:
    """
    Serviço Híbrido de Predição de Defeitos (Suporta Random Forest e RL PPO).
    """

    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.use_rl = model_path.endswith('.zip') or 'agent' in model_path
        
        if self.use_rl:
            self.model = PPO.load(model_path)
            # Configuração de Banco para Features de RL
            user = os.getenv("DB_USER", "postgres")
            pw = os.getenv("DB_PASS", "postgres")
            host = os.getenv("DB_HOST", "127.0.0.1")
            port = os.getenv("DB_PORT", "5433")
            db = os.getenv("DB_NAME", "pds_db")
            url = f"postgresql+pg8000://{user}:{pw}@{host}:{port}/{db}"
            self.engine = create_engine(url)
            print(f"PDSService: Agente RL carregado de {model_path}")
        else:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"PDSService: Modelo Supervisionado carregado de {model_path}")

    def predict(self, data_tuple: list = None, file_path: str = None) -> list:
        """
        Realiza a predição. Se file_path for fornecido e o modelo for RL, 
        busca features normalizadas no banco.
        """
        if self.use_rl:
            if file_path:
                return self._predict_rl_by_path(file_path)
            else:
                # Fallback: Se não tem path, o RL não tem contexto temporal.
                # Para fins de demonstração, retornamos saudável (0).
                return [0]
        else:
            # Lógica legada para Random Forest
            X_features = ["LOC", "COM", "BLK", "NOF", "NOC", "APF", "AMC", "NER", "NEH", "CYC", "MAD"]
            dataset = pd.DataFrame([data_tuple], columns=X_features)
            return self.model.predict(dataset).tolist()

    def _predict_rl_by_path(self, file_path: str) -> list:
        """Busca as features de RL (Z-scores, Deltas) no banco e prediz."""
        query = text("""
            SELECT z_loc, z_cyc, z_mad, delta_loc, delta_cyc, delta_mad, sin_dow, cos_dow 
            FROM vw_rl_features 
            WHERE file_path = :path 
            LIMIT 1
        """)
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(query, conn, params={"path": file_path})
            
            if df.empty:
                return [0]
            
            obs = df.values.astype("float32")
            action, _states = self.model.predict(obs, deterministic=True)
            return [int(action)]
        except Exception as e:
            print(f"Erro ao buscar features RL: {e}")
            return [0]
