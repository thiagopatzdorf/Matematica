#!/bin/bash
# Fumaça do lote: prova que a VM subiu da imagem, achou o repo no commit pedido e devolve arquivo pelo bucket.
# Custa minutos. Rode antes do primeiro job de verdade: pesado("script", 0.2, {"nome": "fumaca"}, paralelo=2).
# Ambiente (posto pelo vm/lote.sh): SHARD_INDEX, SHARD_TOTAL, JOB_ID, SAIDA (pasta que sobe como .tar.gz).
set -eu
echo "shard ${SHARD_INDEX}/${SHARD_TOTAL} do job ${JOB_ID} em $(hostname)"
echo "commit $(git rev-parse HEAD); $(nproc) vCPU; $(free -g | awk '/Mem:/{print $2}') GiB"
command -v lake >/dev/null && lake --version || echo "lake ausente na imagem"
printf '{"shard": %s, "total": %s, "commit": "%s"}\n' "$SHARD_INDEX" "$SHARD_TOTAL" "$(git rev-parse HEAD)" > "$SAIDA/shard.json"
