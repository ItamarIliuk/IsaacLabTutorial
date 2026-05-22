#!/bin/bash
# =============================================================================
# Setup Comum — Workshop NVIDIA Isaac Lab
# Execute dentro do container Isaac Sim após ter o ambiente rodando
# =============================================================================

set -e

ISAAC_PYTHON="/isaac-sim/python.sh"
WORKSHOP_ROOT="/root/IsaacLabTutorial"
ISAAC_LAB_PATH="/root/IsaacLab"

echo "================================================"
echo " Workshop Isaac Lab — Setup Comum"
echo "================================================"

# 1. Verificar ambiente
echo "\n[1/4] Verificando ambiente..."
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
$ISAAC_PYTHON --version
echo "Isaac Sim Python: OK"

# 2. Instalar/verificar Isaac Lab
echo "\n[2/4] Verificando Isaac Lab..."
if ! $ISAAC_PYTHON -c "import isaaclab" 2>/dev/null; then
    echo "Instalando Isaac Lab..."
    [ ! -d "$ISAAC_LAB_PATH" ] && git clone --depth=1 https://github.com/isaac-sim/IsaacLab.git $ISAAC_LAB_PATH
    cd $ISAAC_LAB_PATH
    ln -sfn /isaac-sim _isaac_sim 2>/dev/null || true
    $ISAAC_PYTHON -m pip install -e source/isaaclab source/isaaclab_tasks -q
    echo "Isaac Lab instalado!"
else
    echo "Isaac Lab: OK"
fi

# 3. Instalar pacote do workshop
echo "\n[3/4] Instalando pacote do workshop..."
[ ! -d "$WORKSHOP_ROOT" ] && git clone https://github.com/ItamarIliuk/IsaacLabTutorial.git $WORKSHOP_ROOT
cd $WORKSHOP_ROOT
git checkout claude/nvidia-isaac-workshop-repo-YufRK 2>/dev/null || git pull origin claude/nvidia-isaac-workshop-repo-YufRK
$ISAAC_PYTHON -m pip install -e workshop/source/workshop_quadrupede -q
echo "Pacote workshop: OK"

# 4. Instalar ferramentas de análise
echo "\n[4/4] Instalando ferramentas..."
$ISAAC_PYTHON -m pip install jupyterlab matplotlib tensorboard -q
echo "Ferramentas: OK"

# Verificação final
echo ""
$ISAAC_PYTHON -c "
import torch
import isaaclab
import workshop_quadrupede
print(f'PyTorch: {torch.__version__}')
print(f'CUDA: {torch.cuda.is_available()} — {torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A"}')
print('Isaac Lab: OK')
print('Workshop Quadrupede: OK')
"

echo ""
echo "================================================"
echo " Tudo pronto! Inicie o JupyterLab com:"
echo "================================================"
echo ""
echo "  cd $WORKSHOP_ROOT"
echo "  $ISAAC_PYTHON -m jupyter lab \\"
echo "    --ip=0.0.0.0 --port=8888 --no-browser \\"
echo "    --notebook-dir=workshop/notebooks"
echo ""
echo "  Abra: workshop/notebooks/00_setup_ambiente.ipynb"
echo "================================================"
