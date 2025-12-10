# 📝 Formatos de URL Suportados - DeepAI Scanner

O script `run_single_scan.py` agora aceita **qualquer formato de URL ou domínio**! A extração de domínio é automática.

---

## ✅ Formatos Testados e Validados

### **1. URL Completa com Path**
```bash
python scripts/run_single_scan.py "https://lojinha.com.br/lojinha/login/index.php"
# Extrai → qqtechs.com.br
# ✅ FUNCIONA
```

### **2. URL Completa com Query String**
```bash
python scripts/run_single_scan.py "https://google.com/search?q=test&lang=pt"
# Extrai → google.com
# ✅ FUNCIONA
```

### **3. Domínio Simples**
```bash
python scripts/run_single_scan.py "github.com"
# Extrai → github.com
# ✅ FUNCIONA
```

### **4. URL com Protocolo HTTP**
```bash
python scripts/run_single_scan.py "http://example.com/page"
# Extrai → example.com
# ✅ FUNCIONA
```

### **5. URL com Protocolo HTTPS**
```bash
python scripts/run_single_scan.py "https://example.com"
# Extrai → example.com
# ✅ FUNCIONA
```

### **6. URL com Porta Customizada**
```bash
python scripts/run_single_scan.py "http://example.com:8080/admin"
# Extrai → example.com
# ✅ FUNCIONA
```

### **7. URL com Subdomínio**
```bash
python scripts/run_single_scan.py "https://api.github.com/repos"
# Extrai → api.github.com
# ✅ FUNCIONA
```

### **8. URL com Credenciais (Removidas Automaticamente)**
```bash
python scripts/run_single_scan.py "https://user:password@example.com/page"
# Extrai → example.com
# ✅ FUNCIONA
```

### **9. URL com Fragment**
```bash
python scripts/run_single_scan.py "https://example.com/page#section"
# Extrai → example.com
# ✅ FUNCIONA
```

### **10. Domínio com Múltiplas Extensions**
```bash
python scripts/run_single_scan.py "https://lojinha.com.br"
# Extrai → qqtechs.com.br
# ✅ FUNCIONA
```

---

## 🎯 Exemplos Práticos

### Escanear um Website Completo
```bash
python scripts/run_single_scan.py "https://qqtechs.com.br/qqtech/login/index.php"
```

### Escanear uma Página Específica
```bash
python scripts/run_single_scan.py "https://github.com/novasentinel-tech/DeepAI"
```

### Escanear com Modo Verbose
```bash
python scripts/run_single_scan.py "https://google.com" --verbose
```

### Gerar Relatório HTML
```bash
python scripts/run_single_scan.py "https://example.com" --output-html relatorio.html
```

### Escanear Múltiplos URLs em Batch
```bash
for url in \
    "https://google.com" \
    "https://github.com" \
    "https://qqtechs.com.br/qqtech/login/index.php"
do
    python scripts/run_single_scan.py "$url"
done
```

---

## 🔄 O Que Acontece nos Bastidores

```
Input do Usuário
    ↓
Extração de Domínio (função extract_domain_from_url)
    ↓
Validação de Domínio
    ↓
Verificação de Rate Limits
    ↓
Logging de Auditoria
    ↓
Pipeline de Análise
    ↓
Resultado JSON
```

### Função de Extração

```python
# Exemplos de transformação:

https://qqtechs.com.br/qqtech/login/index.php
  → qqtechs.com.br

https://google.com/search?q=test&lang=pt
  → google.com

http://example.com:8080/admin
  → example.com

github.com
  → github.com

https://user:pass@example.com:8443/page#section
  → example.com
```

---

## 📊 Teste Rápido

Executar este comando para verificar se tudo está funcionando:

```bash
python scripts/run_single_scan.py "https://qqtechs.com.br/qqtech/login/index.php" 2>&1 | grep -E "(Input|Extracted|SCANNING)"
```

Saída esperada:
```
INFO | Input: https://qqtechs.com.br/qqtech/login/index.php
INFO | Extracted domain: qqtechs.com.br
🔍 SCANNING: https://qqtechs.com.br/qqtech/login/index.php
📍 Domain extracted: qqtechs.com.br
```

---

## ⚠️ Casos Edge (Não Testados Formalmente)

```bash
# Estes devem funcionar, mas use com cuidado:

python scripts/run_single_scan.py "192.168.1.1"           # IP Direto
python scripts/run_single_scan.py "localhost:3000"        # localhost com porta
python scripts/run_single_scan.py "::1"                   # IPv6 (pode falhar)
```

---

## 💡 Dicas

1. **Use aspas duplas** para URLs com caracteres especiais:
   ```bash
   python scripts/run_single_scan.py "https://example.com?q=search&lang=pt"
   ```

2. **URLs com porta** são extraídas corretamente:
   ```bash
   python scripts/run_single_scan.py "https://example.com:8443/api"
   # → example.com (porta é removida automaticamente)
   ```

3. **Subdomínios são preservados**:
   ```bash
   python scripts/run_single_scan.py "https://api.github.com"
   # → api.github.com (subdomínio NÃO é removido)
   ```

---

**Status**: ✅ Totalmente Funcional

**Última Atualização**: 27 de Fevereiro de 2026

**Desenvolvido por**: João Pedro Rodrigues Viana
