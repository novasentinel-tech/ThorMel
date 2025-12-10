# 🚀 QUICK START - Começar Usar DeepAI em 5 minutos

Guia rápido para começar JÁ!

---

## 1️⃣ SETUP (2 minutos)

```bash
# Ativar ambiente
source .venv/bin/activate

# Instalar dependências (se não tiver)
pip install -r requirements.txt
```

---

## 2️⃣ VALIDAR (1 minuto)

```bash
# Testar se tudo funciona
python scripts/validate_system.py

# Resultado esperado:
# ✓ PASS   Module Imports
# ✓ PASS   Component Initialization
# ✓ PASS   Pipeline Initialization
# ✓ PASS   Feature Dimensions
# ✓ PASS   Model Availability
# ✓ PASS   Security Enforcement
# ✓ PASS   Test Coverage
```

---

## 3️⃣ ESCANEAR (1 minuto)

### Opção A: Um site
```bash
python scripts/run_single_scan.py google.com
```

### Opção B: Uma URL completa
```bash
python scripts/run_single_scan.py "https://github.com/new/repository"
```

### Opção C: Múltiplos sites
```bash
echo "google.com
github.com
stackoverflow.com" > sites.txt

python scripts/run_phase_a_scan.py sites.txt
```

**Resultado**:
```json
{
  "target": "google.com",
  "classification": "benign",
  "confidence": 95.2,
  "risk_level": "low"
}
```

---

## 4️⃣ VER RESULTADO

### Classificações Possíveis

| Resultado | Significado |
|-----------|-------------|
| 🟢 benign | SEGURO ✅ |
| 🟡 suspicious | CUIDADO ⚠️ |
| 🔴 malicious | PERIGOSO ❌ |
| ⚫ dangerous | BLOQUEADO 🚫 |

---

## 5️⃣ PRÓXIMOS PASSOS

### Se quer treinar modelo ML
```bash
python scripts/train_phase_c.py          # Treino completo (5-10 min)
python scripts/train_phase_c_fast.py     # Treino rápido (2-3 min)
```

### Se quer usar inteligência (RL)
```bash
python scripts/train_phase_d_rl.py --episodes 500     # Treinar RL
python scripts/inference_phase_d_rl.py google.com     # Usar RL
```

### Se quer ver TUDO funcionando
```bash
python scripts/demo_phase_f.py          # Demo completo (30 seg)
```

---

## 📋 COMANDOS MAIS USADOS

```bash
# Rápido: Escanear um site
python scripts/run_single_scan.py seu-dominio.com

# Completo: Com relatório HTML
python scripts/run_single_scan.py seu-dominio.com --output-html relatorio.html

# Batch: Múltiplos sites
python scripts/run_phase_a_scan.py sites.txt

# Demo: Ver tudo funcionando
python scripts/demo_phase_f.py

# Treinar: Modelo ML
python scripts/train_phase_c_fast.py

# Validar: Sistema
python scripts/validate_system.py
```

---

## 🎯 CASOS DE USO RÁPIDOS

### "Quero saber se um site é seguro"
```bash
python scripts/run_single_scan.py coolsite.com.br
```

### "Quero analisar 100 sites"
```bash
python scripts/run_phase_a_scan.py lista_de_sites.txt > resultado.json
```

### "Quero HTML com explicação"
```bash
python scripts/run_single_scan.py google.com --output-html report.html
open report.html
```

### "Quero entender como funciona"
```bash
python scripts/demo_phase_f.py
# Veja os arquivos HTML gerados em data/reports/
```

---

## ✅ CHECKLIST

- [ ] Ativei o ambiente
- [ ] Rodei validate_system.py (passou em 7/7?)
- [ ] Escanei um site com run_single_scan.py
- [ ] Recebi resultado (benign/suspicious/malicious)
- [ ] Li a documentação (README.md, CHEAT_SHEET.md)

---

## 🆘 ALGO DÉU ERRADO?

| Erro | Solução |
|------|---------|
| `ModuleNotFoundError: No module named 'src'` | Ambiente não ativado: `source .venv/bin/activate` |
| `No such file or directory` | Você está na pasta certa? `cd /workspaces/DeepAI` |
| `command not found: python` | Tente `python3` ao invés de `python` |
| Timeout | Domínio pode estar offline, tente outro |
| Muito lento | Seu computador é fraco, veja README.md (hardware) |

**Mais problemas?** Leia [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md)

---

## 📚 Documentação por Nível

### Iniciante
- [README.md](README.md) - Visão geral
- [CHEAT_SHEET.md](CHEAT_SHEET.md) - Comandos prontos

### Intermediário
- [TODOS_OS_COMANDOS.md](TODOS_OS_COMANDOS.md) - Todos os 9 scripts
- [EXEMPLOS_PRATICOS.md](EXEMPLOS_PRATICOS.md) - 10 cenários reais

### Avançado
- [docs/arquitetura.md](docs/arquitetura.md) - Como funciona
- [docs/documentacao_features.md](docs/documentacao_features.md) - 87 features
- [docs/politica_etica.md](docs/politica_etica.md) - Ética e segurança

---

## ⚡ ONE-LINER (Copie e Cole!)

```bash
# Escanear JÁ
python scripts/run_single_scan.py google.com

# Treinar JÁ
python scripts/train_phase_c_fast.py

# Validar JÁ
python scripts/validate_system.py

# Ver tudo JÁ
python scripts/demo_phase_f.py
```

---

## 🎓 Próximo Passo

1. **Iniciante?** → Leia [README.md](README.md)
2. **Quer usar YÁ?** → Use [CHEAT_SHEET.md](CHEAT_SHEET.md)
3. **Quer aprender?** → Leia [docs/arquitetura.md](docs/arquitetura.md)
4. **Tem problema?** → Veja [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md)

---

**Status**: ✅ Pronto para começar  
**Tempo estimado**: 5 minutos até seu primeiro scan  
**Requisitos**: Python 3.9+, ~2GB RAM, Internet
