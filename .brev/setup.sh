#!/bin/bash
# =============================================================================
# NVIDIA Brev Launchable - Workshop Quadrúpede com Isaac Lab
# AI Summit Joinville | Isaac Sim 5.1 + RSL-RL + PPO
#
# Este script é executado AUTOMATICAMENTE quando o ambiente Brev é criado.
# Não é necessário rodá-lo manualmente.
# =============================================================================
set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${BLUE}[BREV]${NC} $1"; }
ok()   { echo -e "${GREEN}[OK]${NC}   $1"; }
warn() { echo -e "${YELLOW}[AVISO]${NC} $1"; }

echo ""
echo "=========================================================="
echo "   Workshop Quadrúpede - NVIDIA Brev Launchable"
echo "   AI Summit Joinville | Isaac Sim 5.1 + RSL-RL"
echo "=========================================================="
echo ""

ISAAC_PATH="/isaac-sim"
WORKSHOP_REPO="https://github.com/ItamarIliuk/IsaacLabTutorial.git"
WORKSHOP_BRANCH="main"
WORKSHOP_DIR="${HOME}/workshop"
LOGS_DIR="${HOME}/logs"
JUPYTER_PORT=8888
TENSORBOARD_PORT=6006

# ---------------------------------------------------------------------------
# 1. Verificar GPU
# ---------------------------------------------------------------------------
log "[1/6] Verificando GPU..."
if ! command -v nvidia-smi &> /dev/null; then
  warn "nvidia-smi não encontrado. Verifique se a instância tem GPU."
else
  GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
  GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader | head -1)
  ok "GPU: ${GPU_NAME} (${GPU_MEM})"
fi

# ---------------------------------------------------------------------------
# 2. Verificar Isaac Sim
# ---------------------------------------------------------------------------
log "[2/6] Verificando Isaac Sim..."
if [ ! -d "${ISAAC_PATH}" ]; then
  warn "Isaac Sim não encontrado em ${ISAAC_PATH}."
  warn "Certifique-se de usar a imagem: nvcr.io/nvidia/isaac-sim:5.1.0"
  warn "Veja: workshop/BREV_LAUNCHABLE.md para instruções."
  exit 1
fi
ok "Isaac Sim encontrado em ${ISAAC_PATH}"

# ---------------------------------------------------------------------------
# 3. Instalar Isaac Lab
# ---------------------------------------------------------------------------
log "[3/6] Instalando Isaac Lab..."
cd "${ISAAC_PATH}"
if [ ! -d "IsaacLab" ]; then
  log "   Clonando Isaac Lab (pode levar alguns minutos)..."
  git clone --depth=1 https://github.com/isaac-sim/IsaacLab.git IsaacLab
else
  log "   Isaac Lab já existe — atualizando..."
  cd IsaacLab && git pull --ff-only 2>/dev/null || true && cd ..
fi

cd "${ISAAC_PATH}/IsaacLab"
log "   Instalando pacotes Isaac Lab..."
"${ISAAC_PATH}/python.sh" -m pip install --quiet -e source/isaaclab
"${ISAAC_PATH}/python.sh" -m pip install --quiet -e source/isaaclab_tasks
"${ISAAC_PATH}/python.sh" -m pip install --quiet -e source/isaaclab_rl
ok "Isaac Lab instalado"

# ---------------------------------------------------------------------------
# 4. Clonar e instalar workshop
# ---------------------------------------------------------------------------
log "[4/6] Configurando workshop..."
if [ ! -d "${WORKSHOP_DIR}" ]; then
  log "   Clonando repositório do workshop..."
  git clone --depth=1 --branch="${WORKSHOP_BRANCH}" "${WORKSHOP_REPO}" "${WORKSHOP_DIR}"
else
  log "   Workshop já existe — atualizando..."
  cd "${WORKSHOP_DIR}" && git pull --ff-only 2>/dev/null || true
fi

cd "${WORKSHOP_DIR}"
"${ISAAC_PATH}/python.sh" -m pip install --quiet -e workshop/source/
ok "Pacote workshop_quadrupede instalado"

# ---------------------------------------------------------------------------
# 5. Instalar ferramentas adicionais
# ---------------------------------------------------------------------------
log "[5/6] Instalando ferramentas de desenvolvimento..."
"${ISAAC_PATH}/python.sh" -m pip install --quiet \
  jupyterlab \
  matplotlib \
  tensorboard \
  ipywidgets \
  notebook
ok "JupyterLab, TensorBoard e matplotlib instalados"

# ---------------------------------------------------------------------------
# 6. Configurar e iniciar serviços
# ---------------------------------------------------------------------------
log "[6/6] Iniciando serviços..."
mkdir -p "${LOGS_DIR}"

# JupyterLab (background)
"${ISAAC_PATH}/python.sh" -m jupyter lab \
  --ip=0.0.0.0 \
  --port=${JUPYTER_PORT} \
  --no-browser \
  --notebook-dir="${WORKSHOP_DIR}/workshop/notebooks" \
  --NotebookApp.token='' \
  --NotebookApp.password='' \
  > "${LOGS_DIR}/jupyter.log" 2>&1 &
JUPYTER_PID=$!
ok "JupyterLab iniciado (PID ${JUPYTER_PID}) → porta ${JUPYTER_PORT}"

# TensorBoard (background)
tensorboard \
  --logdir="${WORKSHOP_DIR}/logs" \
  --host=0.0.0.0 \
  --port=${TENSORBOARD_PORT} \
  > "${LOGS_DIR}/tensorboard.log" 2>&1 &
TB_PID=$!
ok "TensorBoard iniciado (PID ${TB_PID}) → porta ${TENSORBOARD_PORT}"

# ---------------------------------------------------------------------------
# Verificação final
# ---------------------------------------------------------------------------
echo ""
log "Verificação final do ambiente..."
"${ISAAC_PATH}/python.sh" -c "
import sys, torch
print(f'   Python:          {sys.version.split()[0]}')
print(f'   PyTorch:         {torch.__version__}')
print(f'   CUDA disponível: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'   GPU:             {torch.cuda.get_device_name(0)}')
try:
    import omni.isaac.lab; print('   Isaac Lab:       OK')
except: print('   Isaac Lab:       ERRO')
try:
    import workshop_quadrupede; print('   workshop_quadru: OK')
except: print('   workshop_quadru: ERRO')
"

echo ""
echo "=========================================================="
echo "   ✅ Workshop configurado e pronto!"
echo "=========================================================="
echo ""
echo "   📓 JupyterLab:   http://localhost:${JUPYTER_PORT}"
echo "   📊 TensorBoard:  http://localhost:${TENSORBOARD_PORT}"
echo ""
echo "   Para treinar:"
echo "   cd ${WORKSHOP_DIR}"
echo "   ${ISAAC_PATH}/python.sh workshop/scripts/treinar.py \\"
echo "     --task Workshop-Anymal-v0 --headless --num_envs 4096"
echo ""
echo "   Logs em: ${LOGS_DIR}/"
echo "=========================================================="
