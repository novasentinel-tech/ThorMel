# 🚀 TODOS OS COMANDOS - DeepAI IA

Guia completo de TODOS os comandos disponíveis para usar sua IA DeepAI!

---

## 📋 Índice Rápido

1. [Escanear Domínios](#1️⃣-escanear-domínios)
2. [Treinar Machine Learning](#2️⃣-treinar-machine-learning)
3. [Treinar Reinforcement Learning](#3️⃣-treinar-reinforcement-learning)
4. [Fazer Inferência](#4️⃣-fazer-inferência)
5. [Validar Sistema](#5️⃣-validar-sistema)
6. [Demo Completa](#6️⃣-demo-completa)
7. [Exemplos Práticos](#7️⃣-exemplos-práticos)

---

# 1️⃣ **ESCANEAR DOMÍNIOS**

## Comando: `run_single_scan.py`

**O QUE FAZ**: Escaneia UM domínio completamente

### ✅ Forma Básica
```bash
python scripts/run_single_scan.py google.com
```

### ✅ Com URL Completa
```bash
python scripts/run_single_scan.py "https://qqtechs.com.br/qqtech/login/index.php"
```

### ✅ Com Relatório HTML
```bash
python scripts/run_single_scan.py google.com --output-html relatorio.html
```

### ✅ Com Verbose (Mais Detalhes)
```bash
python scripts/run_single_scan.py google.com --verbose
```

### ✅ Ver Ajuda
```bash
python scripts/run_single_scan.py --help
```

### 📊 Saída
```json
{
  "status": "success",
  "target": "google.com",
  "classification": "LOW",
  "confidence": 0.92,
  "features_extracted": 87,
  "scan_time": 12.5,
  "recommendations": [...]
}
```

---

## Comando: `run_phase_a_scan.py`

**O QUE FAZ**: Escaneia múltiplos domínios em BATCH (Fase A - Coleta de Dados)

### ✅ Forma Básica
```bash
python scripts/run_phase_a_scan.py google.com github.com
```

### ✅ Com Arquivo de Domínios
```bash
# Criar arquivo
echo "google.com
github.com
stackoverflow.com" > dominios.txt

# Processar
python scripts/run_phase_a_scan.py -f dominios.txt
```

### ✅ Com Timeout Customizado
```bash
python scripts/run_phase_a_scan.py google.com github.com --timeout 300
```

### ✅ Com Formato JSON
```bash
python scripts/run_phase_a_scan.py google.com --json > resultados.json
```

### ✅ Ver Ajuda
```bash
python scripts/run_phase_a_scan.py --help
```

### 📊 Saída
```json
{
  "scans": [
    {
      "target": "google.com",
      "http": {...},
      "tls": {...},
      "dns": {...},
      "whois": {...},
      "ports": {...},
      "tech_stack": {...}
    }
  ]
}
```

---

# 2️⃣ **TREINAR MACHINE LEARNING**

## Comando: `train_phase_c.py`

**O QUE FAZ**: Treina modelo LightGBM (Machine Learning Supervisionado)

### ✅ Forma Básica (Padrão)
```bash
python scripts/train_phase_c.py
```
- Gera dataset de 10.000 amostras
- Treina modelo LightGBM
- Valida com 5-fold CV
- Salva modelo em `data/models/`

### ✅ Com Customizações
```bash
python scripts/train_phase_c.py \
    --epochs 100 \
    --batch-size 32 \
    --validation-split 0.2 \
    --random-state 42
```

### ✅ Com Dados Próprios
```bash
python scripts/train_phase_c.py \
    --data-path data/seu_dataset.npz \
    --epochs 200
```

### ✅ Com Saída Personalizada
```bash
python scripts/train_phase_c.py \
    --epochs 150 \
    --output-model models/meu_modelo_v1.pkl
```

### ✅ Ver Ajuda
```bash
python scripts/train_phase_c.py --help
```

### 📊 Output
```
PHASE C: MACHINE LEARNING MODEL TRAINING
[STEP 1] Generating dataset...
[STEP 2] Training LightGBM...
[STEP 3] Evaluating model...
[STEP 4] Cross-validation...

Final Metrics:
  Accuracy: 95.2%
  Precision: 94.8%
  Recall: 95.5%
  F1-Score: 95.1%
```

---

## Comando: `train_phase_c_fast.py`

**O QUE FAZ**: Treina LightGBM de forma RÁPIDA (versão otimizada)

### ✅ Forma Básica
```bash
python scripts/train_phase_c_fast.py
```
- Versão mais rápida de train_phase_c.py
- Menos validação, mais velocidade
- Ideal para iterações rápidas

### ✅ Com Parâmetros
```bash
python scripts/train_phase_c_fast.py \
    --learning-rate 0.1 \
    --max-depth 8 \
    --num-leaves 31
```

### ✅ Ver Ajuda
```bash
python scripts/train_phase_c_fast.py --help
```

---

# 3️⃣ **TREINAR REINFORCEMENT LEARNING**

## Comando: `train_phase_d_rl.py`

**O QUE FAZ**: Treina agente PPO para aprender estratégias de priorização

### ✅ Forma Básica
```bash
python scripts/train_phase_d_rl.py
```
- Treina agente PPO
- 1000 episódios por padrão
- Salva checkpoint em `checkpoints/`

### ✅ Com Episódios Customizados
```bash
python scripts/train_phase_d_rl.py --episodes 5000
```

### ✅ Com Learning Rate Custom
```bash
python scripts/train_phase_d_rl.py \
    --learning-rate 3e-4 \
    --episodes 2000
```

### ✅ Com Batch Size
```bash
python scripts/train_phase_d_rl.py \
    --batch-size 64 \
    --episodes 1000
```

### ✅ Com Reward Mode
```bash
python scripts/train_phase_d_rl.py \
    --reward-mode "cumulative" \
    --episodes 1000
```

### ✅ Com CUDA (GPU)
```bash
python scripts/train_phase_d_rl.py \
    --cuda \
    --episodes 5000
```

### ✅ Com Checkpoint
```bash
python scripts/train_phase_d_rl.py \
    --episodes 2000 \
    --save-checkpoint checkpoints/meu_agente.zip
```

### ✅ Ver Ajuda
```bash
python scripts/train_phase_d_rl.py --help
```

### 📊 Output
```
Using device: cuda
Initializing PPO agent...
Episode [1/1000] | Reward: 0.45 | Loss: 0.23
Episode [2/1000] | Reward: 0.52 | Loss: 0.19
...
Episode [1000/1000] | Reward: 0.89 | Loss: 0.05
Training completed! Checkpoint saved to: checkpoints/ppo_agent_v1.zip
```

---

# 4️⃣ **FAZER INFERÊNCIA**

## Comando: `inference_phase_d_rl.py`

**O QUE FAZ**: Usa agente RL treinado para fazer previsões

### ✅ Forma Básica
```bash
python scripts/inference_phase_d_rl.py google.com
```
- Carrega modelo ML
- Carrega agente RL
- Faz predição

### ✅ Com Checkpoint Customizado
```bash
python scripts/inference_phase_d_rl.py google.com \
    --checkpoint checkpoints/meu_agente.zip
```

### ✅ Com Modelo ML Customizado
```bash
python scripts/inference_phase_d_rl.py google.com \
    --model-path data/models/meu_modelo.pkl
```

### ✅ Com ambos customizados
```bash
python scripts/inference_phase_d_rl.py google.com \
    --model-path data/models/custom_ml.pkl \
    --checkpoint checkpoints/custom_rl.zip
```

### ✅ Ver Ajuda
```bash
python scripts/inference_phase_d_RL.py --help
```

### 📊 Output
```json
{
  "domain": "google.com",
  "ml_prediction": "LOW",
  "ml_confidence": 0.92,
  "rl_action": "PRIORITY_LOW",
  "final_priority": "LOW",
  "explanation": "..."
}
```

---

# 5️⃣ **VALIDAR SISTEMA**

## Comando: `validate_system.py`

**O QUE FAZ**: Verifica se tudo está instalado e funcionando

### ✅ Validação Completa
```bash
python scripts/validate_system.py
```

### ✅ Com Detalhes
```bash
python scripts/validate_system.py --verbose
```

### ✅ Teste Rápido
```bash
python scripts/validate_system.py --quick
```

### ✅ Ver Ajuda
```bash
python scripts/validate_system.py --help
```

### 📊 Output Esperado
```
DEEPAI SYSTEM VALIDATION
✓ Module Imports: 9/9 OK
✓ Component Initialization: 7/7 OK
✓ Data Files: 3/3 OK
✓ Models: 2/2 OK
✓ Memory: 4 GB Available
✓ CPU: 8 cores
✓ GPU: NVIDIA RTX 3080 (Optional)

OVERALL STATUS: ✅ ALL CHECKS PASSED
```

---

## Comando: `verify_security.py`

**O QUE FAZ**: Verifica restrições de segurança e modo acadêmico

### ✅ Forma Básica
```bash
python scripts/verify_security.py
```

### ✅ Com Cheques Completos
```bash
python scripts/verify_security.py --full
```

### ✅ Ver Ajuda
```bash
python scripts/verify_security.py --help
```

### 📊 Output Esperado
```
DEEPAI SECURITY VERIFICATION
✓ Academic Mode: ENFORCED
✓ Rate Limiting: ACTIVE
✓ Timeout Enforcement: ACTIVE
✓ Domain Validation: ACTIVE
✓ Audit Logging: ACTIVE
✓ No Exploitation Detected: OK

SECURITY STATUS: ✅ SECURE
```

---

# 6️⃣ **DEMO COMPLETA**

## Comando: `demo_phase_f.py`

**O QUE FAZ**: Executa demo de TODAS as 6 fases integradas

### ✅ Demo Completa
```bash
python scripts/demo_phase_f.py
```

### ✅ Com Target Customizado
```bash
python scripts/demo_phase_f.py google.com
```

### ✅ Com Verbosity
```bash
python scripts/demo_phase_f.py --verbose
```

### ✅ Ver Ajuda
```bash
python scripts/demo_phase_f.py --help
```

### 📊 Output Esperado
```
DEEPAI COMPLETE PIPELINE DEMO
phase A: Data Collection
    ✓ HTTP Headers: 15 features
    ✓ TLS/SSL: 18 features
    ✓ DNS: 12 features
    ✓ WHOIS: 10 features
    ✓ Ports: 15 features
    ✓ Tech Stack: 17 features
    Total: 87 features extracted

Phase B: Feature Engineering
    ✓ Normalization: Complete
    ✓ Validation: Passed
    ✓ Anomaly Detection: 0 anomalies

Phase C: ML Classification
    ✓ Prediction: LOW
    ✓ Confidence: 0.92
    ✓ Class Probabilities: [0.92, 0.06, 0.02, 0.00]

Phase D: RL Optimization
    ✓ Action Space: 10 actions
    ✓ Selected: PRIORITY_LOW
    ✓ Reward: 0.87

Phase E: Explainability
    ✓ SHAP Values: Calculated
    ✓ NLG Generation: Complete
    ✓ Recommendations: 5 generated

Phase F: Integration
    ✓ Report Generation: Complete
    ✓ Audit Logging: Complete
    ✓ JSON Export: Complete

OVERALL: ✅ ALL PHASES PASSED
```

---

# 7️⃣ **EXEMPLOS PRÁTICOS**

## 🔍 Escanear um Website
```bash
python scripts/run_single_scan.py "https://github.com"
```

## 📊 Batch Scan de Múltiplos Sites
```bash
python scripts/run_phase_a_scan.py google.com github.com stackoverflow.com
```

## 🎓 Treinar Modelo de ML
```bash
python scripts/train_phase_c.py --epochs 150
```

## 🤖 Treinar Agente RL
```bash
python scripts/train_phase_d_rl.py --episodes 2000 --cuda
```

## 🔮 Fazer Predição com RL Treinado
```bash
python scripts/inference_phase_d_rl.py google.com \
    --checkpoint checkpoints/ppo_agent_v1.zip
```

## ✅ Validar Tudo
```bash
python scripts/validate_system.py --verbose
```

## 🔐 Verificar Segurança
```bash
python scripts/verify_security.py --full
```

## 🎬 Demo Completa
```bash
python scripts/demo_phase_f.py --verbose
```

## 📈 Treinar ML Rápido + RL
```bash
# Treinar ML rápido
python scripts/train_phase_c_fast.py

# Depois treinar RL
python scripts/train_phase_d_rl.py --episodes 1000
```

## 🔄 Pipeline Completo
```bash
# 1. Coletar dados
python scripts/run_single_scan.py google.com

# 2. Treinar modelo ML
python scripts/train_phase_c.py

# 3. Treinar agente RL
python scripts/train_phase_d_rl.py --episodes 1000

# 4. Fazer predição
python scripts/inference_phase_d_rl.py google.com
```

---

# 📚 **MATRIZ DE COMANDOS**

| Objetivo | Comando | Tempo | Saída |
|----------|---------|-------|-------|
| **Escanear 1 URL** | `run_single_scan.py` | ~10-15s | JSON |
| **Escanear 10+ URLs** | `run_phase_a_scan.py` | ~2-5 min | Batch JSON |
| **Treinar ML** | `train_phase_c.py` | ~5-10 min | Modelo .pkl |
| **Treinar ML (Rápido)** | `train_phase_c_fast.py` | ~2-3 min | Modelo .pkl |
| **Treinar RL** | `train_phase_d_rl.py` | ~10-30 min | Checkpoint.zip |
| **Fazer Inferência RL** | `inference_phase_d_rl.py` | ~5-10s | JSON |
| **Validar Sistema** | `validate_system.py` | ~10s | Status |
| **Verificar Segurança** | `verify_security.py` | ~5s | Status |
| **Demo Completa** | `demo_phase_f.py` | ~20-30s | Relatório |

---

# 🛠️ **ARGUMENTOS COMUNS**

## Para Scripts de Scan
```
--verbose          # Mais informações
--output-html      # Salvar relatório HTML
--timeout          # Timeout em segundos
--json             # Formato JSON
```

## Para Scripts de Treino
```
--epochs            # Número de épocas
--batch-size        # Tamanho do batch
--learning-rate     # Taxa de aprendizado
--output-model      # Caminho do modelo
--cuda              # Usar GPU
```

## Para Scripts de Validação
```
--verbose           # Modo detalhado
--quick             # Teste rápido
--full              # Validação completa
```

---

# 🎯 **FLUXO RECOMENDADO**

### 1️⃣ **Primeira Vez**
```bash
# Validar instalação
python scripts/validate_system.py

# Verificar segurança
python scripts/verify_security.py

# Testar com demo
python scripts/demo_phase_f.py
```

### 2️⃣ **Usar Sistema**
```bash
# Escanear um domínio
python scripts/run_single_scan.py seu_dominio.com

# Ver resultado
python scripts/run_single_scan.py seu_dominio.com --verbose
```

### 3️⃣ **Treinar Modelos (Opcional)**
```bash
# Treinar ML
python scripts/train_phase_c.py

# Treinar RL
python scripts/train_phase_d_rl.py --episodes 2000

# Usar modelo treinado
python scripts/inference_phase_d_rl.py seu_dominio.com
```

---

# 📞 **TROUBLESHOOTING**

## Erro: "Command not found"
```bash
# Ativar ambiente
source .venv/bin/activate
cd /workspaces/DeepAI
```

## Erro: "ModuleNotFoundError"
```bash
# Instalar dependências
pip install -r requirements.txt
```

## Erro: "Permission denied"
```bash
# Dar permissão
chmod +x scripts/*.py
```

## Modelo não encontrado
```bash
# Treinar novo modelo
python scripts/train_phase_c.py
```

---

# ✨ **PRÓXIMAS AÇÕES**

1. ✅ Escolha o comando que quer usar
2. ✅ Copie exatamente como está escrito
3. ✅ Execute no terminal
4. ✅ Veja o resultado

---

**Data**: 27 de Fevereiro de 2026  
**Status**: ✅ 100% Completo  
**Desenvolvido por**: João Pedro Rodrigues Viana (16 anos)
