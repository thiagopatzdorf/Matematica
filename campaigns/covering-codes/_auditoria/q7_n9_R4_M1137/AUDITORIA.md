# Pacote de auditoria: q7_n9_R4_M1137

- SHA-256 do arquivo: `df3e8d527bc393a9680fe4b2b39e7bde088ab6a02f2f94ee26019a5efc05a102`
- commit auditado (clone limpo): `780377cc50de8cda02db2da3ec8ba416aeac9e08`
- 1137 linhas, 1137 distintas, 40353607 pontos no espaço
- comando: `git clone <repo> && git checkout 780377cc50de8cda02db2da3ec8ba416aeac9e08 && python3 tools/campaign/audit_package.py q7_n9_R4_M1137`
- ambiente: {"os": "Linux-6.18.44-fc-v64-x86_64-with-glibc2.39", "python": "3.11.15", "numpy": "2.4.6", "gcc": "cc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0", "rustc": "rustc 1.97.0 (2d8144b78 2026-07-07)", "go": "go version go1.24.7 linux/amd64", "cpu": "Intel(R) Xeon(R) Processor @ 2.10GHz", "nproc": 4}

| verificador | exit | tempo (s) | pico RSS (MB) | saída |
|---|---|---|---|---|
| verify-c (C, bolas/bitset) | 0 | 0.388 | 15.8 | `q=7 n=9 R=4 M=1137 points=40353607 uncovered=0 sha256=df3e8d527bc393a9680fe4b2b39e7bde088ab6a02f2f94ee26019a5e` |
| verify-rust (Rust, dilatação por camadas) | 0 | 2.149 | 117.5 | `COVERS q=7 n=9 R=4 M=1137 points=40353607 uncovered=0` |
| verify-py-dilation (Python/numpy) | 0 | 3.82 | 112.2 | `q=7 n=9 R=4 M=1137 points=40353607 uncovered=0 sha256=df3e8d527bc393a9680fe4b2b39e7bde088ab6a02f2f94ee26019a5e` |
| verify-cleanroom (Go, BFS multi-fonte) | 0 | 4.599 | 194.7 | `COBRE q=7 n=9 R=4 M=1137 points=40353607 uncovered=0` |

## Testes negativos (exit por verificador, na ordem acima)

- uma_palavra_removida, M intacto (#distintas != M => exit 2): [2, 2, 2, 2]
- duplicata (exit 2): [2, 2, 2, 2]
- simbolo_invalido (dígito >= q => exit 2): [2, 2, 2, 2]
- comprimento_errado (exit 2): [2, 2, 2, 2]
- R-1, arquivo com nome neutro (cobertura falha => exit 1): [1, 1, 1, 1]
- R-1, arquivo com o nome original (verify-c: exit 2 por contradizer o nome; os outros: 1): [2, 1, 1, 1]
- M-1 declarado (exit 2): [2, 2, 2, 2]
