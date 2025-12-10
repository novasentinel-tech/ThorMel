export type RiskLevel = "critical" | "high" | "medium" | "low" | "info"

export interface Vulnerability {
  id: string
  name: string
  riskLevel: RiskLevel
  location: string
  scanner: string
  description: string
  evidence: string
  recommendation: string
}

export interface ScanResult {
  id: string
  target: string
  date: string
  scanType: string
  riskScore: number
  totalVulnerabilities: number
  openPorts: number
  warnings: number
  vulnerabilities: Vulnerability[]
  distribution: {
    critical: number
    high: number
    medium: number
    low: number
    info: number
  }
  technologies: {
    server: string
    language: string
    framework: string
    os: string
    cms: string
  }
  logEntries: string[]
}

export interface ScanHistoryEntry {
  id: string
  target: string
  date: string
  riskScore: number
  scanType: string
  status: "completed" | "running" | "failed"
}

export const mockScanResult: ScanResult = {
  id: "scan-001",
  target: "https://exemplo.com.br",
  date: "2026-02-26T14:30:00Z",
  scanType: "Completo",
  riskScore: 72,
  totalVulnerabilities: 14,
  openPorts: 5,
  warnings: 8,
  vulnerabilities: [
    {
      id: "vuln-001",
      name: "SQL Injection",
      riskLevel: "critical",
      location: "Parametro 'id' em /api/users",
      scanner: "SQL Injection Scanner",
      description:
        "Foi detectada uma vulnerabilidade de SQL Injection no parametro 'id'. Um atacante pode manipular consultas SQL para acessar ou modificar dados nao autorizados no banco de dados.",
      evidence: `GET /api/users?id=1' OR '1'='1 HTTP/1.1\nHost: exemplo.com.br\n\nResposta: 200 OK\nCorpo: [{"id":1,"name":"admin","email":"admin@exemplo.com.br"},{"id":2,"name":"usuario","email":"user@exemplo.com.br"}]`,
      recommendation:
        "Utilize consultas parametrizadas (prepared statements) em vez de concatenar strings SQL. Implemente validacao de entrada rigorosa e use um ORM para abstrair o acesso ao banco de dados.",
    },
    {
      id: "vuln-002",
      name: "Cross-Site Scripting (XSS)",
      riskLevel: "high",
      location: "Campo de busca em /search",
      scanner: "XSS Scanner",
      description:
        "O campo de busca e vulneravel a XSS refletido. Scripts maliciosos podem ser injetados e executados no navegador de outros usuarios.",
      evidence: `GET /search?q=<script>alert('XSS')</script> HTTP/1.1\n\nResposta contendo o script sem sanitizacao:\n<div class="results">Resultados para: <script>alert('XSS')</script></div>`,
      recommendation:
        "Sanitize todas as entradas do usuario antes de renderiza-las no HTML. Use funcoes de escape apropriadas e implemente Content Security Policy (CSP) no cabecalho HTTP.",
    },
    {
      id: "vuln-003",
      name: "Cabecalhos de Seguranca Ausentes",
      riskLevel: "medium",
      location: "Resposta HTTP global",
      scanner: "Header Scanner",
      description:
        "Cabecalhos de seguranca importantes estao ausentes na resposta HTTP, incluindo X-Content-Type-Options, X-Frame-Options e Strict-Transport-Security.",
      evidence: `HTTP/1.1 200 OK\nContent-Type: text/html\nServer: Apache/2.4.41\n\nCabecalhos ausentes:\n- X-Content-Type-Options\n- X-Frame-Options\n- Strict-Transport-Security\n- Content-Security-Policy`,
      recommendation:
        "Configure o servidor web para incluir todos os cabecalhos de seguranca recomendados. Utilize ferramentas como helmet.js para Node.js ou configure diretamente no Apache/Nginx.",
    },
    {
      id: "vuln-004",
      name: "Versao do Servidor Exposta",
      riskLevel: "low",
      location: "Cabecalho Server",
      scanner: "Info Disclosure Scanner",
      description:
        "O servidor esta divulgando sua versao exata no cabecalho HTTP Server. Isso pode ajudar atacantes a identificar vulnerabilidades conhecidas para essa versao especifica.",
      evidence: `HTTP/1.1 200 OK\nServer: Apache/2.4.41 (Ubuntu)\nX-Powered-By: PHP/8.1.2`,
      recommendation:
        "Configure o servidor para suprimir a versao nos cabecalhos HTTP. No Apache, use 'ServerTokens Prod' e 'ServerSignature Off'. Remova tambem o cabecalho X-Powered-By.",
    },
    {
      id: "vuln-005",
      name: "CSRF Token Ausente",
      riskLevel: "high",
      location: "Formulario de login em /auth/login",
      scanner: "CSRF Scanner",
      description:
        "O formulario de login nao possui token CSRF, permitindo que atacantes forjem requisicoes em nome do usuario.",
      evidence: `<form action="/auth/login" method="POST">\n  <input type="text" name="username" />\n  <input type="password" name="password" />\n  <button type="submit">Login</button>\n</form>\n\nNenhum campo hidden com token CSRF encontrado.`,
      recommendation:
        "Implemente tokens CSRF em todos os formularios que realizam acoes. Use bibliotecas como csurf para Node.js ou os mecanismos nativos do framework utilizado.",
    },
    {
      id: "vuln-006",
      name: "Porta SSH Aberta",
      riskLevel: "medium",
      location: "Porta 22/TCP",
      scanner: "Port Scanner",
      description:
        "A porta SSH esta aberta e acessivel publicamente. Embora necessaria para administracao, deve ser protegida contra ataques de forca bruta.",
      evidence: `PORT     STATE SERVICE  VERSION\n22/tcp   open  ssh      OpenSSH 8.9\n80/tcp   open  http     Apache 2.4.41\n443/tcp  open  https    Apache 2.4.41\n3306/tcp open  mysql    MySQL 8.0.32\n8080/tcp open  http     Node.js`,
      recommendation:
        "Restrinja o acesso SSH por IP usando firewall. Desative autenticacao por senha e use apenas chaves SSH. Considere mudar a porta padrao e implementar fail2ban.",
    },
    {
      id: "vuln-007",
      name: "Cookie sem Flag HttpOnly",
      riskLevel: "medium",
      location: "Cookie de sessao 'PHPSESSID'",
      scanner: "Cookie Scanner",
      description:
        "O cookie de sessao nao possui a flag HttpOnly, permitindo que scripts do lado do cliente acessem o cookie e potencialmente roubem a sessao.",
      evidence: `Set-Cookie: PHPSESSID=abc123def456; Path=/;\n\nFlags ausentes: HttpOnly, Secure, SameSite`,
      recommendation:
        "Configure todos os cookies de sessao com as flags HttpOnly, Secure e SameSite=Strict. No PHP, ajuste session.cookie_httponly = 1 no php.ini.",
    },
    {
      id: "vuln-008",
      name: "Banco de Dados Exposto",
      riskLevel: "critical",
      location: "Porta 3306/TCP (MySQL)",
      scanner: "Port Scanner",
      description:
        "O servico MySQL esta acessivel publicamente na porta 3306. Isso pode permitir ataques de forca bruta e acesso nao autorizado ao banco de dados.",
      evidence: `PORT     STATE SERVICE  VERSION\n3306/tcp open  mysql    MySQL 8.0.32\n\nBanner: MySQL 8.0.32-0ubuntu0.22.04.2\nAutenticacao: mysql_native_password`,
      recommendation:
        "Bloqueie o acesso externo a porta 3306 usando firewall. Configure o MySQL para escutar apenas em localhost (bind-address = 127.0.0.1). Use SSH tunnel para acesso remoto.",
    },
    {
      id: "vuln-009",
      name: "Directory Listing Habilitado",
      riskLevel: "low",
      location: "/uploads/",
      scanner: "Directory Scanner",
      description:
        "A listagem de diretorios esta habilitada, permitindo que qualquer pessoa veja o conteudo dos diretorios do servidor.",
      evidence: `GET /uploads/ HTTP/1.1\n\n<html>\n<title>Index of /uploads</title>\n<body>\n  <a href="backup.sql">backup.sql</a>\n  <a href="config.php.bak">config.php.bak</a>\n</body>\n</html>`,
      recommendation:
        "Desative a listagem de diretorios no servidor web. No Apache, adicione 'Options -Indexes' no .htaccess ou na configuracao do VirtualHost.",
    },
    {
      id: "vuln-010",
      name: "TLS 1.0/1.1 Habilitado",
      riskLevel: "medium",
      location: "Configuracao SSL/TLS",
      scanner: "SSL Scanner",
      description:
        "O servidor suporta versoes antigas e inseguras do protocolo TLS (1.0 e 1.1), que possuem vulnerabilidades conhecidas.",
      evidence: `Protocolos suportados:\n- TLSv1.0  (INSEGURO)\n- TLSv1.1  (INSEGURO)\n- TLSv1.2  (OK)\n- TLSv1.3  (OK)\n\nCifras fracas detectadas:\n- TLS_RSA_WITH_RC4_128_SHA`,
      recommendation:
        "Desative TLS 1.0 e 1.1 no servidor. Configure apenas TLS 1.2 e 1.3. Remova cifras fracas e use apenas cifras modernas recomendadas.",
    },
    {
      id: "vuln-011",
      name: "Rate Limiting Ausente",
      riskLevel: "high",
      location: "Endpoint /api/auth/login",
      scanner: "Brute Force Scanner",
      description:
        "O endpoint de autenticacao nao possui rate limiting, permitindo ataques de forca bruta ilimitados.",
      evidence: `100 tentativas em 10 segundos:\n\nPOST /api/auth/login HTTP/1.1\n{"username":"admin","password":"tentativa_001"}\n-> 401 Unauthorized (2ms)\n...\n{"username":"admin","password":"tentativa_100"}\n-> 401 Unauthorized (3ms)\n\nNenhum bloqueio ou atraso detectado.`,
      recommendation:
        "Implemente rate limiting no endpoint de login (ex: maximo 5 tentativas por minuto). Use bibliotecas como express-rate-limit ou implemente no nivel do reverse proxy (Nginx).",
    },
    {
      id: "vuln-012",
      name: "Informacao Sensivel no Codigo-Fonte",
      riskLevel: "high",
      location: "Codigo-fonte HTML de /admin",
      scanner: "Source Code Scanner",
      description:
        "Comentarios HTML contendo informacoes sensiveis foram encontrados no codigo-fonte da pagina de administracao.",
      evidence: `<!-- TODO: Remover antes do deploy -->\n<!-- API Key: sk_live_abc123xyz789 -->\n<!-- DB Password: P@ssw0rd123! -->\n<!-- Admin panel: /super-secret-admin -->`,
      recommendation:
        "Remova todos os comentarios com informacoes sensiveis do codigo-fonte. Utilize variaveis de ambiente para armazenar credenciais e nunca as exponha no codigo do lado do cliente.",
    },
    {
      id: "vuln-013",
      name: "Redirecionamento Aberto",
      riskLevel: "medium",
      location: "Parametro 'redirect' em /auth/callback",
      scanner: "Redirect Scanner",
      description:
        "O parametro de redirecionamento aceita URLs externas, permitindo ataques de phishing.",
      evidence: `GET /auth/callback?redirect=https://evil.com/phishing HTTP/1.1\n\nHTTP/1.1 302 Found\nLocation: https://evil.com/phishing`,
      recommendation:
        "Valide todos os URLs de redirecionamento contra uma whitelist de dominios permitidos. Nao permita redirecionamentos para URLs externas arbitrarias.",
    },
    {
      id: "vuln-014",
      name: "Arquivo robots.txt Expoe Rotas",
      riskLevel: "info",
      location: "/robots.txt",
      scanner: "Info Disclosure Scanner",
      description:
        "O arquivo robots.txt revela a existencia de diretorios sensiveis como /admin e /api/internal.",
      evidence: `User-agent: *\nDisallow: /admin/\nDisallow: /api/internal/\nDisallow: /backup/\nDisallow: /config/`,
      recommendation:
        "Revise o robots.txt para nao revelar caminhos sensiveis. Use autenticacao e controle de acesso adequados em vez de depender do robots.txt para ocultar conteudo.",
    },
  ],
  distribution: {
    critical: 2,
    high: 4,
    medium: 5,
    low: 2,
    info: 1,
  },
  technologies: {
    server: "Apache 2.4.41",
    language: "PHP 8.1.2",
    framework: "Laravel 10.x",
    os: "Ubuntu 22.04 LTS",
    cms: "Nenhum detectado",
  },
  logEntries: [
    "[14:30:01] Iniciando scan em https://exemplo.com.br...",
    "[14:30:01] Tipo de scan: Completo",
    "[14:30:02] Resolvendo DNS para exemplo.com.br...",
    "[14:30:02] IP resolvido: 203.0.113.42",
    "[14:30:03] === Iniciando Port Scanner ===",
    "[14:30:05] Porta 22/tcp aberta - SSH (OpenSSH 8.9)",
    "[14:30:05] Porta 80/tcp aberta - HTTP (Apache 2.4.41)",
    "[14:30:06] Porta 443/tcp aberta - HTTPS (Apache 2.4.41)",
    "[14:30:07] Porta 3306/tcp aberta - MySQL (8.0.32)",
    "[14:30:07] [CRITICO] MySQL exposto publicamente na porta 3306",
    "[14:30:08] Porta 8080/tcp aberta - HTTP (Node.js)",
    "[14:30:08] Port Scanner concluido - 5 portas abertas",
    "[14:30:09] === Iniciando Technology Detection ===",
    "[14:30:10] Servidor: Apache/2.4.41 (Ubuntu)",
    "[14:30:10] Linguagem: PHP/8.1.2",
    "[14:30:11] Framework: Laravel 10.x (detectado via X-Powered-By e padrao de rotas)",
    "[14:30:11] Technology Detection concluido",
    "[14:30:12] === Iniciando SQL Injection Scanner ===",
    "[14:30:15] Testando parametro 'id' em /api/users...",
    "[14:30:16] [CRITICO] SQL Injection encontrado em /api/users?id=1' OR '1'='1",
    "[14:30:18] SQL Injection Scanner concluido - 1 vulnerabilidade encontrada",
    "[14:30:19] === Iniciando XSS Scanner ===",
    "[14:30:22] Testando campo de busca em /search...",
    "[14:30:23] [ALTO] XSS Refletido encontrado em /search?q=<script>",
    "[14:30:25] XSS Scanner concluido - 1 vulnerabilidade encontrada",
    "[14:30:26] === Iniciando Header Scanner ===",
    "[14:30:27] Analisando cabecalhos HTTP...",
    "[14:30:28] [MEDIO] Cabecalhos de seguranca ausentes detectados",
    "[14:30:28] Header Scanner concluido",
    "[14:30:29] === Iniciando SSL Scanner ===",
    "[14:30:31] [MEDIO] TLS 1.0 e 1.1 habilitados",
    "[14:30:31] [MEDIO] Cifras fracas detectadas",
    "[14:30:32] SSL Scanner concluido",
    "[14:30:33] === Iniciando CSRF Scanner ===",
    "[14:30:35] [ALTO] Token CSRF ausente em /auth/login",
    "[14:30:35] CSRF Scanner concluido",
    "[14:30:36] === Iniciando Brute Force Scanner ===",
    "[14:30:40] [ALTO] Rate limiting ausente em /api/auth/login",
    "[14:30:40] Brute Force Scanner concluido",
    "[14:30:41] === Iniciando Directory Scanner ===",
    "[14:30:43] [BAIXO] Directory listing habilitado em /uploads/",
    "[14:30:43] Directory Scanner concluido",
    "[14:30:44] === Gerando relatorio final ===",
    "[14:30:44] Score de risco calculado: 72/100",
    "[14:30:44] Total de vulnerabilidades: 14",
    "[14:30:44] Scan completo finalizado com sucesso.",
  ],
}

