import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Carrega .env do projeto
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, "..", "..", ".env")
load_dotenv(dotenv_path)

class PDSEnvironment(gym.Env):
    """
    Ambiente de Reinforcement Learning para Predição de Falha de Build.
    """
    def __init__(self, render_mode=None):
        super(PDSEnvironment, self).__init__()
        
        # Conexão com o banco (PostgreSQL + pg8000 para evitar encoding issues)
        user = os.getenv("DB_USER", "postgres")
        pw = os.getenv("DB_PASS", "postgres")
        host = os.getenv("DB_HOST", "127.0.0.1")
        port = os.getenv("DB_PORT", "5433")
        db = os.getenv("DB_NAME", "pds_db")
        url = f"postgresql+pg8000://{user}:{pw}@{host}:{port}/{db}"
        self.engine = create_engine(url)
        
        # Definição do Espaço de Observação (8 features contínuas)
        # z_loc, z_cyc, z_mad, delta_loc, delta_cyc, delta_mad, sin_dow, cos_dow
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(8,), dtype=np.float32
        )
        
        # Definição do Espaço de Ação (0: Build Sucesso, 1: Build Falha)
        self.action_space = spaces.Discrete(2)
        
        self.data = None
        self.current_idx = 0

    def _load_data(self):
        query = text("SELECT z_loc, z_cyc, z_mad, delta_loc, delta_cyc, delta_mad, sin_dow, cos_dow, build_fail FROM vw_rl_features")
        with self.engine.connect() as conn:
            self.data = pd.read_sql(query, conn)
            # Remove NaNs resultantes dos Deltas na primeira release
            self.data = self.data.fillna(0)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if self.data is None:
            self._load_data()
        
        # Começa de um ponto aleatório para diversidade no treino
        self.current_idx = np.random.randint(0, len(self.data))
        
        observation = self._get_obs()
        info = {}
        return observation, info

    def _get_obs(self):
        obs = self.data.iloc[self.current_idx][
            ['z_loc', 'z_cyc', 'z_mad', 'delta_loc', 'delta_cyc', 'delta_mad', 'sin_dow', 'cos_dow']
        ].values
        return obs.astype(np.float32)

    def step(self, action):
        target = int(self.data.iloc[self.current_idx]['build_fail'])
        
        # Função de Recompensa (Reward Engineering)
        # Objetivo: Acertar a falha (1) é muito valioso. Errar a falha (False Negative) é muito penalizado.
        reward = 0
        if action == target:
            if target == 1:
                reward = 10.0 # Sucesso: Detectou uma falha real
            else:
                reward = 1.0  # Sucesso: Confirmou build saudável
        else:
            if target == 1:
                reward = -20.0 # Falha Crítica: Deixou passar uma quebra (False Negative)
            else:
                reward = -5.0  # Erro: Alerta falso (False Positive)

        # Move para o próximo estado (incremental ou aleatório?)
        # Para simular série temporal, vamos para o próximo registro
        self.current_idx = (self.current_idx + 1) % len(self.data)
        
        observation = self._get_obs()
        terminated = False # Treino contínuo
        truncated = False
        info = {"target": target, "predicted": action}
        
        return observation, reward, terminated, truncated, info

    def close(self):
        self.engine.dispose()
