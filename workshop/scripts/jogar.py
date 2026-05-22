"""Executa a política treinada do quadrúpede no simulador.

Uso:
    # Carregar checkpoint automático (mais recente):
    ./isaaclab.sh -p workshop/scripts/jogar.py --task Workshop-Anymal-v0 \\
        --load_run workshop_quadrupede_anymal --num_envs 32

    # Especificar checkpoint exato:
    ./isaaclab.sh -p workshop/scripts/jogar.py --task Workshop-Anymal-v0 \\
        --load_run workshop_quadrupede_anymal --checkpoint model_1500.pt
"""

import argparse

from isaaclab.app import AppLauncher

# ------------------------------------------------------------
# Argumentos
# ------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="Workshop Isaac Lab — Executar Política Treinada"
)
parser.add_argument("--num_envs", type=int, default=32, help="Ambientes para visualizar")
parser.add_argument("--load_run", type=str, required=True, help="Nome do experimento")
parser.add_argument("--checkpoint", type=str, default="model_.*.pt", help="Arquivo do checkpoint")
AppLauncher.add_app_launcher_args(parser)
args_cli, _ = parser.parse_known_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

# ------------------------------------------------------------
# Imports
# ------------------------------------------------------------
import os
import torch
import gymnasium as gym

from isaaclab_tasks.utils import get_checkpoint_path, parse_env_cfg
from isaaclab_rl.rsl_rl.runners import OnPolicyRunner

import workshop_quadrupede


def main():
    env_cfg = parse_env_cfg(
        "Workshop-Anymal-v0",
        device=args_cli.device,
        num_envs=args_cli.num_envs,
    )
    # Sem ruído na política durante execução
    env_cfg.episode_length_s = 60.0  # episódios mais longos para visualização

    env = gym.make("Workshop-Anymal-v0", cfg=env_cfg)

    from workshop_quadrupede.agents.rsl_rl_ppo_cfg import AnymalWorkshopPPORunnerCfg

    agent_cfg = AnymalWorkshopPPORunnerCfg()
    agent_cfg.resume = True
    agent_cfg.load_run = args_cli.load_run
    agent_cfg.load_checkpoint = args_cli.checkpoint

    log_dir = os.path.join("logs", agent_cfg.experiment_name)
    checkpoint = get_checkpoint_path(
        log_dir,
        run_dir=args_cli.load_run,
        checkpoint=args_cli.checkpoint,
        other_dirs=["."],
    )

    print(f"\nCarregando checkpoint: {checkpoint}")

    runner = OnPolicyRunner(
        env,
        agent_cfg,
        log_dir=None,
        device=args_cli.device,
    )
    runner.load(checkpoint)

    # Obter política sem ruído de exploração
    policy = runner.get_inference_policy(device=args_cli.device)

    # Loop de execução
    obs, _ = env.reset()
    step = 0
    print("\nExecutando política... (Ctrl+C para parar)")
    print("Acesse o streaming em: http://localhost:49100\n")

    try:
        while simulation_app.is_running():
            with torch.inference_mode():
                actions = policy(obs["policy"])
            obs, rewards, terminated, truncated, info = env.step(actions)
            step += 1

            if step % 200 == 0:
                mean_reward = rewards.mean().item()
                print(f"Step {step:5d} | Reward médio: {mean_reward:.3f}")
    except KeyboardInterrupt:
        print("\nParado pelo usuário.")

    env.close()
    simulation_app.close()


if __name__ == "__main__":
    main()