export const mockScanHistory: ScanHistoryEntry[] = [
  {
    id: "scan-001",
    target: "https://exemplo.com.br",
    date: "2026-02-26T14:30:00Z",
    riskScore: 72,
    scanType: "Completo",
    status: "completed",
  },
  {
    id: "scan-002",
    target: "https://loja.exemplo.com.br",
    date: "2026-02-25T09:15:00Z",
    riskScore: 45,
    scanType: "Rapido",
    status: "completed",
  },
  {
    id: "scan-003",
    target: "https://api.exemplo.com.br",
    date: "2026-02-24T16:00:00Z",
    riskScore: 88,
    scanType: "Completo",
    status: "completed",
  },
  {
    id: "scan-004",
    target: "https://blog.exemplo.com.br",
    date: "2026-02-23T11:30:00Z",
    riskScore: 23,
    scanType: "Rapido",
    status: "completed",
  },
  {
    id: "scan-005",
    target: "https://painel.exemplo.com.br",
    date: "2026-02-22T08:45:00Z",
    riskScore: 61,
    scanType: "Completo",
    status: "completed",
  },
]

export const scanners = [
  { id: "port", name: "Port Scanner", duration: 5 },
  { id: "tech", name: "Technology Detection", duration: 3 },
  { id: "sqli", name: "SQL Injection Scanner", duration: 6 },
  { id: "xss", name: "XSS Scanner", duration: 6 },
  { id: "headers", name: "Header Scanner", duration: 2 },
  { id: "ssl", name: "SSL Scanner", duration: 3 },
  { id: "csrf", name: "CSRF Scanner", duration: 2 },
  { id: "brute", name: "Brute Force Scanner", duration: 4 },
  { id: "dir", name: "Directory Scanner", duration: 2 },
]

