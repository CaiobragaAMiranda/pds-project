import os
from stable_baselines3 import PPO
from pds.environment import PDSEnvironment
from stable_baselines3.common.callbacks import CheckpointCallback
import torch

def train():
    # 1. Instancia o Ambiente
    env = PDSEnvironment()
    
    # 2. Define o Modelo (PPO - Proximal Policy Optimization)
    # Usamos uma MLP (Multi-Layer Perceptron) como política
    model = PPO(
        "MlpPolicy", 
        env, 
        verbose=1, 
        device="cuda" if torch.cuda.is_available() else "cpu",
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99, # Fator de desconto para importância de eventos futuros
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
