#!/bin/bash
# =============================================================================
# Setup Vast.ai — Workshop NVIDIA Isaac Lab
# Summit de IA — Joinville, SC, 2026
# =============================================================================
#
# PASSO A PASSO (execute no seu computador / siga no navegador):
#
# 1. Crie conta em https://cloud.vast.ai
# 2. Adicione crédito (mínimo $5 — suficiente para 8-10h de RTX 3090)
# 3. Em "Search" → filtre por:
#    - GPU: RTX 3090 ou RTX 4090
#    - VRAM: 24+ GB
#    - RAM: 32+ GB
#    - Storage: 100+ GB
#    - Image: "pytorch/pytorch" ou "nvidia/cuda:12.1.0-devel-ubuntu22.04"
# 4. Em "Edit Image & Config", defina:
#    - Docker image: nvcr.io/nvidia/isaac-sim:5.1.0
#    - Expose ports: 22 8888 47995 47996 49100
# 5. Clique "Rent"
# 6. Vá em "Instances" e aguarde ficar "Running"
# 7. Clique em "Connect" e copie o comando SSH
#
# Após conectar via SSH, execute este script:
# =============================================================================

set -e

echo "================================================"
echo " Workshop Isaac Lab — Setup Vast.ai"
echo "================================================"

# Verificar GPU
echo "\n[1/5] Verificando GPU..."
nvidia-smi

# Verificar Isaac Sim
echo "\n[2/5] Verificando Isaac Sim..."
if [ -d "/isaac-sim" ]; then
    echo "Isaac Sim encontrado em /isaac-sim"
    ls /isaac-sim/python.sh 2>/dev/null && echo "Python runtime: OK" || echo "AVISO: python.sh não encontrado"
else
    echo "ERRO: Isaac Sim não encontrado em /isaac-sim"
    echo "Certifique-se de usar a imagem nvcr.io/nvidia/isaac-sim:5.1.0"
    exit 1
fi

# Instalar Isaac Lab
echo "\n[3/5] Instalando Isaac Lab..."
if [ ! -d "/root/IsaacLab" ]; then
    git clone --depth=1 https://github.com/isaac-sim/IsaacLab.git /root/IsaacLab
fi

cd /root/IsaacLab
ln -sfn /isaac-sim _isaac_sim 2>/dev/null || true

/isaac-sim/python.sh -m pip install --upgrade pip setuptools wheel -q
for pkg in source/isaaclab source/isaaclab_tasks source/isaaclab_mimic; do
    [ -d "$pkg" ] && /isaac-sim/python.sh -m pip install -e "$pkg" -q
done

echo "Isaac Lab instalado!"

# Clonar workshop
echo "\n[4/5] Configurando repositório do workshop..."
if [ ! -d "/root/IsaacLabTutorial" ]; then
    git clone https://github.com/ItamarIliuk/IsaacLabTutorial.git /root/IsaacLabTutorial
fi

cd /root/IsaacLabTutorial
git checkout claude/nvidia-isaac-workshop-repo-YufRK 2>/dev/null || true

# Instalar pacote do workshop
/isaac-sim/python.sh -m pip install -e workshop/source/workshop_quadrupede -q
echo "Pacote workshop instalado!"

# Configurar JupyterLab
echo "\n[5/5] Configurando JupyterLab..."
/isaac-sim/python.sh -m pip install jupyterlab -q

echo ""
echo "================================================"
echo " Setup concluído! Para iniciar o workshop:"
echo "================================================"
echo ""
echo "  cd /root/IsaacLabTutorial"
echo "  /isaac-sim/python.sh -m jupyter lab \\"
echo "    --ip=0.0.0.0 --port=8888 --no-browser \\"
echo "    --notebook-dir=workshop/notebooks"
echo ""
echo "  Acesse: http://$(curl -s ifconfig.me 2>/dev/null || echo 'SEU_IP'):8888"
echo "================================================"
