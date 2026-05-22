#!/bin/bash
# Setup leve para GitHub Codespaces (sem Isaac Sim completo)
set -e

WORKSPACE="${CONTAINER_WORKSPACE_FOLDER:-/workspaces/isaaclabtutorial}"

echo "=================================================="
echo "  Workshop Quadrúpede - Setup GitHub Codespaces"
echo "  Modo: Edição de Código + Notebooks (sem simulação)"
echo "=================================================="
echo ""
echo "⚠️  GitHub Codespaces NÃO suporta Isaac Sim completo."
echo "   Use Vast.ai ou NVIDIA Brev para simulação + treinamento."
echo ""

# 1. Instalar dependências Python
echo "📦 [1/3] Instalando dependências Python..."
pip install --quiet --upgrade pip
pip install --quiet \
  torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install --quiet \
  jupyterlab \
  matplotlib \
  tensorboard \
  numpy \
  scipy \
  gymnasium \
  ipywidgets \
  ipython
echo "   ✅ Dependências instaladas"

# 2. Instalar stubs do pacote workshop
echo ""
echo "🤖 [2/3] Instalando pacote workshop (modo stub)..."
cd "${WORKSPACE}"

# Cria stubs do Isaac Lab para que o código possa ser importado sem a simulação
pip install --quiet -e workshop/source/ 2>/dev/null || echo "   ⚠️  Instalação parcial (esperado sem Isaac Sim)"
echo "   ✅ Pacote workshop carregado"

# 3. Configurar JupyterLab
echo ""
echo "🛠️  [3/3] Configurando JupyterLab..."
jupyter lab --generate-config -y > /dev/null 2>&1 || true
python3 -c "print('   Python:', __import__('sys').version.split()[0])"
python3 -c "import torch; print('   PyTorch:', torch.__version__, '(CPU mode)')"
python3 -c "import jupyterlab; print('   JupyterLab:', jupyterlab.__version__)"

echo ""
echo "================================================"
echo "  ✅ Codespaces configurado!"
echo "================================================"
echo ""
echo "Para abrir os notebooks:"
echo "  Ctrl+Shift+P → 'Tasks: Run Task' → '🚀 JupyterLab (Codespaces)'"
echo "  OU clique diretamente nos arquivos .ipynb no explorador"
echo ""
echo "Para simulação completa, use Vast.ai ou NVIDIA Brev."
echo "Veja: workshop/VSCODE_CODESPACES.md"
