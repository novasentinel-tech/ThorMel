# Política de Ética & Diretrizes de Segurança

## Princípios Centrais

### 1. Integridade Acadêmica
- Sistema opera EXCLUSIVAMENTE para pesquisa educacional
- Nenhuma exploração comercial permitida
- Todo uso deve ser transparente e documentado
- Resultados devem ser reportados honestamente

### 2. Não Causar Dano
- **Zero Exploração Ativa**: Nenhuma vulnerabilidade é explorada
- **Observação Passiva Apenas**: Coleta de informações sem intrusão
- **Respeitar Infraestrutura**: Sistemas críticos explicitamente protegidos
- **Privacidade em Primeiro Lugar**: Nenhuma coleta de dados pessoais

### 3. Transparência & Responsabilidade
- Toda ação registrada em trail de auditoria imutável
- Todas as previsões explicáveis e interpretáveis
- Usuários responsáveis por seu uso
- Verificação regular de integridade requerida

### 4. Conformidade Legal
- Operaciona dentro de leis e regulamentos aplicáveis
- Respeita direitos de propriedade intelectual
- Honra termos de serviço
- Nenhum acesso não autorizado a qualquer sistema

---

## O Que é Permitido ✓

### Coleta de Informações Passiva

```
✓ Análise de Cabeçalhos HTTP
✓ Inspeção de Certificados TLS/SSL
✓ Enumeração de Registros DNS
✓ Fingerprinting de Tech Stack
✓ Detecção de Serviços em Porta
✓ Lookup WHOIS
✓ Verificação de Reputação IP Pública
✓ Conformidade robots.txt
```

### Análise & Avaliação
```
✓ Classificação de Risco de Vulnerabilidade
✓ Análise de Postura de Segurança
✓ Avaliação de Configuração
✓ Verificação de Conformidade
✓ Verificação de Melhores Práticas
```

### Uso Educacional
```
✓ Pesquisa & Artigos Acadêmicos
✓ Ensino & Treinamento
✓ Consciência de Segurança
✓ Desenvolvimento Profissional
✓ Proof-of-Concept Demonstrations (autorizado)
```

---

## O Que é PROIBIDO ✗

### Exploração Ativa
```
✗ Injeção SQL
✗ Cross-Site Scripting (XSS)
✗ Cross-Site Request Forgery (CSRF)
✗ Execução Remota de Código
✗ Escalação de Privilégios
✗ Exfiltração de Dados
✗ Negação de Serviço (DoS/DDoS)
✗ Ataques de Bruteforce
✗ Adivinhação de Credenciais
```

### Atividades Maliciosas
```
✗ Comprometimento de Sistemas
✗ Injeção de Malware
✗ Instalação de Backdoor
✗ Deployment de Ransomware
✗ Destruição de Dados
✗ Disrupção de Serviço
✗ Invasão de Privacidade
```

### Circunvenção
```
✗ Bypass de Rate Limits
✗ Excedimento de Timeouts
✗ Scanning de Alvos Bloqueados
✗ Desabilitação de Logging de Auditoria
✗ Remoção de Verificações de Segurança
✗ Modificação de Código para Exploração
```

---

## Autorização & Consentimento

### Obrigatório Antes de Scanning
- ✅ Ser proprietário do alvo, OU
- ✅ Ter permissão explícita escrita do proprietário, OU  
- ✅ Plataforma de teste autorizada (HackerOne, Bugcrowd, etc.)

### NÃO Obrigatório
- ❌ Websites públicos para análise passiva puramente observacional
- ❌ Mas ainda sujeito a robots.txt e rate limiting

### Infraestrutura Crítica
```
SEMPRE PROIBIDO - Mesmo com permissão:
  • Agências governamentais (.gov, .mil)
  • Infraestrutura crítica (lista CISA)
  • Instituições financeiras
  • Sistemas de saúde
  • Serviços de emergência
  • Provedores de utilidade
  • Instalações nucleares
  • Sistemas eleitorais
```

---

## Monitoramento & Enforcement de Uso

### Enforcement Automático
1. **Validação de Domínio**: Bloqueio automático de alvos proibidos
2. **Rate Limiting**: Limite rígido em frequência de requisições
3. **Enforcement de Timeout**: 60 segundos máximo por scan
4. **Modo Acadêmico**: Não pode ser desabilitado ou contornado
5. **Logging de Auditoria**: Todas as ações registradas imutavelmente

