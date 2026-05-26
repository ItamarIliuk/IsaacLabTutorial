# NVIDIA Brev Launchable

O **Brev Launchable** permite que qualquer participante abra um ambiente GPU na nuvem, **100% configurado e pronto**, com um único clique — sem instalar nada localmente.

> Este fluxo segue o modelo de uso do repositório [`isaac-launchable`](https://github.com/ItamarIliuk/isaac-launchable): deploy no Brev, aguardar setup automático e abrir serviços via **Secure Links**.

---

## Abrir o Ambiente Agora

[![Abrir no NVIDIA Brev](https://brev.nvidia.com/button.svg)](https://brev.nvidia.com/launchable/deploy?repoUrl=https://github.com/ItamarIliuk/IsaacLabTutorial)

> **Ou acesse diretamente:**
> ```
> https://brev.nvidia.com/launchable/deploy?repoUrl=https://github.com/ItamarIliuk/IsaacLabTutorial
> ```

---

## O que acontece ao clicar?

1. Brev cria uma instância GPU na nuvem com **Isaac Sim 5.1.0** pré-instalado
2. O script `.brev/setup.sh` roda **automaticamente** e:
   - Instala **Isaac Lab** (framework de RL)
   - Clona e instala o **pacote do workshop** (`workshop_quadrupede`)
   - Instala **JupyterLab**, TensorBoard e matplotlib
   - Inicia JupyterLab na porta 8888
   - Inicia TensorBoard na porta 6006
3. Em ~10 minutos, o ambiente está pronto

---

## Configuração do Launchable

### Imagem Docker recomendada

```
nvcr.io/nvidia/isaac-sim:5.1.0
```

Ao criar o Launchable no painel do Brev, configure:

| Parâmetro | Valor |
|-----------|-------|
| **Imagem** | `nvcr.io/nvidia/isaac-sim:5.1.0` |
| **GPU** | RTX 3090 ou RTX 4090 (requer RT Cores) |
| **RAM** | Mínimo 32 GB |
| **Disco** | Mínimo 60 GB |
| **Portas** | 8888, 6006, 49100, 47995 |

### Portas expostas

| Porta | Serviço | Acesso |
|-------|---------|--------|
| `8888` | JupyterLab | `http://localhost:8888` |
| `6006` | TensorBoard | `http://localhost:6006` |
| `49100` | Isaac Sim WebSocket | Streaming 3D |
| `47995` | Omniverse WebRTC | Visualização |

---

## Passo a Passo para Participantes

### 1. Criar conta NVIDIA Brev

Acesse [brev.nvidia.com](https://brev.nvidia.com) e crie uma conta gratuita.

> **Novos usuários ganham créditos gratuitos** para as primeiras horas de GPU.

### 2. Lançar o Launchable

Clique no botão acima ou acesse o link do Launchable.

Na tela de configuração:
- **Nome:** `workshop-quadrupede` (ou qualquer nome)
- **GPU:** Selecione RTX 3090 ou 4090
- **Imagem:** `nvcr.io/nvidia/isaac-sim:5.1.0`
- Clique em **"Deploy"**

### 3. Aguardar o setup automático (~10 min)

O Brev mostrará o log de setup em tempo real. Aguarde a mensagem:

```
✅ Workshop configurado e pronto!
```

### 4. Acessar JupyterLab (Secure Links)

No painel da instância no Brev:
1. Vá até **Using Secure Links**
2. Abra o link da porta **8888** (JupyterLab)

Se preferir via CLI/túnel local:
```bash
brev open workshop-quadrupede
# depois acesse http://localhost:8888
```

### 5. Executar os notebooks

Na interface do JupyterLab, abra os notebooks na ordem:

```
📓 00_setup_ambiente.ipynb      ← Verifique o ambiente
📓 01_introducao_isaac_lab.ipynb
📓 02_ambiente_quadrupede.ipynb
📓 03_treinamento_rsl_rl.ipynb  ← Lance o treinamento aqui
📓 04_resultados.ipynb          ← Visualize o robô andando
```

### 6. Treinar o quadrúpede

Via terminal no JupyterLab (ou via SSH):

```bash
cd ~/workshop
/isaac-sim/python.sh workshop/scripts/treinar.py \
  --task Workshop-Anymal-v0 \
  --headless \
  --num_envs 4096
```

Monitore o progresso no TensorBoard:
```bash
# Acesse: http://localhost:6006
```

### 7. Executar a política treinada

```bash
/isaac-sim/python.sh workshop/scripts/jogar.py \
  --task Workshop-Anymal-v0 \
  --load_run workshop_quadrupede_anymal \
  --num_envs 4
```

---

## Reinicialização Rápida

Uma das grandes vantagens do Brev Launchable é que o ambiente **persiste entre sessões**. Você pode:

- **Pausar** a instância (economiza créditos) e **retomar** quando quiser
- O JupyterLab e TensorBoard **reiniciam automaticamente** com o script `.brev/setup.sh`
- Seus checkpoints de treinamento ficam salvos em `~/workshop/logs/`

### Para reiniciar os serviços manualmente:

```bash
bash ~/workshop/.brev/setup.sh
```

---

## Comparação de Plataformas

| Plataforma | Setup | GPU | Custo estimado | Reinício rápido |
|------------|-------|-----|----------------|----------------|
| **Brev Launchable** | 1 clique ✨ | RTX configurável | ~$0.40/h | ✅ Persistente |
| Vast.ai | Manual (10 min) | RTX marketplace | ~$0.30–0.80/h | ⚠️ Recria container |
| VS Code + Docker | Manual (local) | GPU própria | Custo da GPU | ✅ Local |
| GitHub Codespaces | 1 clique | CPU/A10G | ~$0.18/h | ⚠️ Sem Isaac Sim |

---

## Estrutura do Launchable

```
.brev/
└── setup.sh          ← Executado automaticamente pelo Brev

workshop/
├── notebooks/        ← Abertos no JupyterLab (porta 8888)
├── scripts/
│   ├── treinar.py    ← Treinamento PPO
│   └── jogar.py      ← Inferência da política
└── setup/
    └── setup_brev.sh ← Guia manual alternativo
```

---

## Solução de Problemas

**Setup não completou?**
```bash
cat /tmp/workshop_setup.log
# ou
bash ~/workshop/.brev/setup.sh 2>&1 | tee /tmp/setup_retry.log
```

**JupyterLab não abre?**
```bash
# Verificar se está rodando
ps aux | grep jupyter
# Reiniciar
/isaac-sim/python.sh -m jupyter lab --ip=0.0.0.0 --port=8888 --no-browser \
  --notebook-dir=~/workshop/workshop/notebooks --NotebookApp.token=''
```

**GPU não detectada?**
```bash
nvidia-smi
/isaac-sim/python.sh -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```
