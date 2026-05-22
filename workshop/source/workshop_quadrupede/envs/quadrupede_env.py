"""Ambiente de locomoção quadrúpede para o workshop.

Implementa um MDP de locomoção para o robô Anymal C usando Isaac Lab.
O agente aprende a seguir comandos de velocidade (x, y, yaw) em terreno plano.

Referência: https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs
"""

from __future__ import annotations

import torch
from dataclasses import MISSING

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation, ArticulationCfg
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils import configclass

# Asset do Anymal C (disponível no Isaac Lab)
try:
    from isaaclab_assets import ANYMAL_C_CFG
except ImportError:
    # Fallback: configuração simplificada para testes sem o asset completo
    from isaaclab.assets import ArticulationCfg
    from isaaclab.actuators import ImplicitActuatorCfg
    ANYMAL_C_CFG = ArticulationCfg(
        prim_path="{ENV_REGEX_NS}/Robot",
        spawn=sim_utils.UsdFileCfg(
            usd_path="${ISAACLAB_ASSETS_DATA_DIR}/Robots/ANYbotics/anymal_c/anymal_c.usd",
            activate_contact_sensors=True,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                disable_gravity=False,
                retain_accelerations=False,
                linear_damping=0.0,
                angular_damping=0.0,
                max_linear_velocity=1000.0,
                max_angular_velocity=1000.0,
                max_depenetration_velocity=1.0,
            ),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=True,
                solver_position_iteration_count=4,
                solver_velocity_iteration_count=0,
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.6),
            joint_pos={
                ".*HAA": 0.0,
                ".*HFE": 0.4,
                ".*KFE": -0.8,
            },
        ),
        actuators={
            "legs": ImplicitActuatorCfg(
                joint_names_expr=[".*HAA", ".*HFE", ".*KFE"],
                effort_limit=80.0,
                velocity_limit=7.5,
                stiffness=80.0,
                damping=2.0,
            ),
        },
    )


@configclass
class AnymalWorkshopEnvCfg(DirectRLEnvCfg):
    """Configuração do ambiente de locomoção do Anymal para o workshop."""

    # --- Simulação ---
    sim: SimulationCfg = SimulationCfg(
        dt=0.005,           # passo de tempo: 5ms (200 Hz)
        render_interval=4,  # renderizar a cada 4 steps de física (50 Hz)
    )

    # --- Cena ---
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=4096,      # ambientes paralelos (reduzir se VRAM < 16 GB)
        env_spacing=2.5,    # espaçamento entre instâncias (metros)
        replicate_physics=True,
    )

    # --- Robô ---
    robot: ArticulationCfg = ANYMAL_C_CFG.replace(
        prim_path="/World/envs/env_.*/Robot"
    )

    # --- Terreno ---
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
        debug_vis=False,
    )

    # --- Espaços de ação e observação ---
    # Observação: lin_vel(3) + ang_vel(3) + gravidade_proj(3) + cmd(3) +
    #             joint_pos(12) + joint_vel(12) + actions(12) = 48
    action_space: int = 12   # 12 joints do Anymal (3 por pata x 4 patas)
    observation_space: int = 48
    state_space: int = 0     # sem estado privilegiado neste exemplo

    # --- Escala de ações ---
    # As redes aprendem valores em [-1, 1], que são escalados aqui
    action_scale: float = 0.5  # radianos

    # --- Comandos de velocidade (amostrados aleatoriamente a cada reset) ---
    cmd_lin_vel_x_range: tuple = (-1.0, 1.0)    # m/s: frente/atrás
    cmd_lin_vel_y_range: tuple = (-1.0, 1.0)    # m/s: lateral
    cmd_ang_vel_yaw_range: tuple = (-1.0, 1.0)  # rad/s: rotação

    # --- Coeficientes de recompensa ---
    # Positivos: comportamentos desejados
    rew_lin_vel_xy_scale: float = 1.0     # seguir velocidade linear (principal)
    rew_ang_vel_z_scale: float = 0.5      # seguir velocidade angular
    rew_feet_air_time_scale: float = 0.25  # incentivar marcha (pés no ar)
    # Negativos: penalidades
    rew_lin_vel_z_scale: float = -2.0     # não pular
    rew_ang_vel_xy_scale: float = -0.05   # não rolar/tombar
    rew_joint_acc_scale: float = -2.5e-7  # movimento suave (aceleração)
    rew_action_rate_scale: float = -0.01  # controle suave (variação de ação)
    rew_flat_orientation_scale: float = -5.0  # ficar ereto

    # --- Duração do episódio ---
    episode_length_s: float = 20.0  # segundos


