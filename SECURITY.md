# Segurança

## Como relatar

Escreva para o e-mail da pessoa mantenedora que consta em `CITATION.cff` (thiagosleman@gmail.com), com assunto
`[segurança] Matematica` e: o que você viu, como reproduzir, o que isso permite e, se souber, como corrigir. **Não abra
issue pública** nem poste o achado em PR, chat ou rede social antes da correção. Respondemos o mais rápido possível e
creditamos quem relata, se a pessoa quiser. Não há programa de recompensa.

## O que é segredo

Tem de ficar fora do Git, de log, de issue e de tela:

* o **token de URL** do Infinito (a URL pessoal `https://<host>/mcp/<token>/` é a senha) e o token de administrador;
* chaves de API (por exemplo a do Gemini), tokens do Zenodo e do GitHub, credenciais de nuvem e de service account;
* qualquer cookie ou URL assinada, e caminhos ou IPs de máquinas internas.

Se um segredo vazou, **avise primeiro** e trate como queimado: o administrador revoga o acesso (no Infinito, a pessoa
é cortada sem afetar as outras) e o segredo é trocado. Apagar o commit não basta, porque o histórico é público.
Para conferir que um segredo existe, mostre o tamanho dele, nunca o valor.

## Escopo

Dentro do escopo:

* **o MCP Infinito** (`infinito/`): autenticação por token, o teto de crédito por pessoa, a allowlist de trabalhos
  pesados, vazamento de token em log, qualquer jeito de gastar além do teto ou de ler dado de outra pessoa;
* **o CI** (`.github/workflows/`): ações não fixadas, permissões amplas demais, injeção por título de PR ou nome de
  branch, vazamento de segredo em log;
* o que o repositório executa em máquina de quem contribui (scripts, verificador em C, geradores).

Fora do escopo: a correção matemática de um resultado (isso é revisão, abra uma issue pública), vulnerabilidade em
Lean, Mathlib, GitHub, Cloudflare ou Google Cloud (relate a quem as mantém) e ataque que exija acesso físico.

## Versões

Só a branch `main` recebe correção. Resultados já publicados no Zenodo ficam como estão.
