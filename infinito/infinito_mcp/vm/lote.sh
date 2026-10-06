#!/bin/bash
# Startup-script das VMs efêmeras do lote (infinito_mcp/executor_lote.py): roda UM shard e DESLIGA a máquina.
# Quem cria a VM, põe este script e o job (`infinito-job`) é o executor; quem a apaga também (ou o próprio Compute,
# pelo maxRunDuration com instanceTerminationAction=DELETE).
#
# Travas, todas aqui dentro da VM (o servidor já validou, mas a VM não confia nele):
# * allowlist de tipos; parâmetros por regex; o comando nunca vem do pedido;
# * `script` só roda `pesado/jobs/<nome>.sh` de um commit que JÁ ESTÁ na main (`merge-base --is-ancestor`):
#   empurrar um branch com script novo não basta, tem de passar por PR e merge do dono;
# * sem service account: log e saída sobem por URL assinada de UM objeto, se o executor mandou;
# * sem job nos metadados (boot manual): não faz nada. Mesmo job duas vezes (reboot): ignora.
set -u
MD=http://metadata.google.internal/computeMetadata/v1
H="Metadata-Flavor: Google"
JOB=$(curl -fs -H "$H" "$MD/instance/attributes/infinito-job") || exit 0
STATE=/var/lib/infinito; mkdir -p "$STATE"
campo() { python3 -c 'import json,sys;v=json.loads(sys.argv[1]).get(sys.argv[2]);print("" if v is None else v)' "$JOB" "$1"; }
ID=$(campo id) || exit 0
SHARD=$(campo shard); TOTAL=$(campo total)
[ "$(cat "$STATE/feito" 2>/dev/null)" = "$ID-$SHARD" ] && exit 0
echo "$ID-$SHARD" > "$STATE/feito"
put() { curl -fs -X PUT -H "$H" --data-binary "$2" "$MD/instance/guest-attributes/infinito/$1" >/dev/null; }
put id "$ID"; put shard "$SHARD"; put inicio "$(date +%s)"; put estado rodando

# Saída: tipo, commit pedido (ou vazio = main) e o corpo do comando, separados por TAB. Recusa = código 2.
LINHA=$(python3 - "$JOB" <<'PY'
import json, re, shlex, sys
j = json.loads(sys.argv[1]); tipo = j["tipo"]; p = j.get("params") or {}
commit = str(p.get("commit", "") or "")
if commit and not re.fullmatch(r"[0-9a-f]{7,40}", commit):
    sys.exit(2)
if tipo == "lake_build":
    alvo = str(p.get("alvo", ""))
    if alvo and not re.fullmatch(r"[A-Za-z0-9_.]{1,80}", alvo):
        sys.exit(2)
    corpo = f"(lake exe cache get || true) && lake build {alvo}".strip()
elif tipo == "verificar_grande":
    arq = str(p.get("arquivo", ""))
    if not re.fullmatch(r"q\d+_n\d+_R\d+_M\d+\.txt", arq):
        sys.exit(2)
    corpo = f"gcc -O2 -o /tmp/verify tools/verify/verify.c && /tmp/verify data/codes/{arq}"
elif tipo == "script":
    nome = str(p.get("nome", ""))
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,39}", nome):
        sys.exit(2)
    corpo = f"test -f pesado/jobs/{nome}.sh && bash pesado/jobs/{nome}.sh"
else:
    sys.exit(2)
print(f"{tipo}\t{commit}\t{corpo}")
PY
) || { put codigo 2; put saida "job recusado pela allowlist da VM"; put fim "$(date +%s)"; put estado concluido; shutdown -h now; exit 0; }
COMMIT=$(printf '%s' "$LINHA" | cut -f2); CORPO=$(printf '%s' "$LINHA" | cut -f3-)
HORAS=$(campo horas)
SEG=$(python3 -c 'import sys;print(max(60,int(float(sys.argv[1])*3600)))' "$HORAS")

export HOME=/root PATH=/root/.elan/bin:$PATH
export SHARD_INDEX="$SHARD" SHARD_TOTAL="$TOTAL" JOB_ID="$ID" SAIDA="$STATE/saida"
mkdir -p "$SAIDA"
LOG="$STATE/$ID-$SHARD.log"; : > "$LOG"
# Subshell, não chaves: um `exit` de recusa aqui dentro não pode pular a gravação do resultado lá embaixo.
(
  command -v git >/dev/null && command -v gcc >/dev/null || { apt-get update -qq && apt-get install -y -qq git gcc curl; }
  command -v lake >/dev/null || { curl -sSf https://elan.lean-lang.org/elan-init.sh | sh -s -- -y --default-toolchain none; }
  REPO=/opt/infinito/Matematica
  [ -d "$REPO/.git" ] || git clone -q -b main https://github.com/thiagopatzdorf/Matematica "$REPO"
  cd "$REPO" || exit 3
  [ -f .git/shallow ] && git fetch -q --unshallow origin main
  git fetch -q origin main || exit 3
  ALVO=${COMMIT:-origin/main}
  # Só commit que a main já contém: é o que torna "script" uma allowlist revisada, não um comando livre.
  git merge-base --is-ancestor "$ALVO" origin/main || { echo "commit $ALVO fora da main: recusado"; exit 2; }
  git -c advice.detachedHead=false checkout -q --force "$ALVO" && git clean -qfdx -e .lake || exit 3
  echo "== shard $SHARD_INDEX/$SHARD_TOTAL, commit $(git rev-parse HEAD)"
  timeout "$SEG" bash -c "$CORPO"
) >> "$LOG" 2>&1
CODIGO=$?
put codigo "$CODIGO"
put saida "$(tail -c 3000 "$LOG" | iconv -c -t utf-8)"
URL_LOG=$(campo url_log); URL_SAIDA=$(campo url_saida)
[ -n "$URL_LOG" ] && curl -fs -X PUT -H "Content-Type: text/plain" --data-binary "@$LOG" "$URL_LOG" >/dev/null && put log_no_bucket 1
if [ -n "$URL_SAIDA" ] && [ -n "$(ls -A "$SAIDA")" ]; then
  tar -czf "$STATE/saida.tar.gz" -C "$SAIDA" . && curl -fs -X PUT -H "Content-Type: application/gzip" \
    --data-binary "@$STATE/saida.tar.gz" "$URL_SAIDA" >/dev/null && put saida_no_bucket 1
fi
put fim "$(date +%s)"; put estado concluido
sync; shutdown -h now
