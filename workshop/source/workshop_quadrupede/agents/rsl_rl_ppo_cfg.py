"""Configuração do agente PPO via RSL-RL para o workshop."""

from isaaclab.utils import configclass

from isaaclab_rl.rsl_rl import (
    RslRlOnPolicyRunnerCfg,
    RslRlPpoActorCriticCfg,
    RslRlPpoAlgorithmCfg,
)


@configclass
class AnymalWorkshopPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    """Configuração do runner PPO para o workshop de locomoção.

    Hiperparâmetros balanceados para treinamento em ~1h em RTX 4090
    com 4096 ambientes paralelos.
    """

    # --- Coleta de dados ---
    num_steps_per_env: int = 24         # passos por ambiente antes de atualizar
    # total de amostras/iter = num_steps_per_env * num_envs = 24 * 4096 = 98304

    # --- Duração do treinamento ---
    max_iterations: int = 1500          # iterações totais (~1h em RTX 4090)
    save_interval: int = 100            # salvar checkpoint a cada N iterações
    experiment_name: str = "workshop_quadrupede_anymal"
    empirical_normalization: bool = False

    # --- Arquitetura da rede neural ---
    policy: RslRlPpoActorCriticCfg = RslRlPpoActorCriticCfg(
        init_noise_std=1.0,
        actor_hidden_dims=[512, 256, 128],   # rede do ator (política)
        critic_hidden_dims=[512, 256, 128],  # rede do crítico (valor)
        activation="elu",                    # ELU: boa para locomotion tasks
    )

    # --- Algoritmo PPO ---
    algorithm: RslRlPpoAlgorithmCfg = RslRlPpoAlgorithmCfg(
        # Coeficientes de perda
        value_loss_coef=1.0,          # peso da perda do crítico
        use_clipping=True,            # PPO clipping (estabilidade)
        clip_param=0.2,               # epsilon do clipping
        entropy_coef=0.01,            # incentiva exploração

        # Atualização
        num_learning_epochs=5,        # épocas de gradiente por iteração
        num_mini_batches=4,           # mini-batches por época
        learning_rate=1.0e-3,         # taxa de aprendizado inicial
        schedule="adaptive",          # ajusta LR baseado no KL divergence

        # Desconto e GAE
        gamma=0.99,                   # desconto de recompensa
        lam=0.95,                     # parâmetro GAE-Lambda

        # Regularização
        desired_kl=0.01,              # KL target para ajuste do LR
        max_grad_norm=1.0,            # clipping de gradiente
    )
