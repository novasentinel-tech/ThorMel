# 💡 EXEMPLOS PRÁTICOS - Como Usar a IA DeepAI

Situações reais e como resolver com DeepAI!

---

## 📋 CENÁRIO 1: Verificar se um Site é Seguro

**Situação**: Você recebeu um link estranho e quer saber se é seguro.

```bash
# Comando
python scripts/run_single_scan.py "https://qqtechs.com.br"

# Resultado esperado
{
  "status": "success",
  "target": "qqtechs.com.br",
  "classification": "benign",  # SEGURO = benign
  "confidence": 95.2,
  "features_extracted": 87,
  "risk_level": "low"
}

# Interpretação
✅ SEGURO se: classification = "benign"
⚠️  CUIDADO se: classification = "suspicious"
❌ PERIGOSO se: classification = "malicious" ou "dangerous"
```

---

## 🔐 CENÁRIO 2: Verificar Múltiplos Clientes/Fornecedores

**Situação**: Você precisa validar a segurança de 50 sites de parceiros.

```bash
# Passo 1: Criar arquivo com todos os sites
cat > parceiros.txt << EOF
parceiro1.com.br
parceiro2.com
meu-fornecedor.com
novo-cliente.com
EOF

# Passo 2: Escanear todos
python scripts/run_phase_a_scan.py parceiros.txt

# Resultado
Escaneando: parceiro1.com.br ... [benign]
Escaneando: parceiro2.com ... [suspicious]
Escaneando: meu-fornecedor.com ... [benign]
Escaneando: novo-cliente.com ... [malicious] ⚠️

# Interpretação
✅ parceiro1 e meu-fornecedor = CONFIÁVEIS
⚠️  parceiro2 = INVESTIGAR
❌ novo-cliente = NÃO USE
```

---

## 🎯 CENÁRIO 3: Pesquisador Analisando Ameaças

**Situação**: Você estuda domínios maliciosos e quer análise detalhada.

```bash
# Comando com detalhes
python scripts/run_single_scan.py malware-site.com --verbose

# Resultado
Target: malware-site.com
Risk Level: CRITICAL
Confidence: 98.7%

Features analisadas:
- HTTP Headers: sospeitoso (certificado inválido)
- TLS/SSL: sospeitoso (HSTS ausente)
- DNS: perigoso (resolutores públicos suspeitosos)
- WHOIS: sospeitoso (registrado com proxy)
- Ports: normal (80, 443 abertos)
- Tech Stack: normal (Apache, PHP)

Explicação: 
O site combina certificado fraco + configuração DNS suspeita
= Alto risco de ataque man-in-the-middle

Recomendação: NÃO ACESSE
```

---

## 📊 CENÁRIO 4: Aproveitar Inteligência (RL Agent)

**Situação**: Você quer que a IA aprenda sua estratégia de análise.

```bash
# Passo 1: Treinar agente
python scripts/train_phase_d_rl.py --episodes 1000

# Resultado
Episódio 1/1000 ... Reward: 45.2%
Episódio 100/1000 ... Reward: 72.1%
Episódio 500/1000 ... Reward: 89.3%
Episódio 1000/1000 ... Reward: 94.1%

Agente treinado com sucesso!
Checkpoint salvo em: checkpoints/rl/ppo_model.zip

# Passo 2: Usar agente para prever
python scripts/inference_phase_d_rl.py site-novo.com

# Resultado
RL Agent Prediction:
Risk: 23.4 (Baixo)
Confidence: 96.2%
Recomendação: SEGURO
```

---

## 🏢 CENÁRIO 5: Empresa com Site Próprio

**Situação**: Sua empresa quer melhorar a segurança do site dela mesma.

```bash
# Passo 1: Analisar site atual
python scripts/run_single_scan.py minha-empresa.com.br

# Resultado pode ser:
❌ "malicious" ou "dangerous"
⚠️  "suspicious"
✅ "benign"

# Se for "suspicious" ou pior:

# Passo 2: Entender problemas
python scripts/run_single_scan.py minha-empresa.com.br --verbose

# Resultado mostra EXATAMENTE o que melhorar:
❌ HTTP: Header X-Content-Type-Options faltando
❌ TLS: SSL versão 3.0 (muito antiga)
⚠️  DNS: Resolver pode ser mais seguro
✅ Port: Apenas 80 e 443 (bom)

# Passo 3: Melhorar (da para o seu time técnico):
- Adicionar security headers no servidor
- Atualizar TLS para 1.2+
- Configurar DNS resolver mais seguro

# Passo 4: Validar melhoria
python scripts/run_single_scan.py minha-empresa.com.br
# Resultado esperado: ✅ "benign"
```

---

## 🔬 CENÁRIO 6: Pesquisa de Segurança

**Situação**: Você está pesquisando padrões de segurança em domínios.

```bash
# Passo 1: Escanear muitos domínios
cat > dominos_para_pesquisa.txt << EOF
example.com
test.com
demo.com
sample.com
www.example.com
EOF

# Passo 2: Executar batch
python scripts/run_phase_a_scan.py dominos_para_pesquisa.txt

# Resultado em JSON
[
  {"domain": "example.com", "risk": "benign", "conf": 96.2},
  {"domain": "test.com", "risk": "suspicious", "conf": 87.3},
  {"domain": "demo.com", "risk": "benign", "conf": 94.1},
  ...
]

# Passo 3: Analisar estatísticas
- 60% benign (seguem padrões seguros)
- 30% suspicious (alguns problemas)
- 10% dangerous (alto risco real)

# Conclusão: Use para publicação, tese, artigo
```