### Validação Pré-Scan
```python
✓ Verificação de formato de domínio
✓ Verificação de lista negra
✓ Detecção de IP privado
✓ Verificação de rate limit
✓ Autorização de usuário
```

### Verificação Pós-Scan
```python
✓ Integridade do trail de auditoria
✓ Conformidade de timeout
✓ Nenhuma exploração detectada
✓ Conformidade de política confirmada
```

---

## Divulgação Responsável

### Quando Vulnerabilidades são Descobertas

1. **NÃO Explorar**: Nunca testar/confirmar vulnerabilidade
2. **Documentar**: Registrar descobertas que análise passiva revelou
3. **Reportar**: Notificar organização afetada privadamente
4. **Aguardar**: Permitir tempo razoável para remediação (geralmente 90 dias)
5. **Divulgar**: Apenas divulgação pública após fix confirmado

### Processo de Reportagem
```
Notificação Privada da Organização
  ↓ (permitir 30 dias resposta)
Lembrete se sem resposta  
  ↓ (permitir 60 dias adicionais)
Divulgação Coordenada (90 dias total)
  ↓
Divulgação Pública
```

---

## Integridade Acadêmica

### Uso de Dados para Pesquisa
- ✅ Coletar dados de segurança passivos
- ✅ Analisar padrões de vulnerabilidade
- ✅ Treinar modelos em dados históricos
- ✅ Publicar descobertas & melhorias
- ❌ NÃO incluir nomes de organização real sem consentimento
- ❌ NÃO incluir detalhes sensíveis
- ❌ NÃO identificar indivíduos
- ❌ NÃO compartilhar banco de dados bruto

---

## Responsabilidade

### Responsabilidades do Usuário
- Ler e entender esta política
- Usar apenas para fins autorizados
- Reportar abuso imediatamente
- Manter logs de auditoria
- Proteger credenciais
- Atualizar sistema regularmente

### Responsabilidades do Projeto
- Manter controles de segurança
- Monitorar por abuso
- Responder a violações
- Atualizar proteções
- Fornecer guia claro
- Tornar código revisável

### Lei de Proteção
- Cooperação com autoridades para investigação criminal
- Preservação de logs de auditoria para investigações
- Reportagem de atividade suspeita ilegal

---

## Violações & Consequências

### Violações Detectadas Resultarão Em

1. **Bloqueio Imediato**: Conta/IP suspenso
2. **Revisão de Auditoria**: Trail de auditoria completo analisado
3. **Investigação**: Determinar escopo e intenção
4. **Ação Legal**: Se criminal, reportar a autoridades
5. **Divulgação Pública**: Análise de padrão publicada (sem detalhes)

### Exemplos de Violações
- Tentativa de explorar vulnerabilidades
- Scanning de alvos proibidos
- Excedimento de limites configurados
- Desabilitação de controles de segurança
- Uso para fins comerciais sem licença
- Prejudicar qualquer organização ou indivíduo

---

## Recursos & Suporte

### Documentação
- [README](../README.md) - Guia de início rápido
- [Guia do Usuário](guia_usuario.md) - Uso detalhado
- [Referência API](referencia_api.md) - Detalhes técnicos

### Obtendo Ajuda
- Email: team@deepai-security.edu
- Issues: Rastreador de issues no GitHub
- Preocupação de segurança: security@deepai-security.edu

### Reportando Abuso
- Imediato: security@deepai-security.edu
- Anônimo: Formulário de reportagem anônima
- Detalhes: Incluir ID de log de auditoria se possível

---

## Atualizações de Política

Esta política pode ser atualizada para refletir mudanças legais, melhores práticas de segurança, ou melhorias operacionais. Usuários serão notificados de mudanças significativas.

**Versão Atual**: 1.0  
**Última Revisão**: 27 de Fevereiro de 2026  
**Próxima Revisão**: 27 de Fevereiro de 2027

---

## Reconhecimentos

Esta política de ética é baseada em:
- OWASP Bug Bounty Best Practices
- Coordinated Vulnerability Disclosure (CVD) Principles
- IEEE Ethical Computing
- Padrões de Pesquisa Acadêmica
- Responsible AI Principles

---

**Ao usar este sistema, você concorda em estar em conformidade com toda esta política de ética.**

*Sem exceções. Sem workarounds. Sem bypass possível.*
