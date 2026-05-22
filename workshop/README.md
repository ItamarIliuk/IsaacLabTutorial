# Workshop: Robô Quadrúpede com NVIDIA Isaac Lab

**Summit de IA — Joinville, SC | 2026**

Bem-vindo! Em **2h30min** você vai:

- Configurar um ambiente de GPU na nuvem (Vast.ai ou NVIDIA Brev)
- Instalar e usar o NVIDIA Isaac Lab com Isaac Sim 5.1
- Criar um ambiente de simulação para um robô quadrúpede (Anymal C)
- Treinar uma política de locomoção com Reinforcement Learning (RSL-RL / PPO)
- Visualizar o robô andando de forma autônoma

---

## Agenda

| Tempo | Módulo | Conteúdo |
|-------|--------|----------|
| 0:00 – 0:25 | **00 · Setup** | Conta cloud, instância GPU, Docker + Isaac Sim |
| 0:25 – 0:55 | **01 · Isaac Lab** | Conceitos, arquitetura, primeiro ambiente |
| 0:55 – 1:25 | **02 · Ambiente** | MDP, observações, ações, recompensas do quadrúpede |
| 1:25 – 2:00 | **03 · Treinamento** | RSL-RL, PPO, TensorBoard |
| 2:00 – 2:30 | **04 · Resultados** | Visualização, métricas, próximos passos |

---

## Hardware necessário (cloud)

| GPU | VRAM | Custo estimado | Adequado para |
|-----|------|----------------|---------------|
| RTX 3090 | 24 GB | ~$0,35/h | Workshop básico |
| RTX 4090 | 24 GB | ~$0,55/h | Workshop (recomendado) |
| A6000 / L40S | 48 GB | ~$1,00/h | Treinamentos avançados |

> **Atenção:** Isaac Sim requer GPU com **RT Cores**. A100 e H100 **não** são suportados para renderização.

---

## Plataformas de Cloud GPU

### Opção 1: Vast.ai
```bash
# 1. Crie conta em https://cloud.vast.ai
# 2. Adicione crédito (mínimo $5)
# 3. Siga: setup/setup_vastai.sh
```

### Opção 2: NVIDIA Brev
```bash
# 1. Crie conta em https://brev.dev
# 2. Siga: setup/setup_brev.sh
```

---

## Início Rápido (após ter a instância rodando)

```bash
# 1. Clonar o repositório
git clone https://github.com/ItamarIliuk/IsaacLabTutorial.git
cd IsaacLabTutorial

# 2. Instalar o pacote do workshop
/isaac-sim/python.sh -m pip install -e workshop/source/workshop_quadrupede

# 3. Abrir JupyterLab
/isaac-sim/python.sh -m jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

# 4. Abrir notebook: workshop/notebooks/00_setup_ambiente.ipynb
```

---

## Estrutura do Repositório

```
workshop/
├── notebooks/                      # Notebooks Jupyter por módulo
│   ├── 00_setup_ambiente.ipynb     # Módulo 0: Setup cloud
│   ├── 01_introducao_isaac_lab.ipynb  # Módulo 1: Conceitos
│   ├── 02_ambiente_quadrupede.ipynb   # Módulo 2: Criar ambiente
│   ├── 03_treinamento_rsl_rl.ipynb    # Módulo 3: Treinar
│   └── 04_resultados.ipynb            # Módulo 4: Resultados
├── setup/                          # Scripts de configuração cloud
│   ├── setup_vastai.sh             # Guia Vast.ai
│   ├── setup_brev.sh               # Guia NVIDIA Brev
│   └── setup_comum.sh              # Setup comum pós-instância
├── scripts/                        # Scripts de execução
│   ├── treinar.py                  # Lançar treinamento RL
│   └── jogar.py                    # Executar política treinada
└── source/
    └── workshop_quadrupede/        # Pacote Python do ambiente
        ├── __init__.py             # Registro do ambiente
        ├── envs/
        │   ├── __init__.py
        │   └── quadrupede_env.py   # Ambiente MDP do Anymal
        └── agents/
            ├── __init__.py
            └── rsl_rl_ppo_cfg.py   # Configuração PPO
```

---

## Tecnologias

| Tecnologia | Versão | Papel |
|-----------|--------|-------|
| NVIDIA Isaac Sim | 5.1 | Simulador físico (USD, PhysX/Newton) |
| NVIDIA Isaac Lab | latest | Framework RL para robótica |
| Newton Physics | — | Motor de física de nova geração |
| RSL-RL | 2.x | Algoritmo PPO otimizado para GPU |
| PyTorch | 2.x | Backend de deep learning |
| JupyterLab | — | Interface interativa do workshop |

---

## Pré-requisitos

- Conta no [Vast.ai](https://cloud.vast.ai/?ref_id=374137/) **ou** [NVIDIA Brev](https://brev.dev/)
- Navegador moderno (Chrome recomendado)
- Conhecimento básico de Python e redes neurais

---

## Referências

- [Isaac Lab Documentação](https://isaac-sim.github.io/IsaacLab)
- [Isaac Sim 5.1 Docs](https://docs.isaacsim.omniverse.nvidia.com/5.1.0)
- [RSL-RL GitHub](https://github.com/leggedrobotics/rsl_rl)
- [Blog NVIDIA: Quadruped Locomotion + Newton](https://developer.nvidia.com/blog/train-a-quadruped-locomotion-policy-and-simulate-cloth-manipulation-with-nvidia-isaac-lab-and-newton/)
- [Anymal Paper — ETH Zurich](https://arxiv.org/abs/1901.08652)

---

## Suporte

- Abra uma issue neste repositório
- Discord: [link do evento]
