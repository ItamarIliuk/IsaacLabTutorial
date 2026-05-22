"""Pacote do ambiente quadrúpede para o workshop."""

import gymnasium as gym

##
# Registro do ambiente no Gymnasium
##

gym.register(
    id="Workshop-Anymal-v0",
    entry_point="workshop_quadrupede.envs:AnymalWorkshopEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": "workshop_quadrupede.envs:AnymalWorkshopEnvCfg",
        "rsl_rl_cfg_entry_point": f"{__name__}.agents.rsl_rl_ppo_cfg:AnymalWorkshopPPORunnerCfg",
    },
)
