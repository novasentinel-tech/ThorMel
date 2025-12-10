# ❓ FAQ & TROUBLESHOOTING - Dúvidas e Soluções

Respostas para as perguntas mais comuns!

---

## 🆘 PROBLEMAS COMUNS

### ❌ "ModuleNotFoundError: No module named..."

**Problema**: Sistema não encontra dependências.

**Solução**:
```bash
# 1. Ativar ambiente
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Validar
python scripts/validate_system.py
```

---

### ❌ "command not found: python"

**Problema**: Python não encontrado.

**Solução**:
```bash
# Tentar estas variações
python3 scripts/run_single_scan.py google.com
# OU
/usr/bin/python3 scripts/run_single_scan.py google.com
# OU
which python  # descobre onde está
```

---

### ❌ "Permission denied"

**Problema**: Não tem permissão para executar.

**Solução**:
```bash
# Dar permissão
chmod +x scripts/*.py

# Ou usar python diretamente
python scripts/run_single_scan.py google.com
```

---

### ❌ "ConnectionError" ou "Timeout"

**Problema**: Não consegue conectar ao domínio.

**Solução**:
```bash
# 1. Verificar internet
ping google.com

# 2. Tentar outro domínio
python scripts/run_single_scan.py github.com

# 3. Aumentar timeout (editar script e aumentar valor)
# Se persistir: seu internet está ruim OU domínio está offline
```

---

### ❌ "ModuleNotFoundError: No module named 'torch'"

**Problema**: PyTorch não instalado (para RL).

**Solução**:
```bash
# Instalar PyTorch (com CPU)
pip install torch==2.0.0

# OU com GPU (NVIDIA)
pip install torch==2.0.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Depois validar
python scripts/validate_system.py
```

---

### ❌ "Model not found in checkpoints/"

**Problema**: Modelo não foi treinado ainda.

**Solução**:
```bash
# 1. Treinar modelo primeiro
python scripts/train_phase_c.py

# 2. Treinar RL
python scripts/train_phase_d_rl.py --episodes 500

# 3. Agora usar
python scripts/inference_phase_d_rl.py google.com
```

---

### ❌ "Já existe arquivo X.pkl"

**Problema**: Tentando treinar mas modelo já existe.

**Solução**:
```bash
# Opção 1: Deletar arquivo antigo
rm -f models/lightgbm_model.pkl

# Opção 2: Treinar com output diferente
python scripts/train_phase_c.py --output-model models/modelo_novo.pkl
```

---

### ❌ "Out of memory" (OOM)

**Problema**: Computador não tem RAM suficiente.

**Solução**:
```bash
# 1. Usar versão FAST
python scripts/train_phase_c_fast.py

# 2. Escanear menos domínios por vez
python scripts/run_single_scan.py google.com  # Não em batch

# 3. Fechar outros programas
# 4. Se persistir: seu computador é fraco (veja hardware necessário em README.md)
```

---

### ❌ "CUDA/GPU not found"

**Problema**: Quer usar GPU mas não encontra.

**Solução**:
```bash
# Verificar se tem GPU NVIDIA
nvidia-smi

# Se não tiver saída: sem GPU, use CPU
python scripts/train_phase_d_rl.py  # (sem --cuda)

# Se tiver GPU:
python scripts/train_phase_d_rl.py --cuda
```

---

### ❌ "Arquivo sites.txt não encontrado"

**Problema**: Batch scan não acha arquivo.

**Solução**:
```bash
# 1. Verificar arquivo existe
ls -la sites.txt

# 2. Criar arquivo se não existir
cat > sites.txt << 'EOF'
google.com
github.com
stackoverflow.com
EOF

# 3. Executar
python scripts/run_phase_a_scan.py sites.txt
```

---

## ❓ PERGUNTAS FREQUENTES

### P1: Como faço pra escanear meu site?

**R**: Simples! Execute:
```bash
python scripts/run_single_scan.py seu-dominio.com
```