class AnymalWorkshopEnv(DirectRLEnv):
    """Ambiente de locomoção quadrúpede.

    O robô Anymal C deve aprender a seguir comandos de velocidade
    em um plano horizontal. O treinamento usa PPO via RSL-RL.
    """

    cfg: AnymalWorkshopEnvCfg

    def __init__(
        self,
        cfg: AnymalWorkshopEnvCfg,
        render_mode: str | None = None,
        **kwargs,
    ):
        super().__init__(cfg, render_mode, **kwargs)

        # Índices dos joints (todos os 12 joints de perna)
        self._joint_ids, _ = self.robot.find_joints(".*")

        # Posições/velocidades padrão dos joints
        self._default_joint_pos = self.robot.data.default_joint_pos.clone()
        self._default_joint_vel = self.robot.data.default_joint_vel.clone()

        # Buffer de ações internas (inicializado em zero)
        self._actions = torch.zeros(
            self.num_envs, self.cfg.action_space, device=self.device
        )
        self._last_actions = torch.zeros_like(self._actions)

        # Comandos de velocidade: [lin_x, lin_y, ang_yaw]
        self._commands = torch.zeros(self.num_envs, 3, device=self.device)

        # Estado dos pés (para recompensa de marcha)
        self._feet_ids, _ = self.robot.find_bodies(".*FOOT")
        self._feet_air_time = torch.zeros(
            self.num_envs, len(self._feet_ids), device=self.device
        )
        self._last_contact = torch.zeros(
            self.num_envs, len(self._feet_ids), dtype=torch.bool, device=self.device
        )

    def _setup_scene(self):
        """Configura a cena: robô, terreno e iluminação."""
        # Adicionar robô
        self.robot = Articulation(self.cfg.robot)
        self.scene.articulations["robot"] = self.robot

        # Configurar terreno
        self.cfg.terrain.num_envs = self.scene.cfg.num_envs
        self.cfg.terrain.env_spacing = self.scene.cfg.env_spacing
        self.terrain = self.cfg.terrain.class_type(self.cfg.terrain)

        # Clonar ambientes em grid
        self.scene.clone_environments(copy_from_source=False)
        self.scene.filter_collisions(global_prim_paths=[self.cfg.terrain.prim_path])

        # Iluminação dome
        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)

    def _pre_physics_step(self, actions: torch.Tensor):
        """Recebe ações da política e prepara para aplicar no simulador."""
        self._last_actions = self._actions.clone()
        # Clamp para garantir ações no range [-1, 1]
        self._actions = actions.clamp(-1.0, 1.0)

    def _apply_action(self):
        """Converte ações normalizadas em alvos de posição de joint."""
        # Posição alvo = posição padrão + escala * ação
        joint_targets = self._default_joint_pos + self.cfg.action_scale * self._actions
        self.robot.set_joint_position_target(joint_targets, joint_ids=self._joint_ids)
        self.robot.write_data_to_sim()

    def _get_observations(self) -> dict:
        """Constrói o vetor de observação (48 dimensões).

        O vetor concatena (no frame do robô):
        - Velocidade linear da base     (3)
        - Velocidade angular da base    (3)
        - Gravidade projetada           (3) — detecta inclinação
        - Comandos de velocidade        (3)
        - Posições dos joints (rel.)    (12)
        - Velocidades dos joints        (12)
        - Últimas ações                 (12)
        ─────────────────────────────────
        Total:                          (48)
        """
        obs = torch.cat(
            [
                self.robot.data.root_lin_vel_b,                        # (N, 3)
                self.robot.data.root_ang_vel_b,                        # (N, 3)
                self.robot.data.projected_gravity_b,                   # (N, 3)
                self._commands,                                         # (N, 3)
                self.robot.data.joint_pos - self._default_joint_pos,  # (N, 12)
                self.robot.data.joint_vel,                             # (N, 12)
                self._actions,                                          # (N, 12)
            ],
            dim=-1,
        )  # shape: (N, 48)

        return {"policy": obs}

    def _get_rewards(self) -> torch.Tensor:
        """Calcula a recompensa total como soma de termos."""
        lin_vel_b = self.robot.data.root_lin_vel_b
        ang_vel_b = self.robot.data.root_ang_vel_b
        projected_gravity = self.robot.data.projected_gravity_b
        joint_acc = self.robot.data.joint_acc

        rewards = {}

        # 1. Rastreamento de velocidade linear (x, y) — principal sinal de aprendizado
        lin_vel_error = torch.sum(
            torch.square(self._commands[:, :2] - lin_vel_b[:, :2]), dim=1
        )
        rewards["lin_vel_xy"] = (
            torch.exp(-lin_vel_error / 0.25) * self.cfg.rew_lin_vel_xy_scale
        )

        # 2. Rastreamento de velocidade angular (yaw)
        ang_vel_error = torch.square(
            self._commands[:, 2] - ang_vel_b[:, 2]
        )
        rewards["ang_vel_z"] = (
            torch.exp(-ang_vel_error / 0.25) * self.cfg.rew_ang_vel_z_scale
        )

        # 3. Penalidade de velocidade vertical (robô não deve pular)
        rewards["lin_vel_z"] = (
            torch.square(lin_vel_b[:, 2]) * self.cfg.rew_lin_vel_z_scale
        )

        # 4. Penalidade de velocidade angular horizontal (não rolar/tombar)
        rewards["ang_vel_xy"] = (
            torch.sum(torch.square(ang_vel_b[:, :2]), dim=1)
            * self.cfg.rew_ang_vel_xy_scale
        )

        # 5. Penalidade de aceleração de joint (movimento suave)
        rewards["joint_acc"] = (
            torch.sum(torch.square(joint_acc), dim=1)
            * self.cfg.rew_joint_acc_scale
        )

        # 6. Penalidade de variação de ação (controle suave)
        rewards["action_rate"] = (
            torch.sum(torch.square(self._actions - self._last_actions), dim=1)
            * self.cfg.rew_action_rate_scale
        )

        # 7. Penalidade de orientação (robô deve ficar ereto)
        rewards["flat_orientation"] = (
            torch.sum(torch.square(projected_gravity[:, :2]), dim=1)
            * self.cfg.rew_flat_orientation_scale
        )

        # Soma todos os termos de recompensa
        total_reward = sum(rewards.values())
        return total_reward

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        """Determina quando terminar ou resetar cada ambiente.

        Returns:
            terminated: robô caiu (reiniciar com penalidade)
            time_out: limite de tempo atingido (reiniciar sem penalidade)
        """
        # Termina se a base estiver muito baixa (robô caiu)
        height = self.robot.data.root_pos_w[:, 2]
        terminated = height < 0.3  # metros

        # Timeout ao atingir limite do episódio
        time_out = self.episode_length_buf >= self.max_episode_length - 1

        return terminated, time_out

    def _reset_idx(self, env_ids: torch.Tensor):
        """Reseta os ambientes indicados para estado inicial."""
        if len(env_ids) == 0:
            return

        super()._reset_idx(env_ids)

        # Resetar joints com pequena perturbação aleatória (diversidade)
        joint_pos = self._default_joint_pos[env_ids].clone()
        joint_vel = self._default_joint_vel[env_ids].clone()
        joint_pos += torch.randn_like(joint_pos) * 0.1
        joint_vel += torch.randn_like(joint_vel) * 0.05

        self.robot.write_joint_state_to_sim(
            joint_pos, joint_vel, env_ids=env_ids
        )

        # Resetar posição e orientação da base
        default_root_state = self.robot.data.default_root_state[env_ids].clone()
        default_root_state[:, :3] += self.scene.env_origins[env_ids]
        self.robot.write_root_state_to_sim(default_root_state, env_ids=env_ids)

        # Amostrar novos comandos de velocidade aleatórios
        lo, hi = self.cfg.cmd_lin_vel_x_range
        self._commands[env_ids, 0] = torch.empty(len(env_ids), device=self.device).uniform_(lo, hi)
        lo, hi = self.cfg.cmd_lin_vel_y_range
        self._commands[env_ids, 1] = torch.empty(len(env_ids), device=self.device).uniform_(lo, hi)
        lo, hi = self.cfg.cmd_ang_vel_yaw_range
        self._commands[env_ids, 2] = torch.empty(len(env_ids), device=self.device).uniform_(lo, hi)

        # Resetar buffers internos
        self._actions[env_ids] = 0.0
        self._last_actions[env_ids] = 0.0
        self._feet_air_time[env_ids] = 0.0
        self._last_contact[env_ids] = False