---

## 🤖 CENÁRIO 7: Automatizar Monitoramento Contínuo

**Situação**: Você quer monitorar 1000 domínios automaticamente.

```bash
# Passo 1: Criar script que roda todo dia
cat > monitor_diario.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)

# Escanear todos
python scripts/run_phase_a_scan.py dominios.txt > "resultado_$DATE.json"

# Se alguém mudou para malicious, alertar
if grep -q "malicious" "resultado_$DATE.json"; then
  echo "⚠️ ALERTA: Domínio malicioso detectado!"
  echo "Verifique resultado_$DATE.json"
fi

# Guardar resultado
mv "resultado_$DATE.json" historico/
EOF

# Passo 2: Acessar via CRON
crontab -e
# Adicionar: 0 2 * * * /root/monitor_diario.sh  # Roda 2h da manhã

# Resultado: Você monitora 1000 sites todo dia automaticamente!
```

---

## 📈 CENÁRIO 8: Treinar com Seus Dados

**Situação**: Você tem base de dados de sites bons e ruins.

```bash
# Passo 1: Preparar dados
# Arquivo: meus_dados_de_treino.csv
# url,label
# google.com,1
# malware-site.com,0
# facebook.com,1

# Passo 2: Treinar modelo
python scripts/train_phase_c.py \
    --data-file meus_dados_de_treino.csv \
    --output-model modelo_customizado.pkl

# Resultado
Treino iniciado...
Época 1/10 - Acurácia: 82.3%
Época 5/10 - Acurácia: 91.2%
Época 10/10 - Acurácia: 95.7% ✅

Modelo salvo com sucesso!

# Passo 3: Usar modelo customizado
python scripts/inference_phase_d_rl.py novo-site.com \
    --model modelo_customizado.pkl

# Resultado: predição baseada em SEUS dados!
```

---

## 🎓 CENÁRIO 9: Aprender sobre Segurança

**Situação**: Você quer entender como sites são analisados.

```bash
# Passo 1: Ver demo completo
python scripts/demo_phase_f.py

# Resultado mostra:
1. Sites sendo escaneados (google.com, github.com, example.com)
2. 87 features sendo extraídas por site
3. Classificação final (benign/suspicious/malicious)
4. Explicação em linguagem natural
5. Relatório HTML gerado

# Passo 2: Ler explicação detalhada
# Abrir: data/reports/example_com_report.html no navegador
# Você vê EXATAMENTE por que o site é classificado assim

# Passo 3: Aprofundar
# Ler documentação de features: docs/documentacao_features.md
# Entender cada um dos 87 features

# Resultado: Você aprende segurança na prática!
```

---

## 🚨 CENÁRIO 10: Responder Incidente

**Situação**: Um site suspeito apareceu em seus servidores!

```bash
# ⏱️ Tempo: MÁXIMO 2 MINUTOS

# Passo 1: Obter domínio (30 segundos)
SITE_SUSPEITO="dominio-estranho.com"

# Passo 2: Analisar AGORA (10-15 segundos)
python scripts/run_single_scan.py $SITE_SUSPEITO --verbose

# Passo 3: Resultado
❌ classification: "dangerous"
❌ confidence: 98.9%
✅ action: BLOQUEIA IMEDIATAMENTE

# Passo 4: Investigação (registrar)
echo "$(date): Bloqueado domínio $SITE_SUSPEITO - malicioso detectado" >> incidentes.log

# Resultado: Incidente controlado em <2 minutos!
```

---

## 💾 RESUMO: Comandos por Cenário

| Cenário | Comando |
|---------|---------|
| Verificar 1 site | `python scripts/run_single_scan.py site.com` |
| Verificar múltiplos | `python scripts/run_phase_a_scan.py dominios.txt` |
| Análise detalhada | `python scripts/run_single_scan.py site.com --verbose` |
| Relatório HTML | `python scripts/run_single_scan.py site.com --output-html relatorio.html` |
| Treinar modelo | `python scripts/train_phase_c.py` |
| Treinar RL | `python scripts/train_phase_d_rl.py --episodes 1000` |
| Usar RL | `python scripts/inference_phase_d_rl.py site.com` |
| Ver tudo | `python scripts/demo_phase_f.py` |
| Validar sistema | `python scripts/validate_system.py` |

---

## 🎯 FLUXOGRAMA: Como Decidir?

```
Você quer fazer O QUÊ?
│
├─ Verificar UM site?
│  └─ python scripts/run_single_scan.py site.com
│
├─ Verificar MÚLTIPLOS sites?
│  └─ python scripts/run_phase_a_scan.py sites.txt
│
├─ Usar INTELIGÊNCIA (RL)?
│  └─ python scripts/train_phase_d_rl.py
│  └─ python scripts/inference_phase_d_rl.py site.com
│
├─ TREINAR modelo?
│  └─ python scripts/train_phase_c.py
│
├─ Ver TUDO FUNCIONANDO?
│  └─ python scripts/demo_phase_f.py
│
└─ VALIDAR que funciona?
   └─ python scripts/validate_system.py
```

---

**Status**: ✅ Pronto para usar  
**Cenários cobertos**: 10 situações reais
**Última atualização**: 27 de Fevereiro de 2026
