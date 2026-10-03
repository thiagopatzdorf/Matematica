# Como reproduzir a validação de K_7(9,4) ≤ 1137

Tudo roda em CPU local; não precisa de nuvem. Medido num contêiner com 4 núcleos e 15 GB.

## 0. Requisitos

- Linux, `gcc` com OpenMP (testado com 13.3), `rustc` (testado com 1.97), Python 3 com NumPy (testado
  com 3.11 e NumPy 2.4.6).
- Para o Lean: `elan`. O toolchain é fixado em `lean-toolchain` (Lean 4.34.1) e o Mathlib em
  `lake-manifest.json`.

## 1. Witness (segundos)

```bash
cd artifacts/k7_9_4_1137 && sha256sum -c SHA256SUMS && cd -
python3 verification/validate_witness.py artifacts/k7_9_4_1137/code_1137.txt 1137
# PASS formato: q=7 n=9 |C|=1137, 0 duplicatas, 0 inválidas
# sha256 = df3e8d527bc393a9680fe4b2b39e7bde088ab6a02f2f94ee26019a5efc05a102
```

## 2. Os três verificadores, a redundância e as mutações (~12 min)

```bash
verification/run_all.sh
```

O script faz o seguinte, um passo por vez, e para no primeiro erro:

| passo | programa | tempo medido | memória de pico |
|---|---|---|---|
| A: força bruta, `d(x,C)` para os 7^9 pontos | `verify_bruteforce.c` (C/OpenMP) | 233 s (4 núcleos) | 10 MB |
| B: união das bolas de raio 0..4 | `verify_balls.py` (NumPy) | 126–302 s | 1,6 GB |
| C: BFS multifonte no grafo de Hamming | `verify_bfs/main.rs` (Rust) | 18 s | 197 MB |
| redundância individual de cada palavra | `redundancy_check.c` | 319 s | 10 MB |
| 8 mutações destrutivas | `run_mutations.py` (usa o C) | ~1 min | — |
| estrutura 3 × 343 + 108 | `structure_check.py` | ~5 s | — |

Os três verificadores têm de imprimir a mesma distribuição:

```
N_0 = 1137
N_1 = 61225
N_2 = 1421934
N_3 = 15340089
N_4 = 23529222
total = 40353607   uncovered = 0   max_distance = 4
PASS
```

As saídas desta rodada estão em `verification/outputs/`.

## 3. Lean (build do zero)

```bash
lake exe cache get        # baixa o Mathlib pré-compilado da versão fixada
lake clean CoveringLean   # limpa só o projeto (`lake clean` sem argumento apaga também o Mathlib
                          # e obriga a recompilá-lo do fonte, o que leva horas)
lake build CoveringSyn    # certificados por síndromes (fora do alvo padrão), incluindo Syn_K1137
```

Para conferir o enunciado e os axiomas:

```lean
import CoveringLean.Syn_K1137
#check @Syn.K7_9_4_le_1137_syn
#print axioms Syn.K7_9_4_le_1137_syn   -- [propext, Classical.choice, Quot.sound]
```

Atenção: `lake build` sozinho **não** compila o teorema, porque `Syn_K1137` está fora do alvo padrão.
Medido: 318 s, com pico de 6,8 GB num processo, em 4 núcleos.

Para conferir que a lista de palavras dentro do Lean é o witness:

```bash
python3 verification/lean/decode_synData.py .   # sha256 df3e8d52…a102, idêntico a code_1137.txt
```

Detalhes, tempos e logs estão em `LEAN_REVIEW.md`. Os ataques ao Lean estão em `LEAN_RED_TEAM.md`.
