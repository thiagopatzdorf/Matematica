# Pacote de auditoria: q7_n9_R4_M1141

- SHA-256 do arquivo: `315692c9c722de4a9865727d8f02419c1e93701f0109683d0574af6b15685e67`
- commit auditado (clone limpo): `780377cc50de8cda02db2da3ec8ba416aeac9e08`
- 1141 linhas, 1141 distintas, 40353607 pontos no espaço
- comando: `git clone <repo> && git checkout 780377cc50de8cda02db2da3ec8ba416aeac9e08 && python3 tools/campaign/audit_package.py q7_n9_R4_M1141`
- ambiente: {"os": "Linux-6.18.44-fc-v64-x86_64-with-glibc2.39", "python": "3.11.15", "numpy": "2.4.6", "gcc": "cc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0", "rustc": "rustc 1.97.0 (2d8144b78 2026-07-07)", "go": "go version go1.24.7 linux/amd64", "cpu": "Intel(R) Xeon(R) Processor @ 2.10GHz", "nproc": 4}

| verificador | exit | tempo (s) | pico RSS (MB) | saída |
|---|---|---|---|---|
| verify-c (C, bolas/bitset) | 0 | 0.328 | 16.5 | `q=7 n=9 R=4 M=1141 points=40353607 uncovered=0 sha256=bcb05960410d3f32ccd0de46720606a6df3d0402cb56c67e93766f12` |
| verify-rust (Rust, dilatação por camadas) | 0 | 1.552 | 117.6 | `COVERS q=7 n=9 R=4 M=1141 points=40353607 uncovered=0` |
| verify-py-dilation (Python/numpy) | 0 | 1.648 | 112.4 | `q=7 n=9 R=4 M=1141 points=40353607 uncovered=0 sha256=bcb05960410d3f32ccd0de46720606a6df3d0402cb56c67e93766f12` |
| verify-cleanroom (Go, BFS multi-fonte) | 0 | 4.024 | 194.6 | `COBRE q=7 n=9 R=4 M=1141 points=40353607 uncovered=0` |

## Testes negativos (exit por verificador, na ordem acima)

- uma_palavra_removida, M intacto (#distintas != M => exit 2): [2, 2, 2, 2]
- duplicata (exit 2): [2, 2, 2, 2]
- simbolo_invalido (dígito >= q => exit 2): [2, 2, 2, 2]
- comprimento_errado (exit 2): [2, 2, 2, 2]
- R-1, arquivo com nome neutro (cobertura falha => exit 1): [1, 1, 1, 1]
- R-1, arquivo com o nome original (verify-c: exit 2 por contradizer o nome; os outros: 1): [2, 1, 1, 1]
- M-1 declarado (exit 2): [2, 2, 2, 2]
