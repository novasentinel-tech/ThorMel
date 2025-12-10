# 🧠 IA Pentest Master - Ferramenta Educacional de Cibersegurança 🛡️

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Educacional-green?style=for-the-badge)
![License](https://img.shields.io/badge/Licen%C3%A7a-MIT-purple?style=for-the-badge)

Uma ferramenta de pentest educacional, impulsionada por IA, com scanners **reais e funcionais** projetados para operar de forma segura. Ideal para aprender a identificar vulnerabilidades em um ambiente controlado, sem realizar ataques destrutivos. 🚀

---

> ## ⚠️ AVISO IMPORTANTE: PROJETO ESTRITAMENTE EDUCACIONAL ⚠️
>
> Esta ferramenta, embora **totalmente funcional**, foi desenvolvida **exclusivamente para fins educacionais**. Seu objetivo é ensinar como scanners de vulnerabilidade operam para identificar falhas de segurança de forma ética e controlada.
>
> - **NÃO UTILIZE** contra sistemas, sites ou infraestruturas para os quais você **NÃO POSSUA AUTORIZAÇÃO** explícita. O uso não autorizado de ferramentas de pentest é **ilegal**.
> - O autor e os contribuidores **NÃO SE RESPONSABILIZAM** por qualquer uso indevido, danos ou consequências legais resultantes do mau uso desta ferramenta.
> - **O FOCO É A DETECÇÃO, NÃO A EXPLORAÇÃO:** Este projeto não contém exploits reais. Módulos de "ataque" são simulados para fins didáticos. O código foi projetado para ser "safe-by-default".

---

## ✨ Funcionalidades e Scanners Implementados

> 🔍 **Nota Técnica:** Quando executado em ambientes cloud (ex.: Firebase Studio), o código roda dentro de containers que podem:
> - Redirecionar tráfego via IP compartilhado
> - Apresentar logs de proxies internos
> - Bloquear iframes ou conteúdo externo no navegador
>
> **Isso é normal** e não significa que a IA está acessando servidores sem autorização.

Este projeto implementa uma suíte de scanners passivos e semi-passivos **funcionais** para identificar potenciais vulnerabilidades, com foco na análise e não na exploração.

-   💉 **SQL Injection (Safe Mode):** Detecta padrões de erro e anomalias que **sugerem** vulnerabilidades de SQLi, sem executar queries destrutivas.
-   🎭 **XSS (Safe Mode):** Identifica pontos de reflexão de dados em parâmetros e analisa o contexto, mas **não executa** scripts no navegador.
-   📂 **Directory Traversal:** Testa parâmetros comumente vulneráveis para detectar possíveis vazamentos de caminhos de arquivos do sistema.
-   🔒 **Header Security:** Analisa os headers de segurança HTTP e avalia sua implementação em relação às boas práticas (OWASP).
-   📜 **SSL/TLS Scanner:** Verifica a validade, data de expiração e protocolos do certificado SSL/TLS do alvo.
-   🚪 **Port Scanner:** Realiza um scan de portas TCP para identificar serviços abertos.
-   📝 **Form Analyzer:** Analisa formulários em busca de falhas de segurança comuns, como ausência de tokens CSRF e autocomplete em campos sensíveis.

> 💡 **Modo Seguro por Design:** Todos os scanners operam em um modo que prioriza a **detecção e a inferência**, garantindo que nenhuma operação destrutiva seja executada. Funcionalidades de ataque direto (como no `MainAttack.py`) são **simuladas** para fins didáticos, não realizando explorações reais.

## 🎯 Objetivos de Aprendizagem

Ao estudar este projeto, você poderá:

-   **Compreender a Arquitetura:** Entender como uma ferramenta de pentest real é estruturada, desde a orquestração até os scanners individuais.
-   **Implementar Scanners:** Aprender as técnicas por trás da detecção de diferentes tipos de vulnerabilidades de forma segura.
-   **Praticar Pentest Ético:** Desenvolver uma mentalidade de segurança, focando na identificação e mitigação de riscos de forma responsável.

## 📂 Estrutura do Projeto

```
cyberseguranca/
├── IA_main.py             # 🧠 Cérebro principal e orquestrador dos scans
├── MainAttack.py          # 🎯 (SIMULADO) Motor de exploração, sem exploits reais
├── config.py              # 🛠️ Configurações detalhadas dos scanners e payloads
├── scans/                 # 📂 Módulo com todos os scanners individuais
│   ├── base_scanner.py
│   ├── sql_injection.py
│   ├── xss_scanner.py
│   ├── directory_traversal.py
│   ├── header_security.py
│   ├── ssl_scanner.py
│   ├── port_scanner.py
│   └── form_analyzer.py
├── relatorios/            # 📄 Diretório onde os relatórios JSON são salvos
└── requirements.txt       # 📦 Dependências Python do projeto
```

## 🚀 Instalação e Execução (Ambiente Local)

**Siga estas instruções APENAS em um ambiente de teste local e controlado.**

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd <NOME_DO_PROJETO>
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Crie o ambiente na raiz do projeto
    python -m venv venv

    # Ative o ambiente
    # No Windows:
    # venv\Scripts\activate
    # No macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r cyberseguranca/requirements.txt
    ```

4.  **Execute o Scan:**
    Utilize o script `IA_main.py` para iniciar uma análise. **APONTE APENAS PARA APLICAÇÕES LOCAIS DE TESTE (ex: `http://localhost:3000`).**

    ```bash
    # Exemplo de comando para análise simples
    python cyberseguranca/IA_main.py http://localhost:3000 analise

    # Exemplo para análise com simulação de exploração
    python cyberseguranca/IA_main.py http://localhost:3000 analise_exploracao
    ```
    Os relatórios detalhados serão salvos na pasta `cyberseguranca/relatorios/`.

---

## ⚖️ Licença e Responsabilidade

Este projeto é distribuído sob a **Licença MIT**. Veja o arquivo `LICENSE` para mais detalhes.

Ao utilizar este software, você concorda que é o **único responsável por suas ações**. Os desenvolvedores não têm qualquer responsabilidade e não são responsáveis por qualquer uso indevido ou dano causado por este programa. **Use com ética e responsabilidade.**
