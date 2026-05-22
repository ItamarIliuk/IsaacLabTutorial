"""Script de treinamento do quadrúpede com RSL-RL.

Uso:
    # Treinamento padrão (4096 envs):
    ./isaaclab.sh -p workshop/scripts/treinar.py --task Workshop-Anymal-v0 --headless

    # Reduzir envs se tiver menos VRAM:
    ./isaaclab.sh -p workshop/scripts/treinar.py --task Workshop-Anymal-v0 --headless --num_envs 1024

    # Retomar de checkpoint:
    ./isaaclab.sh -p workshop/scripts/treinar.py --task Workshop-Anymal-v0 --headless \\
        --resume --load_run workshop_quadrupede_anymal
"""

import argparse

from isaaclab.app import AppLauncher

# ------------------------------------------------------------
# Argumentos de linha de comando
# ------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="Workshop Isaac Lab — Treinamento do Quadrúpede"
)
parser.add_argument(
    "--num_envs",
    type=int,
    default=4096,
    help="Número de ambientes paralelos. Reduza para 1024 se tiver pouca VRAM.",
)
parser.add_argument(
    "--max_iterations",
    type=int,
    default=1500,
    help="Número máximo de iterações de treinamento.",
)
parser.add_argument(
    "--resume",
    action="store_true",
    help="Retomar treinamento de checkpoint existente.",
)
parser.add_argument(
    "--load_run",
    type=str,
    default=None,
    help="Nome do experimento para carregar (usado com --resume).",
)
AppLauncher.add_app_launcher_args(parser)
args_cli, _ = parser.parse_known_args()

# Lançar Isaac Sim (deve ser antes de qualquer import do Isaac Lab)
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

# ------------------------------------------------------------
# Imports (após iniciar o simulador)
# ------------------------------------------------------------
import os
import gymnasium as gym
import torch

from isaaclab_tasks.utils import get_checkpoint_path, parse_env_cfg
from isaaclab_rl.rsl_rl.runners import OnPolicyRunner

import workshop_quadrupede  # registra o ambiente "Workshop-Anymal-v0"


def main():
    # Configurar ambiente
    env_cfg = parse_env_cfg(
        "Workshop-Anymal-v0",
        device=args_cli.device,
        num_envs=args_cli.num_envs,
    )
    env = gym.make("Workshop-Anymal-v0", cfg=env_cfg)

    # Configurar agente PPO
    from workshop_quadrupede.agents.rsl_rl_ppo_cfg import AnymalWorkshopPPORunnerCfg

    agent_cfg = AnymalWorkshopPPORunnerCfg()
    agent_cfg.max_iterations = args_cli.max_iterations

    # Diretório de logs
    log_dir = os.path.join("logs", agent_cfg.experiment_name)
    os.makedirs(log_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f" Treinamento: {agent_cfg.experiment_name}")
    print(f" Ambientes paralelos: {args_cli.num_envs}")
    print(f" Iterações: {agent_cfg.max_iterations}")
    print(f" Logs: {log_dir}")
    print(f" Dispositivo: {args_cli.device}")
    print(f"{'='*60}\n")
    print(" Para monitorar: tensorboard --logdir logs --port 6006")
    print(f"{'='*60}\n")

    # Criar runner PPO
    runner = OnPolicyRunner(
        env,
        agent_cfg,
        log_dir=log_dir,
        device=args_cli.device,
    )

    # Retomar de checkpoint se solicitado
    if args_cli.resume and args_cli.load_run:
        checkpoint = get_checkpoint_path(log_dir, run_dir=args_cli.load_run)
        if checkpoint:
            print(f"Retomando de: {checkpoint}")
            runner.load(checkpoint)

    # Iniciar treinamento
    runner.learn(
        num_learning_iterations=agent_cfg.max_iterations,
        init_at_random_ep_len=True,
    )

    env.close()
    simulation_app.close()


if __name__ == "__main__":
    main()
