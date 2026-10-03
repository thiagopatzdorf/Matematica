# Pacote de auditoria: q7_n9_R4_M1285

- SHA-256 do arquivo: `89cbd6b290a10d8d708e9783a405b8a12ce5efd6a8ea2ee17568b3ee25c50f31`
- commit auditado (clone limpo): `86f02a9bf64954646b4e53e706fd134b15f350f0`
- 1285 linhas, 1285 distintas, 40353607 pontos no espaço
- comando: `git clone <repo> && git checkout 86f02a9bf64954646b4e53e706fd134b15f350f0 && python3 tools/campaign/audit_package.py q7_n9_R4_M1285`
- ambiente: {"os": "Linux-6.18.44-fc-v64-x86_64-with-glibc2.39", "python": "3.11.15", "numpy": "2.4.6", "gcc": "cc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0", "rustc": "rustc 1.97.0 (2d8144b78 2026-07-07)", "go": "go version go1.24.7 linux/amd64", "cpu": "Intel(R) Xeon(R) Processor @ 2.10GHz", "nproc": 4}

| verificador | exit | tempo (s) | pico RSS (MB) | saída |
|---|---|---|---|---|
| verify-c (C, bolas/bitset) | 0 | 0.398 | 16.4 | `q=7 n=9 R=4 M=1285 points=40353607 uncovered=0 sha256=aa388cc9642bc064527a0237b60522ba558491291a2adf02ab1e4d8d` |
| verify-rust (Rust, dilatação por camadas) | 0 | 1.627 | 117.5 | `COVERS q=7 n=9 R=4 M=1285 points=40353607 uncovered=0` |
| verify-py-dilation (Python/numpy) | 0 | 1.978 | 112.4 | `q=7 n=9 R=4 M=1285 points=40353607 uncovered=0 sha256=aa388cc9642bc064527a0237b60522ba558491291a2adf02ab1e4d8d` |
| verify-cleanroom (Go, BFS multi-fonte) | 0 | 4.797 | 194.6 | `COBRE q=7 n=9 R=4 M=1285 points=40353607 uncovered=0` |

## Testes negativos (exit por verificador, na ordem acima)

- uma_palavra_removida, M intacto (#distintas != M => exit 2): [2, 2, 2, 2]
- duplicata (exit 2): [2, 2, 2, 2]
- simbolo_invalido (dígito >= q => exit 2): [2, 2, 2, 2]
- comprimento_errado (exit 2): [2, 2, 2, 2]
- R-1, arquivo com nome neutro (cobertura falha => exit 1): [1, 1, 1, 1]
- R-1, arquivo com o nome original (verify-c: exit 2 por contradizer o nome; os outros: 1): [2, 1, 1, 1]
- M-1 declarado (exit 2): [2, 2, 2, 2]
