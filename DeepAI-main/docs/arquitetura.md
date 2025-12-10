# 🏗️ Arquitetura do Sistema

## Visão Geral da Arquitetura em Camadas

```
┌─────────────────────────────────────┐
│      CAMADA DE ENTRADA              │
│  Validação de Domínio & Whitelist   │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   CAMADA DE COLETA PASSIVA          │
│  • Cabeçalhos HTTP • TLS/SSL        │
│  • Registros DNS  • Tech Stack      │
│  • Port Scanning • WHOIS            │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   CAMADA DE ENGENHARIA DE FEATURES  │
│  87 Features dos Dados Brutos       │
│  • Normalização & Encoding          │
│  • Detecção de Anomalias            │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   CORE ML (Supervisionado)          │
│  Classificação LightGBM             │
│  • 4 Classes de Risco               │
│  • Saídas de Probabilidade          │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   OTIMIZAÇÃO RL (Priorização)       │
│  Tomada de Decisão com Agente PPO   │
│  • 10 Ações Possíveis               │
│  • Aprendizado com Recompensa       │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   CAMADA DE EXPLAINABILIDADE        │
│  • Valores SHAP                     │
│  • Geração de Linguagem Natural     │
│  • Recomendações Acionáveis         │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   CAMADA DE SEGURANÇA & AUDITORIA   │
│  • Rate Limiting                    │
│  • Enforcement de Timeout           │
│  • Log de Auditoria Imutável        │
│  • Enforcement de Modo Acadêmico    │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   SAÍDA & RELATÓRIOS                │
│  Relatório JSON + HTML + Auditoria  │
└─────────────────────────────────────┘
```

## Interações entre Componentes

### 1. Segurança no Ponto de Entrada
- Validador de domínio enforça lista negra
- Rate limiter verifica cotas de uso
- Enforcement de modo acadêmico valida submissão de política

### 2. Coleta de Dados (em Paralelo)
- Coletor HTTP → Análise de cabeçalhos
- Coletor TLS → Inspeção de certificados e cifras
- Coletor DNS → Enumeração de registros
- Detector de tech stack → Fingerprinting
- Port scanner → Identificação de serviços abertos

### 3. Engenharia de Features
- Normalização de dados brutos (escalamento Min-Max)
- Codificação categórica (one-hot)
- Validação de features e detecção de anomalias
- Produz vetores consistentes de 87 dimensões

### 4. Classificação com Machine Learning
- LightGBM ingere as features
- Gera probabilidades de classe (BAIXO, MÉDIO, ALTO, CRÍTICO)
- Extrai importância de features
- Calcula score de confiança

### 5. Priorização com Reinforcement Learning
- Estado construído a partir da saída ML + contexto
- Agente PPO seleciona ação otimizada
- 10 ações de priorização possíveis
- Aprendizado com feedback de analistas

### 6. Geração de Explainabilidade
- SHAP calcula contribuições de features
- NLG converte para texto legível
- Recomendações montadas
- Insights específicos do contexto adicionados

### 7. Segurança & Auditoria
- Rate limit incrementado
- Entrada de log de auditoria anexada (hash-chained)
- Timeout verificado
- Restrições de modo acadêmico verificadas

### 8. Geração de Relatório
- Montagem de saída JSON
- Geração de relatório HTML (opcional)
- Verificação de conformidade
- Arquivamento com timestamp

---

## Princípios Fundamentais de Design

### Segurança em Primeiro Lugar
- ✓ Nenhuma capacidade de exploração whatsoever
- ✓ Endurecido contra abuso
- ✓ Trail de auditoria imutável
- ✓ Modo acadêmico obrigatório

### Transparência & Explainabilidade
- ✓ Toda previsão explicada
- ✓ Toda evidência citada
- ✓ Confiança quantificada
- ✓ Saída legível para humanos

### Avaliação Rigorosa
- ✓ Meta de acurácia 85%+
- ✓ Recall crítico 95%+ (prioridade alta)
- ✓ CV estratificado 5-fold
- ✓ Métricas ponderadas por classe

### Melhoria Contínua
- ✓ Treinamento RL offline
- ✓ Loop de feedback de analistas
- ✓ Retreinamento trimestral
- ✓ Versionamento de modelo

---

