import os
import torch
from stable_baselines3 import PPO
from pds.environment import PDSEnvironment
from stable_baselines3.common.callbacks import CheckpointCallback

# --- CONFIGURAÇÃO DE MEMÓRIA GPU ---
# Limita a fragmentação e ajuda a manter o uso abaixo de 2GB
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32"

def train():
    # 1. Instancia o Ambiente
    env = PDSEnvironment()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    if device == "cuda":
        # Limita a memória visível ou reserva para evitar estourar os 2GB
        # O PyTorch não tem um "hard limit" nativo por software tão simples, 
        # mas podemos monitorar e limpar o cache.
        torch.cuda.empty_cache()
        print(f"GPU Detectada: {torch.cuda.get_device_name(0)}")
        print("Configurando limite de fragmentação para economia de VRAM.")

    # 2. Define o Modelo (PPO)
    model = PPO(
        "MlpPolicy", 
        env, 
        verbose=1, 
        device=device,
        learning_rate=3e-4,
        n_steps=1024, # Reduzido de 2048 para economizar memória durante o rollout
        batch_size=32, # Reduzido de 64 para diminuir o consumo de VRAM
        n_epochs=10,
        gamma=0.99,
    )

    print(f"Iniciando treinamento no dispositivo: {model.device}")

    # 3. Callback para salvar progresso
    checkpoint_callback = CheckpointCallback(
        save_freq=10000, 
        save_path='./models/',
        name_prefix='pds_agent'
    )

    # 4. Treinamento
    # Como os dados são massivos, vamos treinar por 100.000 timesteps iniciais
    model.learn(total_timesteps=100000, callback=checkpoint_callback)

    # 5. Salva o modelo final
    model.save("pds_bug_hunter_agent")
    print("Treinamento concluído. Agente 'pds_bug_hunter_agent' pronto para identificação.")

if __name__ == "__main__":
    train()
