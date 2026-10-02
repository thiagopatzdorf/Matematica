# Como reproduzir a varredura de bases de K_7(9,4)

Os programas estão na branch `feat/kit-de-busca` deste repositório, no commit fixado em
`COMPUTE_CERTIFICATE.json` (campo `kit_commit`). Requisitos: Linux, gcc e Python 3.12.

```bash
git clone -b feat/kit-de-busca https://github.com/thiagopatzdorf/Matematica.git kit && cd kit
git checkout <kit_commit>
gcc -O3 -march=native -o bs scripts/search/base_search.c -lm
gcc -O3 -march=native -o vt scripts/audit/verify_trios.c        # verificador independente
```

## 1. Lista das classes não degeneradas (≈ 1 min)

```bash
./bs enum 7 9 3 4 1 0 > classes.jsonl              # 6362 linhas
python3 - <<'EOF'
import json
L = [json.loads(l) for l in open('classes.jsonl')]
L.sort(key=lambda d: (d['nBc'], d['A']))
open('classes_sorted.jsonl', 'w').write(''.join(json.dumps(d) + '\n' for d in L))
EOF
sha256sum classes_sorted.jsonl   # 4e2035d93538f808e679771be576c2046d59672bc70657d1e45e5b491ce7bad1
```

## 2. Completude da lista e classes degeneradas (≈ 2 min)

```bash
cd scripts/audit
python3 verify_list.py ../../classes_sorted.jsonl /tmp/r.json            # fórmula de massa, duplicatas
python3 degenerate.py /tmp/deg.jsonl /tmp/deg_summary.json               # 1375 degeneradas
```

## 3. Mínimo de órfãs por classe (≈ 20 s por classe num núcleo físico)

```bash
A=$(sed -n "${L}p" classes_sorted.jsonl | python3 -c 'import sys,json;print(json.load(sys.stdin)["A"])')
./bs exactT2 7 9 4 8 "$A" 18 1000 1     # última linha: JSON com "orphans" (-1 = nenhum trio <= 8)
```

- Para as degeneradas, troque a lista por `data/audit/degenerate_classes.jsonl`.
- Custo medido: 6362 classes em ~1 h 50 min de relógio, 3 × t2d-standard-8 spot, ~US$1,0. As
  1375 degeneradas custaram ~20 min.

## 4. Conferência

```bash
python3 scripts/audit/ledger_sweep.py <dir com classes_sorted.jsonl e fz-*/c_L.out>   # missing/duplicates
gcc -O2 -o test_swar scripts/audit/test_swar.c -lm && ./test_swar                      # SWAR
# diferencial: para cada classe L da amostra, rode ./bs exactT, ./bs exactT2 e ./vt com o mesmo T e compare:
python3 scripts/audit/compare_diff.py <dir> 8 <L1> <L2> ...
```

## 5. Verificação independente de uma classe sem o motor otimizado

```bash
./vt 7 9 4 8 "$A"    # bola, aritmética e canonização próprias; sem blocos, simetria ou SWAR
```

O `vt` é o "verificador pequeno": cerca de 150 linhas de C, cuja exatidão é argumentada no
cabeçalho do arquivo. Ele custa ~2–6 min por classe. Rodá-lo nas 7737 classes reproduziria a
varredura inteira sem depender do `exactT2`. Isso não foi feito nesta rodada; o custo estimado está
em `FINAL_AUDIT.md`.
