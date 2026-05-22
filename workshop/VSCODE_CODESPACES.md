# VS Code e GitHub Codespaces

Este guia explica como participar do workshop usando **VS Code** ou **GitHub Codespaces**, para quem prefere um ambiente de desenvolvimento mais familiar ao invés da linha de comando.

---

## Sumário

- [Opção A: VS Code Local + Docker](#opção-a-vs-code-local--docker)
- [Opção B: GitHub Codespaces](#opção-b-github-codespaces)
- [Tarefas Pré-configuradas](#tarefas-pré-configuradas)
- [Limitações e Requisitos de GPU](#limitações-e-requisitos-de-gpu)

---

## Opção A: VS Code Local + Docker

> **Recomendado** para simulação e treinamento completos.

### Pré-requisitos

| Requisito | Mínimo | Recomendado |
|-----------|--------|-------------|
| GPU | NVIDIA RTX (com RT Cores) | RTX 3090 / 4090 |
| VRAM | 8 GB | 16–24 GB |
| RAM | 32 GB | 64 GB |
| Disco | 60 GB livres (imagem ~40 GB) | 100 GB SSD |
| Docker | Engine 24+ | Docker Desktop |
| NVIDIA Toolkit | Container Toolkit | última versão |

### Passo a Passo

**1. Instalar dependências:**

```bash
# Docker Engine
curl -fsSL https://get.docker.com | sh

# NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

**2. Pré-baixar a imagem Isaac Sim** (~40 GB — faça isso antes do workshop):

```bash
docker pull nvcr.io/nvidia/isaac-sim:5.1.0
```

> ⏱️ O download pode levar 30–60 minutos dependendo da conexão.

**3. Clonar o repositório:**

```bash
git clone https://github.com/itamariliuk/isaaclabtutorial.git
cd isaaclabtutorial
```

**4. Abrir no VS Code com Dev Container:**

```bash
code .
```

Quando o VS Code abrir:
- Clique em **"Reopen in Container"** na notificação (canto inferior direito)
- **OU** `Ctrl+Shift+P` → `Dev Containers: Reopen in Container`
- Selecione: **"Workshop Quadrúpede - Isaac Sim Completo (Local)"**

**5. Aguardar o setup automático:**

O script `setup_devcontainer.sh` irá automaticamente:
1. Instalar Isaac Lab
2. Instalar o pacote do workshop
3. Instalar JupyterLab e ferramentas
4. Verificar a instalação

> ⏱️ O setup demora ~10–15 minutos na primeira vez.

---

## Opção B: GitHub Codespaces

> **Para edição de código e estudo dos notebooks.** Simulação completa requer Vast.ai ou NVIDIA Brev.

### ⚠️ Limitação Importante

**Isaac Sim requer RT Cores** (rastreamento de raios em tempo real). O GitHub Codespaces usa GPUs NVIDIA A10G, porém a imagem do Isaac Sim (~40 GB) é muito grande para o startup do Codespaces.

**O que funciona no Codespaces:**
- ✅ Edição e leitura de código
- ✅ Notebooks interativos (modo CPU)
- ✅ Visualização de gráficos e resultados
- ✅ TensorBoard (logs de treinamento pré-gerados)
- ❌ Simulação física com Isaac Sim
- ❌ Treinamento paralelo em GPU

### Passo a Passo

**1. Abrir Codespaces:**

No GitHub, clique em **Code → Codespaces → Create codespace on main**.

**OU** via URL:
```
https://codespaces.new/itamariliuk/isaaclabtutorial
```

**2. Selecionar a configuração:**

Quando perguntado, selecione: **"Workshop Quadrúpede - Edição de Código (Codespaces)"**

**3. Aguardar o setup:**

O script `setup_codespaces.sh` instala Python, PyTorch (CPU), JupyterLab e demais dependências.

> ⏱️ O setup demora ~3–5 minutos.

**4. Abrir os notebooks:**

`Ctrl+Shift+P` → **Tasks: Run Task** → **🚀 JupyterLab (Codespaces)**

Acesse: `http://localhost:8888`

---

## Tarefas Pré-configuradas

Após abrir o projeto no VS Code ou Codespaces, use `Ctrl+Shift+P` → **Tasks: Run Task**:

| Tarefa | Descrição | Ambiente |
|--------|-----------|----------|
| 🚀 Abrir JupyterLab | Abre JupyterLab (Isaac Sim Python) | Local Docker |
| 🚀 JupyterLab (Codespaces) | Abre JupyterLab (Python padrão) | Codespaces |
| 📊 TensorBoard | Monitora métricas de treinamento | Ambos |
| 🤖 Treinar Quadrúpede (4096 envs) | Treinamento completo | Local Docker |
| 🤖 Treinar Quadrúpede (512 envs) | Treino rápido para teste | Local Docker |
| ▶️ Executar Política Treinada | Roda a política salva | Local Docker |
| 🔍 Verificar Instalação | Checa todas as dependências | Local Docker |
| 🛠️ Setup Dev Container | Reinstala dependências | Local Docker |

---

## Estrutura do Devcontainer

```
.devcontainer/
├── isaac-sim-local/
│   └── devcontainer.json    # VS Code Local + Docker (simulação completa)
└── codespaces/
    └── devcontainer.json    # GitHub Codespaces (edição de código)

.vscode/
├── tasks.json               # Tarefas pré-configuradas
├── extensions.json          # Extensões recomendadas
├── settings.json            # Configurações do workspace
└── launch.json              # Configurações de debug

workshop/setup/
├── setup_devcontainer.sh    # Setup para Dev Container local
├── setup_codespaces.sh      # Setup leve para Codespaces
├── setup_vastai.sh          # Setup para Vast.ai
└── setup_brev.sh            # Setup para NVIDIA Brev
```

---

## Limitações e Requisitos de GPU

| Ambiente | GPU Disponível | RT Cores | Isaac Sim | Treinamento |
|----------|---------------|----------|-----------|-------------|
| Vast.ai (RTX 3090) | ✅ NVIDIA RTX 3090 | ✅ Sim | ✅ Completo | ✅ 4096 envs |
| NVIDIA Brev | ✅ Configurável | ✅ Sim | ✅ Completo | ✅ 4096 envs |
| VS Code + Docker Local | ✅ Sua GPU local | Depende | ✅ Se RTX | ✅ Se memória |
| GitHub Codespaces (GPU) | ⚠️ A10G | ✅ Sim | ❌ Imagem grande | ❌ Impraticável |
| GitHub Codespaces (CPU) | ❌ Apenas CPU | ❌ Não | ❌ Não suportado | ❌ Não |

> **Conclusão:** Para o workshop completo, **use Vast.ai ou NVIDIA Brev**. O VS Code com Docker local é uma excelente opção se você tiver uma GPU NVIDIA RTX. O Codespaces é útil apenas para leitura e edição de código.

---

## Extensões VS Code Recomendadas

Quando abrir o projeto, o VS Code irá sugerir instalar as extensões recomendadas. Clique em **"Instalar Tudo"**:

- **Python** + **Pylance** — Suporte completo a Python
- **Jupyter** — Executar notebooks `.ipynb` inline
- **Remote - Containers** — Conectar a Dev Containers
- **Docker** — Gerenciar containers pelo VS Code
- **GitLens** — Visualizar histórico git
- **YAML** — Syntax highlighting para configs
- **Code Spell Checker PT-BR** — Correção ortográfica em português