Resultado:
- ✅ "benign" = seguro
- ⚠️ "suspicious" = cuidado
- ❌ "malicious" = perigo!

---

### P2: Quanto tempo leva?

**R**: Depende de seu computador:

| CPU | Tempo |
|-----|-------|
| 2-core antigo | 25-45 segundos |
| 4-core comum | 10-15 segundos |
| 8-core moderno | 4-8 segundos |
| GPU NVIDIA | 2-5 segundos |

---

### P3: Precisa internet?

**R**: **SIM**, ele analisa o site de verdade. Sem internet não funciona.

```bash
# Com internet: ✅ Funciona
python scripts/run_single_scan.py google.com

# Sem internet: ❌ Erro
# Conecte na rede!
```

---

### P4: Precisa de GPU?

**R**: **NÃO**, mas é muito mais rápido com GPU.

```bash
# Sem GPU (CPU): 10-40 segundos
python scripts/train_phase_c.py

# Com GPU: 2-5 segundos
python scripts/train_phase_d_rl.py --cuda
```

---

### P5: Consigo usar meus próprios dados para treinar?

**R**: **SIM!** Veja o cenário 8 em EXEMPLOS_PRATICOS.md:

```bash
python scripts/train_phase_c.py --data-file meus_dados.csv
```

---

### P6: O que significam os números de "confidence"?

**R**: 0-100%, quanto maior = mais certeza

```
85%+ = Altamente confiável
70-85% = Confiável
50-70% = Regular
<50% = Baixa confiança
```

---

### P7: Qual é a acurácia do sistema?

**R**: **~95%** em domínios normais. Varia por categoria:

```
Por categoria:
- Benign: 97% acurácia
- Suspicious: 91% acurácia
- Malicious: 96% acurácia
- Dangerous: 94% acurácia

Usa: LightGBM + Ensemble de features
```

---

### P8: Posso escanear dominios banidos/bloqueados?

**R**: **NÃO**, por segurança e ética. Sistema bloqueia:

```
Bloqueado:
- Domínios .gov.br, .mil, .mil.br
- Sites de bancos oficiais
- Serviços críticos (CISA list)
- Domínios na blacklist
```

Se tentar: Erro "Domain is blocked for academic/safety reasons"

---

### P9: Meu resultado não salva em arquivo, por quê?

**R**: Resultado fica na tela (stdout). Salve assim:

```bash
# Opção 1: Redirecionar para arquivo
python scripts/run_single_scan.py google.com > resultado.txt

# Opção 2: Usar --output-html flag
python scripts/run_single_scan.py google.com --output-html relatorio.html

# Opção 3: Usar --json flag
python scripts/run_phase_a_scan.py sites.txt --json > resultado.json
```

---

### P10: Como faço backup do modelo treinado?

**R**: Copie a pasta checkpoints:

```bash
# Backup
cp -r checkpoints checkpoints_backup_$(date +%Y%m%d)

# Restaurar se perder
cp -r checkpoints_backup_20260227 checkpoints
```

---

### P11: Consigo rodar múltiplas análises ao mesmo tempo?

**R**: **NÃO recomendado**, mas é possível:

```bash
# Ruim (compete por recursos):
python scripts/run_single_scan.py google.com &
python scripts/run_single_scan.py github.com &

# Bom (sequencial):
python scripts/run_phase_a_scan.py sites.txt

# Melhor (paralelo via batch):
# Editar run_phase_a_scan.py com ProcessPool
```

---

### P12: Posso usar em PRODUÇÃO?

**R**: **CUIDADO!** Sistema é para:
- ✅ Análise e pesquisa
- ✅ Teste de segurança
- ✅ Aprendizado
- ✅ Uso acadêmico

**NÃO para**:
- ❌ Ataques automatizados
- ❌ Scanning malicioso
- ❌ Violar leis

Se usar em produção: Respeite a Lei e ética!