export function getRiskColor(level: RiskLevel): string {
  const colors: Record<RiskLevel, string> = {
    critical: "text-risk-critical",
    high: "text-risk-high",
    medium: "text-risk-medium",
    low: "text-risk-low",
    info: "text-risk-info",
  }
  return colors[level]
}

export function getRiskBgColorClass(level: RiskLevel): string {
  const colors: Record<RiskLevel, string> = {
    critical: "bg-risk-critical",
    high: "bg-risk-high",
    medium: "bg-risk-medium",
    low: "bg-risk-low",
    info: "bg-risk-info",
  }
  return colors[level]
}

export function getRiskLabel(level: RiskLevel | string): string {
  const labels: Record<string, string> = {
    critical: "Critico",
    high: "Alto",
    medium: "Medio",
    low: "Baixo",
    info: "Info",
  }
  return labels[level] || "Desconhecido"
}

export function getScoreColor(score: number): string {
  if (score >= 80) return "text-risk-critical"
  if (score >= 60) return "text-risk-high"
  if (score >= 40) return "text-risk-medium"
  if (score >= 20) return "text-risk-low"
  return "text-risk-info"
}

export function getScoreStrokeColor(score: number): string {
  if (score >= 80) return "var(--risk-critical)"
  if (score >= 60) return "var(--risk-high)"
  if (score >= 40) return "var(--risk-medium)"
  if (score >= 20) return "var(--risk-low)"
  return "var(--risk-info)"
}

    