#!/bin/bash
# =============================================================================
# Setup NVIDIA Brev — Workshop NVIDIA Isaac Lab
# Summit de IA — Joinville, SC, 2026
# =============================================================================
#
# PASSO A PASSO:
#
# 1. Crie conta em https://brev.dev
# 2. Instale o CLI Brev:
#    Mac:   brew install brevdev/homebrew-brev/brev
#    Linux: curl -fsSL https://raw.githubusercontent.com/brevdev/brev-cli/main/install.sh | bash
#
# 3. Faça login:
#    brev login
#
# 4. Crie um ambiente com GPU:
#    brev create workshop-isaaclab --gpu A10G
#    (alternativas: RTX4090, A6000, L40S)
#
# 5. Conecte ao ambiente:
#    brev shell workshop-isaaclab
#
# 6. Execute este script dentro do ambiente:
#    bash setup_brev.sh
# =============================================================================

set -e

echo "================================================"
echo " Workshop Isaac Lab — Setup NVIDIA Brev"
echo "================================================"

# Verificar GPU
echo "\n[1/6] Verificando GPU..."
nvidia-smi || { echo "ERRO: GPU não detectada. Configure GPU no Brev."; exit 1; }

# Instalar Docker (se necessário)
echo "\n[2/6] Verificando Docker..."
if ! command -v docker &>/dev/null; then
    echo "Instalando Docker..."
    curl -fsSL https://get.docker.com | bash
    sudo usermod -aG docker $USER
    newgrp docker
fi
docker --version

# Configurar NVIDIA Container Toolkit
echo "\n[3/6] Configurando NVIDIA Container Toolkit..."
if ! dpkg -l | grep -q nvidia-container-toolkit; then
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L "https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list" | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    sudo apt-get update -q
    sudo apt-get install -y nvidia-container-toolkit
    sudo nvidia-ctk runtime configure --runtime=docker
    sudo systemctl restart docker
fi
echo "NVIDIA Container Toolkit: OK"

# Pull Isaac Sim container
echo "\n[4/6] Baixando Isaac Sim 5.1 (pode levar 20-30 min)..."
docker pull nvcr.io/nvidia/isaac-sim:5.1.0

# Iniciar container e instalar Isaac Lab
echo "\n[5/6] Instalando Isaac Lab no container..."
mkdir -p $HOME/workshop_data

docker run --rm --gpus all \
    -v $HOME/workshop_data:/root/data \
    nvcr.io/nvidia/isaac-sim:5.1.0 \
    bash -c "
        git clone --depth=1 https://github.com/isaac-sim/IsaacLab.git /root/IsaacLab && \
        cd /root/IsaacLab && ln -sfn /isaac-sim _isaac_sim && \
        /isaac-sim/python.sh -m pip install -e source/isaaclab source/isaaclab_tasks -q && \
        git clone https://github.com/ItamarIliuk/IsaacLabTutorial.git /root/IsaacLabTutorial && \
        cd /root/IsaacLabTutorial && git checkout claude/nvidia-isaac-workshop-repo-YufRK && \
        /isaac-sim/python.sh -m pip install -e workshop/source/workshop_quadrupede -q
    "

# Script de inicialização do workshop
echo "\n[6/6] Criando script de inicialização..."
cat > $HOME/iniciar_workshop.sh << 'EOF'
#!/bin/bash
docker run -it --rm --gpus all \
    -p 8888:8888 \
    -p 6006:6006 \
    -p 47995-48012:47995-48012/udp \
    -p 47995-48012:47995-48012/tcp \
    -p 49100:49100 \
    -v $HOME/workshop_data:/root/data \
    -e ACCEPT_EULA=Y \
    -e PRIVACY_CONSENT=Y \
    nvcr.io/nvidia/isaac-sim:5.1.0 \
    bash -c "
        /isaac-sim/python.sh -m jupyter lab \
            --ip=0.0.0.0 --port=8888 --no-browser \
            --notebook-dir=/root/IsaacLabTutorial/workshop/notebooks
    "
EOF
chmod +x $HOME/iniciar_workshop.sh

echo ""
echo "================================================"
echo " Setup concluído!"
echo "================================================"
echo ""
echo "  Para iniciar o workshop:"
echo "  bash ~/iniciar_workshop.sh"
echo ""
echo "  Acesse: http://localhost:8888"
echo "================================================"