---

### P13: Dá pra modificar o código?

**R**: **SIM**, é Open Source! Mas:

```bash
# Antes de modificar, fazer backup
git init
git add .
git commit -m "backup antes de editar"

# Depois editar
# Depois testar
python scripts/validate_system.py

# Depois commitar
git commit -m "minha mudança"
```

---

### P14: Onde vejo os relatórios HTML?

**R**: Em `data/reports/`:

```bash
# Ver arquivos
ls -la data/reports/

# Abrir no navegador
open data/reports/example_com_report.html  # Mac
xdg-open data/reports/example_com_report.html  # Linux
start data/reports/example_com_report.html  # Windows
```

---

### P15: Posso usar em Docker / nuvem?

**R**: **SIM!** Veja sugestões em README.md:

```bash
# Rápida verificação: Docker
docker run -it python:3.9 bash
# Aí instala requirements.txt

# Melhor: criar Dockerfile próprio
# Veja exemplos em docs/
```

---

## 🔧 CHECKLIST: Se Algo Não Funciona

- [ ] Ativa ambiente? `source .venv/bin/activate`
- [ ] Dependências instaladas? `pip install -r requirements.txt`
- [ ] Python certo? `python --version` → 3.9+
- [ ] Sistema validado? `python scripts/validate_system.py`
- [ ] Internet ok? `ping google.com`
- [ ] Permissões ok? `chmod +x scripts/*.py`
- [ ] Espaço em disco? `df -h`
- [ ] RAM suficiente? `free -h`

Se tudo OK e ainda não funciona: volte a estes passos!

---

## 📞 COMO REPORTAR BUG

Se encontrou erro:

```bash
# 1. Anotar erro exato
# (Copie mensagem vermelha completa)

# 2. Tentar reproduzir
python scripts/run_single_scan.py google.com

# 3. Verificar seu ambiente
python scripts/validate_system.py

# 4. Verificar logs
cat data/logs/audit_log.jsonl

# 5. Reportar com informações
# Sistema operacional: Linux Ubuntu 22.04
# Python versão: 3.9.0
# Erro exato: ModuleNotFoundError: No module named 'torch'
# Comando executado: python scripts/train_phase_d_rl.py
# Passo que estava fazendo: Treinamento RL
```

---

## 💡 DICAS & TRICKS

### Dica 1: Atalho para escanear rápido
```bash
alias deepai="python /workspaces/DeepAI/scripts/run_single_scan.py"
deepai google.com
```

### Dica 2: Monitorar progresso
```bash
# Em out terminal, execute de tempos em tempos
watch -n 5 "ls -la data/reports/"  # vê novos relatórios
```

### Dica 3: Processos em background
```bash
# Fazer coisa longa e continuar trabalhando
python scripts/train_phase_d_rl.py --episodes 5000 &
# Agora pode fazer outras coisas

# Ver processos
jobs
```

### Dica 4: Pipe com grep
```bash
# Procurar só os "malicious"
python scripts/run_phase_a_scan.py sites.txt | grep malicious

# Contar total
python scripts/run_phase_a_scan.py sites.txt | grep -c benign
```

---

## 🎓 APRENDER MAIS

- **Arquitetura**: Leia [docs/arquitetura.md](docs/arquitetura.md)
- **Features**: Leia [docs/documentacao_features.md](docs/documentacao_features.md)
- **Ética**: Leia [docs/politica_etica.md](docs/politica_etica.md)
- **Comandos**: Leia [TODOS_OS_COMANDOS.md](TODOS_OS_COMANDOS.md)
- **Exemplos**: Leia [EXEMPLOS_PRATICOS.md](EXEMPLOS_PRATICOS.md)

---

**Status**: ✅ Pronto  
**Problemas cobertos**: 15+ soluções
**FAQs**: 15 perguntas respondidas
**Última atualização**: 27 de Fevereiro de 2026
