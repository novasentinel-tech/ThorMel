# 🎯 CHEAT SHEET - Comandos Mais Usados

Guia rápido com os COMANDOS MAIS USADOS da IA DeepAI!

---

## 🚀 INICIAR (Primeiro passo)

```bash
# Ativar ambiente
source .venv/bin/activate

# Validar tudo está OK
python scripts/validate_system.py

# Testar sistema
python scripts/demo_phase_f.py
```

---

## 🔍 ESCANEAR (O que mais você vai usar!)

### Escanear UM domínio
```bash
python scripts/run_single_scan.py google.com
```

### Escanear UMA URL completa
```bash
python scripts/run_single_scan.py "https://qqtechs.com.br/login/index.php"
```

### Escanear com Relatório HTML
```bash
python scripts/run_single_scan.py google.com --output-html relatorio.html
```

### Escanear com Detalhes (Verbose)
```bash
python scripts/run_single_scan.py google.com --verbose
```

### Escanear MÚLTIPLOS domínios
```bash
python scripts/run_phase_a_scan.py google.com github.com stackoverflow.com
```

### Escanear de arquivo
```bash
echo "google.com
github.com
aws.amazon.com" > sites.txt

python scripts/run_phase_a_scan.py -f sites.txt
```

---

## 🧠 TREINAR MODELOS

### Treinar Modelo ML (Machine Learning)
```bash
python scripts/train_phase_c.py
```

### Treinar ML RÁPIDO (iterações rápidas)
```bash
python scripts/train_phase_c_fast.py
```

### Treinar Agente RL (Reinforcement Learning)
```bash
python scripts/train_phase_d_rl.py
```

### Treinar RL com MAIS EPISÓDIOS
```bash
python scripts/train_phase_d_rl.py --episodes 5000
```

### Treinar RL com GPU (Mais rápido!)
```bash
python scripts/train_phase_d_rl.py --cuda --episodes 2000
```

---

## 🔮 FAZER PREVISÃO

### Usar modelo treinado
```bash
python scripts/inference_phase_d_rl.py google.com
```

### Com modelo customizado
```bash
python scripts/inference_phase_d_rl.py google.com \
    --checkpoint checkpoints/meu_modelo.zip
```

---

## ✅ VERIFICAR SISTEMA

### Validar instalação
```bash
python scripts/validate_system.py
```

### Verificar segurança
```bash
python scripts/verify_security.py
```

### Demo completo (todas as fases)
```bash
python scripts/demo_phase_f.py
```

---

## 📊 PIPELINE COMPLETO (Do início ao fim)

```bash
# 1. Validar
python scripts/validate_system.py

# 2. Escanear um domínio
python scripts/run_single_scan.py google.com

# 3. Treinar modelo ML
python scripts/train_phase_c.py

# 4. Treinar agente RL
python scripts/train_phase_d_rl.py --episodes 1000

# 5. Fazer predição
python scripts/inference_phase_d_rl.py google.com

# 6. Verificar resultado
python scripts/demo_phase_f.py
```

---

## 🎮 BRINCAR / TESTAR

```bash
# Rápido: Apenas validar
python scripts/validate_system.py

# Médio: Escanear um site
python scripts/run_single_scan.py google.com

# Completo: Demo de tudo
python scripts/demo_phase_f.py

# Batch: Escanear 100 sites
python scripts/run_phase_a_scan.py -f sites.txt
```

---

## 🎓 TREINAR (Estudar/Aprender)

```bash
# Passo 1: Entender estrutura
python scripts/validate_system.py --verbose

# Passo 2: Treinar ML
python scripts/train_phase_c.py

# Passo 3: Treinar RL
python scripts/train_phase_d_rl.py

# Passo 4: Testar
python scripts/inference_phase_d_rl.py google.com
```

---

## 💾 SALVAR RESULTADOS

### Relatorio HTML
```bash
python scripts/run_single_scan.py google.com --output-html resultado.html
```

### JSON para processar depois
```bash
python scripts/run_phase_a_scan.py google.com --json > resultado.json
```

### Modelo ML para usar depois
```bash
python scripts/train_phase_c.py --output-model meu_modelo.pkl
```

### Checkpoint RL para usar depois
```bash
python scripts/train_phase_d_rl.py --episodes 2000 --save-checkpoint meu_rl.zip
```

---

## 🆘 PROBLEMAS COMUNS

| Problema | Solução |
|----------|---------|
| Command not found | `source .venv/bin/activate` |
| ModuleNotFoundError | `pip install -r requirements.txt` |
| Permission denied | `chmod +x scripts/*.py` |
| Modelo não encontrado | `python scripts/train_phase_c.py` |
| Timeout | Tente com domínio diferente |

---

## ⚡ RÁPIDO & SIMPLES

```bash
# Quero escanear JÁ
python scripts/run_single_scan.py google.com

# Quero relatório HTML AGORA
python scripts/run_single_scan.py google.com --output-html relatorio.html

# Quero treinar modelo RÁPIDO
python scripts/train_phase_c_fast.py

# Quero ver tudo funcionando
python scripts/demo_phase_f.py

# Quero usar meu modelo
python scripts/inference_phase_d_rl.py google.com --checkpoint models/meu.zip
```

---

## 📱 ONE-LINERS (Copie e Cole)

```bash
# Escanear
python scripts/run_single_scan.py google.com

# Validar
python scripts/validate_system.py

# Treinar ML
python scripts/train_phase_c.py

# Treinar RL
python scripts/train_phase_d_rl.py --episodes 1000

# Predição
python scripts/inference_phase_d_rl.py google.com

# Demo
python scripts/demo_phase_f.py

# Batch
python scripts/run_phase_a_scan.py google.com github.com
```

---

## 🎯 COM ARGUMENTOS

```bash
# Escanear com detalhes
python scripts/run_single_scan.py google.com --verbose

# Treinar com GPU
python scripts/train_phase_d_rl.py --cuda

# Treinar mais
python scripts/train_phase_d_rl.py --episodes 5000

# Treinar mais rápido (menos dados)
python scripts/train_phase_c_fast.py

# Modelo customizado
python scripts/inference_phase_d_rl.py google.com --checkpoint checkpoint.zip
```

---

## 📋 CHECKLIST

- [ ] Ativar ambiente: `source .venv/bin/activate`
- [ ] Validar: `python scripts/validate_system.py`
- [ ] Escanear: `python scripts/run_single_scan.py google.com`
- [ ] Ver resultado em JSON
- [ ] Treinar modelo: `python scripts/train_phase_c.py`
- [ ] Treinar RL: `python scripts/train_phase_d_rl.py`
- [ ] Fazer predição: `python scripts/inference_phase_d_rl.py google.com`

---

**Status**: ✅ Pronto para usar  
**Última atualização**: 27 de Fevereiro de 2026
