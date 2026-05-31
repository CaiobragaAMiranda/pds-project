import os
import torch
import logging
from stable_baselines3 import PPO
from pds.environment import PDSEnvironment
from stable_baselines3.common.callbacks import CheckpointCallback

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONFIGURAÇÃO DE MEMÓRIA GPU ---
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32"

MODEL_NAME = "pds_bug_hunter_agent"
MODEL_PATH = f"{MODEL_NAME}.zip"

def train(steps=100000, is_continual=False):
    """
    Realiza o treinamento do Agente RL. 
    Se is_continual=True, tenta carregar o modelo existente para fine-tuning.
    """
    env = PDSEnvironment()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    if device == "cuda":
        torch.cuda.empty_cache()
        logging.info(f"GPU Detectada: {torch.cuda.get_device_name(0)}. Otimizando VRAM.")

    if is_continual and os.path.exists(MODEL_PATH):
        logging.info(f"Modo Online Learning: Carregando modelo existente '{MODEL_PATH}'")
        model = PPO.load(MODEL_PATH, env=env, device=device)
    else:
        logging.info("Iniciando Treinamento Base do Agente PPO.")
        model = PPO(
            "MlpPolicy", 
            env, 
            verbose=1, 
            device=device,
            learning_rate=3e-4,
            n_steps=1024,
            batch_size=32,
            n_epochs=10,
            gamma=0.99,
        )

    logging.info(f"Executando {steps} timesteps no dispositivo: {model.device}")

    checkpoint_callback = CheckpointCallback(
        save_freq=20000, 
        save_path='./models/',
        name_prefix='pds_agent_checkpoint'
    )

    # Treinamento
    model.learn(total_timesteps=steps, callback=checkpoint_callback, reset_num_timesteps=not is_continual)

    # Salva o modelo final
    model.save(MODEL_NAME)
    logging.info(f"Treinamento concluído. Agente '{MODEL_NAME}' atualizado e pronto.")

if __name__ == "__main__":
    import sys
    # Se passar 'online' como argumento, faz o fine-tuning
    continual = len(sys.argv) > 1 and sys.argv[1] == 'online'
    # Reduzimos os passos para aprendizado contínuo se for o caso
    steps = 20000 if continual else 100000
    train(steps=steps, is_continual=continual)
