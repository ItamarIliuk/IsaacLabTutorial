# NVIDIA Brev Launchable

O **Brev Launchable** permite que qualquer participante abra um ambiente GPU na nuvem com Isaac Lab pré-instalado, VS Code no browser e streaming do Isaac Sim — **tudo com um único clique**, sem instalar nada localmente.

> Este fluxo usa o [`isaac-launchable`](https://github.com/ItamarIliuk/isaac-launchable) como ambiente base: Isaac Lab 2.3 + Isaac Sim 5.1 rodando em containers Docker, acessíveis via VS Code no browser.

---

## 1. Abrir o Ambiente

[![Abrir no NVIDIA Brev](https://brev-assets.s3.us-west-1.amazonaws.com/nv-lb-dark.svg)](https://brev.nvidia.com/launchable/deploy/now?launchableID=env-35JP2ywERLgqtD0b0MIeK1HnF46)

> **Ou acesse diretamente:**
> ```
> https://brev.nvidia.com/launchable/deploy/now?launchableID=env-35JP2ywERLgqtD0b0MIeK1HnF46
> ```

---

## 2. O que sobe automaticamente

Ao clicar em **Deploy**, o Brev provisiona a instância GPU e inicia 3 containers:

| Container | Função | Acesso |
|-----------|--------|--------|
| `vscode` | VS Code no browser (editor + terminal) | URL principal (porta 80) |
| `web-viewer` | Streaming do Isaac Sim | `<sua-url>/viewer` |
| `nginx` | Proxy reverso / Secure Links | — |

> **Tempo de setup:** ~5–10 min na primeira vez (download das imagens Docker).

---

## 3. Passo a Passo para Participantes

### Passo 1 — Criar conta NVIDIA Brev

Acesse [brev.nvidia.com](https://brev.nvidia.com) e crie uma conta gratuita.

> **Novos usuários ganham créditos** para as primeiras horas de GPU.

---

### Passo 2 — Fazer o deploy do Launchable

Clique no botão acima. Na página do Brev:

1. Clique em **"Deploy Launchable"**
2. Aguarde a instância ficar com status **Running** e o setup concluir

---

### Passo 3 — Acessar o VS Code no browser

Na página da instância no Brev:

1. Vá até a seção **"Using Secure Links"**
2. Clique na seta ao lado do link chamado **"isaac"**
3. Faça login com sua conta NVIDIA Brev
4. O VS Code abrirá no browser — pronto para usar

---

### Passo 4 — Clonar o repositório do workshop

Dentro do VS Code, abra um terminal (`Ctrl+` `` ` ``) e execute:

```bash
cd /workspace
git clone https://github.com/ItamarIliuk/IsaacLabTutorial.git
cd IsaacLabTutorial
```

Em seguida, instale o pacote do workshop:

```bash
/workspace/isaaclab/isaaclab.sh -p -m pip install -e workshop/source/
```

---

### Passo 5 — Abrir os notebooks

No explorador de arquivos do VS Code, navegue até:

```
/workspace/IsaacLabTutorial/workshop/notebooks/
```

Abra os notebooks em ordem clicando diretamente nos arquivos `.ipynb`:

```
📓 00_setup_ambiente.ipynb      ← Verifique o ambiente
📓 01_introducao_isaac_lab.ipynb
📓 02_ambiente_quadrupede.ipynb
📓 03_treinamento_rsl_rl.ipynb  ← Configure e lance o treinamento
📓 04_resultados.ipynb          ← Analise as curvas de aprendizado
```

---

### Passo 6 — Treinar o quadrúpede

No terminal do VS Code:

```bash
cd /workspace/IsaacLabTutorial
/workspace/isaaclab/isaaclab.sh -p workshop/scripts/treinar.py \
  --task Workshop-Anymal-v0 \
  --headless \
  --num_envs 4096
```

> Use `--num_envs 512` para um teste mais rápido durante o workshop.

---

### Passo 7 — Visualizar a política treinada

Para ver o robô andando com streaming no browser:

```bash
/workspace/isaaclab/isaaclab.sh -p workshop/scripts/jogar.py \
  --task Workshop-Anymal-v0 \
  --load_run workshop_quadrupede_anymal \
  --num_envs 4 \
  --livestream 2
```

Quando aparecer `Simulation App Startup Complete` no terminal:

1. Abra uma nova aba no browser
2. Cole a mesma URL do VS Code, trocando o final por `/viewer`
   - Exemplo: `https://isaac.brevlab-1234/viewer`
3. Aguarde o stream iniciar (a página mostrará "Waiting for stream...")

---

## Reinicialização Rápida

O ambiente **persiste entre sessões** — pause a instância para economizar créditos e retome quando quiser. Os checkpoints de treinamento ficam salvos em:

```
/workspace/IsaacLabTutorial/logs/workshop_quadrupede_anymal/
```

Se os containers pararem, reinicie com:

```bash
cd /workspace/isaac-launchable/isaac-lab
docker compose up -d
```

---

## Comparação de Plataformas

| Plataforma | Setup | Interface | Custo estimado | Reinício rápido |
|------------|-------|-----------|----------------|-----------------|
| **Brev Launchable** | 1 clique ✨ | VS Code + viewer no browser | ~$0.40–0.80/h | ✅ Persistente |
| Vast.ai | ~10 min manual | Terminal / JupyterLab | ~$0.30–0.80/h | ⚠️ Recria container |
| VS Code + Docker local | Pré-download (~40 GB) | VS Code local | Custo da GPU | ✅ Local |
| GitHub Codespaces | 1 clique | VS Code no browser | ~$0.18/h | ⚠️ Sem Isaac Sim |

---

## Solução de Problemas

**Containers não inicializaram?**
```bash
# Ver status dos containers
docker ps

# Reiniciar tudo
cd /workspace/isaac-launchable/isaac-lab
docker compose down && docker compose up -d
```

**Viewer mostra "Waiting for stream..." por muito tempo?**
- Aguarde o terminal mostrar `Simulation App Startup Complete`
- Atualize a aba do viewer (F5)
- Verifique se o container `web-viewer` está ativo: `docker ps | grep viewer`

**Pacote workshop não encontrado?**
```bash
cd /workspace/IsaacLabTutorial
/workspace/isaaclab/isaaclab.sh -p -m pip install -e workshop/source/
/workspace/isaaclab/isaaclab.sh -p -c "import workshop_quadrupede; print('OK')"
```

**GPU não detectada?**
```bash
nvidia-smi
/workspace/isaaclab/isaaclab.sh -p -c "import torch; print(torch.cuda.is_available())"
```