## Exemplos de Fluxo de Dados

### Exemplo 1: Site Benígno de Baixo Risco

```
Entrada: google.com
  ↓
Validação: PASS ✓
  ↓
Coleta: Headers ✓, TLS 1.3✓, Sec Headers ✓
  ↓
Features: [1.3, 256, True, True, False, ...]
  ↓
Classificação ML: BAIXO (p=0.92)
  ↓
Ação RL: PRIORIDADE_BAIXA
  ↓
Saída: {
  "classificação": "BAIXO",
  "confiança": 0.92,
  "prioridade": "BAIXA",
  "explicação": "Segurança padrão da indústria..."
}
```

### Exemplo 2: Site de Alto Risco Vulnerável

```
Entrada: vulnerable-site.com
  ↓
Validação: PASS ✓
  ↓
Coleta: TLS 1.0✗, No HSTS✗, CMS Desatualizado✗
  ↓
Features: [1.0, 128, False, True, True, ...]
  ↓
Classificação ML: ALTO (p=0.87)
  ↓
Ação RL: PRIORIDADE_CRÍTICA (promovida de ALTO)
  ↓
Saída: {
  "classificação": "ALTO",
  "confiança": 0.87,  
  "prioridade": "CRÍTICA",
  "recomendações": [
    "Atualizar TLS para 1.3...",
    "Implementar HSTS...",
    "Patchear CMS..."
  ]
}
```

### Exemplo 3: Alvo Perigoso Bloqueado

```
Entrada: some-government-agency.gov
  ↓
Validação: BLOQUEADO ✗
  "TLD bloqueado: .gov"
  ↓
Log de Auditoria: Evento BLOQUEADO registrado
  ↓
Saída: {
  "status": "bloqueado",
  "motivo": "Infraestrutura crítica protegida"
}
```

---

## Detalhes da Estrutura de Arquivos

```
src/
├── collectors/          # Coleta de dados
│   ├── http_collector.py        # Timeout 10s
│   ├── tls_collector.py         # Timeout 15s  
│   ├── dns_collector.py         # Timeout 5s
│   └── base_collector.py        # Classe base
│
├── features/            # Criação de features
│   ├── feature_extractor.py     # Extrator principal
│   ├── feature_definitions.py   # 87 especificações
│   ├── normalizers.py           # Min-Max, Std
│   └── validators.py            # Verificações
│
├── models/
│   ├── supervised/      # Modelos ML
│   │   ├── lgbm_classifier.py   # Wrapper LightGBM
│   │   ├── trainer.py           # Pipeline treino
│   │   └── evaluator.py         # Cálculo métricas
│   │
│   └── reinforcement/   # Agentes RL
│       ├── ppo_agent.py         # Implementação PPO
│       ├── environment.py       # Ambiente simulação
│       ├── reward_function.py   # Lógica recompensa
│       └── trainer.py           # Loop treino
│
├── security/            # Enforcement segurança
│   ├── domain_validator.py      # Blacklist/whitelist
│   ├── rate_limiter.py          # Cotas de uso
│   ├── timeout_manager.py       # Limites operacionais
│   ├── academic_mode.py         # Enforcement política
│   └── audit_log.py             # Logging imutável
│
├── explainability/      # Interpretação
│   ├── shap_explainer.py        # Valores SHAP
│   ├── nlg_generator.py         # Geração texto
│   └── templates.py             # Templates explicação
│
└── pipeline/            # Orquestração
    ├── scan_pipeline.py         # Workflow principal
    ├── analysis_pipeline.py     # Passos análise
    └── report_generator.py      # Formatação saída
```

---

## Hierarquia de Configuração

```
valores padrão
  ↓ (sobrescrito por)
Variáveis de ambiente (.env.example)
  ↓ (sobrescrito por)  
Argumentos runtime
  ↓
Configuração Final Aplicada
```

## Versionamento de Modelos

```
Modelos ML:
  latest → v2.3.1 (atual)
  ├── v2.3.0 (anterior)
  ├── v2.2.0
  └── v1.0.0 (experimental)

Modelos RL:
  latest → v1.2.0
  └── v1.0.0

Explicadores SHAP:
  latest → v1.0.0
```

---

**Última Atualização: 27 de Fevereiro de 2026**
