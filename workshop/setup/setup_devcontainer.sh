#!/bin/bash
# Setup para VS Code Dev Container (imagem Isaac Sim já presente)
set -e

WORKSPACE="${CONTAINER_WORKSPACE_FOLDER:-/workspaces/isaaclabtutorial}"
ISAAC_PATH="/isaac-sim"

echo "=================================================="
echo "  Workshop Quadrúpede - Setup Dev Container"
echo "  Isaac Sim: ${ISAAC_PATH}"
echo "  Workspace: ${WORKSPACE}"
echo "=================================================="

# 1. Instalar Isaac Lab
echo ""
echo "📦 [1/4] Instalando Isaac Lab..."
cd "${ISAAC_PATH}"
if [ ! -d "IsaacLab" ]; then
  git clone --depth=1 https://github.com/isaac-sim/IsaacLab.git IsaacLab
fi
cd IsaacLab
"${ISAAC_PATH}/python.sh" -m pip install --quiet -e source/isaaclab
"${ISAAC_PATH}/python.sh" -m pip install --quiet -e source/isaaclab_tasks
"${ISAAC_PATH}/python.sh" -m pip install --quiet -e source/isaaclab_rl
echo "   ✅ Isaac Lab instalado"

# 2. Instalar pacote do workshop
echo ""
echo "🤖 [2/4] Instalando pacote do workshop..."
cd "${WORKSPACE}"
"${ISAAC_PATH}/python.sh" -m pip install --quiet -e workshop/source/
echo "   ✅ workshop_quadrupede instalado"

# 3. Instalar ferramentas de dev
echo ""
echo "🛠️  [3/4] Instalando ferramentas de desenvolvimento..."
"${ISAAC_PATH}/python.sh" -m pip install --quiet jupyterlab matplotlib tensorboard ipywidgets
echo "   ✅ JupyterLab + TensorBoard instalados"

# 4. Verificação final
echo ""
echo "🔍 [4/4] Verificação final..."
"${ISAAC_PATH}/python.sh" -c "
import torch
print(f'   PyTorch: {torch.__version__}')
print(f'   CUDA disponível: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'   GPU: {torch.cuda.get_device_name(0)}')
try:
    import omni.isaac.lab
    print('   Isaac Lab: OK')
except Exception as e:
    print(f'   Isaac Lab: ERRO - {e}')
try:
    import workshop_quadrupede
    print('   workshop_quadrupede: OK')
except Exception as e:
    print(f'   workshop_quadrupede: ERRO - {e}')
"

echo ""
echo "================================================"
echo "  ✅ Dev Container configurado com sucesso!"
echo "================================================"
echo ""
echo "Próximos passos:"
echo "  Ctrl+Shift+P → 'Tasks: Run Task' → '🚀 Abrir JupyterLab'"
echo "  Acesse: http://localhost:8888"
echo ""
echo "Para treinar: Ctrl+Shift+P → 'Tasks: Run Task' → '🤖 Treinar Quadrúpede'"
