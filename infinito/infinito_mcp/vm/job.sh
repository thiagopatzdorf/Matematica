#!/bin/bash
# Startup-script da lean-build2: roda UM job por boot e DESLIGA a máquina. Quem põe este script e o job é o
# executor (infinito_mcp/executor_vm.py), pelos metadados `startup-script` e `infinito-job`.
#
# Sem job nos metadados (boot manual): não faz nada e não desliga. Mesmo job duas vezes (reboot): ignora.
# A VM não tem service account: o resultado sai por guest attributes (namespace `infinito`), que o executor lê.
# O job é uma ALLOWLIST (tipo + parâmetros validados por regex), nunca um comando livre.
set -u
MD=http://metadata.google.internal/computeMetadata/v1
H="Metadata-Flavor: Google"
JOB=$(curl -fs -H "$H" "$MD/instance/attributes/infinito-job") || exit 0
STATE=/var/lib/infinito; mkdir -p "$STATE"
ID=$(python3 -c 'import json,sys;print(json.loads(sys.argv[1])["id"])' "$JOB") || exit 0
[ "$(cat "$STATE/feito" 2>/dev/null)" = "$ID" ] && exit 0
echo "$ID" > "$STATE/feito"
put() { curl -fs -X PUT -H "$H" --data-binary "$2" "$MD/instance/guest-attributes/infinito/$1" >/dev/null; }
put id "$ID"; put inicio "$(date +%s)"; put estado rodando

CMD=$(python3 - "$JOB" <<'PY'
import json, re, shlex, sys
j = json.loads(sys.argv[1]); tipo = j["tipo"]; p = j.get("params") or {}; horas = float(j["horas"])
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
else:
    sys.exit(2)
print(f"timeout {max(60, int(horas * 3600))} bash -c {shlex.quote(corpo)}")
PY
) || { put codigo 2; put saida "job recusado pela allowlist da VM"; put fim "$(date +%s)"; put estado concluido; shutdown -h now; exit 0; }

export HOME=/root PATH=/root/.elan/bin:$PATH
LOG="$STATE/$ID.log"; : > "$LOG"
{
  command -v git >/dev/null && command -v gcc >/dev/null && command -v curl >/dev/null || { apt-get update -qq && apt-get install -y -qq git gcc curl; }
  command -v lake >/dev/null || { curl -sSf https://elan.lean-lang.org/elan-init.sh | sh -s -- -y --default-toolchain none; }
  REPO=/opt/infinito/Matematica
  [ -d "$REPO/.git" ] || git clone -q --depth 1 -b main https://github.com/thiagopatzdorf/Matematica "$REPO"
  cd "$REPO" && git fetch -q --depth 1 origin main && git reset -q --hard origin/main
  eval "$CMD"
} >> "$LOG" 2>&1
CODIGO=$?
put codigo "$CODIGO"
put saida "$(tail -c 3000 "$LOG" | iconv -c -t utf-8)"
put fim "$(date +%s)"; put estado concluido
sync; shutdown -h now
