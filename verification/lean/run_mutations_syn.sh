#!/usr/bin/env bash
# run_mutations_syn.sh TAG OUTDIR [--full]
# Gera as mutações de mutate_syn.py e compila cada módulo adulterado com `lake env lean`, numa pasta
# à parte (OUTDIR/build), sem tocar no lakefile nem em CoveringLean/. Cada mutação PASSA (é
# rejeitada) se algum módulo dela falhar no Lean; o script sai com 1 se alguma mutação compilar.
# Requer o certificado original já compilado (lake build CoveringLean.Syn_TAG).
set -uo pipefail
cd "$(dirname "$0")/../.."
export PATH="$HOME/.elan/bin:$PATH"
command -v lake >/dev/null || { echo "lake não encontrado"; exit 3; }
TAG=$1; OUT=$(realpath -m "$2"); shift 2
mkdir -p "$OUT/build/CoveringLean"
# O Lean resolve `CoveringLean.X` na primeira raiz do LEAN_PATH que tem a pasta CoveringLean, então
# os .olean originais entram na pasta à parte por link simbólico (os adulterados ficam ao lado).
for f in .lake/build/lib/lean/CoveringLean/*; do ln -sf "$(realpath "$f")" "$OUT/build/CoveringLean/"; done
python3 verification/lean/mutate_syn.py "$TAG" "$OUT" "$@" > "$OUT/plan.json" || exit 2
compile() {   # módulo -> 0 se compilou
  local mod=$1 f=${1//.//}
  mkdir -p "$OUT/build/$(dirname "$f")"
  lake env bash -c "LEAN_PATH=$OUT/build:\$LEAN_PATH lean --root=$OUT $OUT/$f.lean -o $OUT/build/$f.olean" \
    > "$OUT/build/${f//\//_}.log" 2>&1
}
status=0
# Só conta como rejeição um erro do Lean com posição no arquivo adulterado; qualquer outra falha
# (lake ausente, import não achado) é defeito do arranjo e aborta. Erro que já custou uma rodada:
# sem isto, "lake: command not found" passava como "mutação rejeitada".
lean_error() { grep -m1 -E "\.lean:[0-9]+:[0-9]+: error" "$1"; }
ctl=$(python3 -c "import json;print(' '.join(json.load(open('$OUT/plan.json'))['control']['modules']))")
for mod in $ctl; do
  f=${mod//.//}
  if compile "$mod"; then echo "$TAG controle: compilou, como esperado ($mod)"; else
    echo "$TAG controle: NÃO compilou -- arranjo quebrado, mutações não valem"; cat "$OUT/build/${f//\//_}.log" | head -5; exit 3; fi
done
for mut in $(python3 -c "import json;p=json.load(open('$OUT/plan.json'));print(' '.join(p['mutations']))"); do
  for grp in modules modules_card modules_cover; do
    mods=$(python3 -c "import json;m=json.load(open('$OUT/plan.json'))['mutations']['$mut'];print(' '.join(m.get('$grp',[])))")
    [[ -z "$mods" ]] && continue
    rejected=""
    for mod in $mods; do
      s=$(date +%s)
      if compile "$mod"; then echo "  ok   $mod ($(( $(date +%s)-s ))s)"; else
        f=${mod//.//}; err=$(lean_error "$OUT/build/${f//\//_}.log" | cut -c1-260)
        if [[ -z "$err" ]]; then echo "  falha sem erro do Lean em $mod (arranjo):"; head -5 "$OUT/build/${f//\//_}.log"; exit 3; fi
        ln=$(sed -E 's/.*\.lean:([0-9]+):.*/\1/' <<<"$err")
        thm=$(sed -n "${ln}p" "$OUT/$f.lean" | grep -oE "^(theorem|example) [^ ]*" | head -1)
        msg=$(sed -E 's/.*\.lean:([0-9]+:[0-9]+): error: /\1: /' <<<"$err" | cut -c1-90)
        echo "  FAIL $mod ($(( $(date +%s)-s ))s) [$thm] $msg"; rejected=$mod; break
      fi
    done
    if [[ -n "$rejected" ]]; then echo "$TAG $mut/$grp: REJEITADA pelo Lean em $rejected"
    else echo "$TAG $mut/$grp: COMPILOU (mutação não detectada!)"; status=1; fi
  done
done
exit $status
