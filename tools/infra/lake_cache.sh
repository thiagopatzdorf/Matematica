#!/usr/bin/env bash
# Cache compartilhado dos pacotes do Lake (Mathlib e dependências) entre worktrees.
#
# Por que existe: cada worktree baixava ou copiava a Mathlib inteira (~7 GB) para o seu
# `.lake/packages`, e o disco da sessão acabava. Dois atalhos já quebraram: symlink para o
# `.lake` de outro worktree (quebrou quando o dono apagou) e build escrito na pasta alheia.
#
# Desenho: UM cache por revisão da Mathlib em `<raiz>/<rev>/packages`, e cada worktree recebe
# uma cópia por hardlink (`cp -al`). Hardlink não ocupa disco e não depende do cache continuar
# existindo (apagar o cache ou o worktree não quebra o outro). O build do projeto escreve em
# `.lake/build` do próprio worktree; os .olean dos pacotes, íntegros, não são reescritos.
#
# Uso (a partir de qualquer pasta do worktree):
#   tools/infra/lake_cache.sh ligar [--forcar]   # cria .lake/packages a partir do cache
#   tools/infra/lake_cache.sh desligar           # apaga .lake/packages deste worktree (o cache fica)
#   tools/infra/lake_cache.sh semear <pasta>     # cria o cache a partir de um .lake/packages completo
#   tools/infra/lake_cache.sh verificar          # confere revisões e o sha256 dos .olean do cache
#   tools/infra/lake_cache.sh onde               # imprime a pasta do cache desta revisão
#
# Raiz do cache: $LAKE_CACHE_DIR, ou `.mathlib-cache` ao lado do checkout principal do repo.
set -euo pipefail

erro() { echo "lake_cache: $*" >&2; exit 1; }

raiz_worktree() { git rev-parse --show-toplevel 2>/dev/null || erro "rode dentro de um worktree git"; }

raiz_cache() {
  if [[ -n "${LAKE_CACHE_DIR:-}" ]]; then echo "$LAKE_CACHE_DIR"; return; fi
  # O .git comum fica no checkout principal; o cache mora ao lado dele, fora de qualquer worktree,
  # para nenhum `rm -rf` de worktree alcançar o que os outros usam.
  local comum
  comum=$(git rev-parse --path-format=absolute --git-common-dir)
  echo "$(dirname "$(dirname "$comum")")/.mathlib-cache"
}

# Revisão de cada pacote no lake-manifest.json, uma linha "nome rev" por pacote.
revisoes() {
  python3 - "$1" <<'PY'
import json, sys
for p in json.load(open(sys.argv[1], encoding="utf-8"))["packages"]:
    print(p["name"], p["rev"])
PY
}

rev_mathlib() { revisoes "$1" | awk '$1 == "mathlib" {print $2}'; }

# Falha se algum pacote da pasta não estiver exatamente na revisão do manifesto: um cache em
# outra revisão faria o Lake refazer o checkout e reescrever arquivos compartilhados.
conferir_revisoes() {
  local manifesto=$1 pacotes=$2 nome rev atual falhas=0
  while read -r nome rev; do
    if [[ ! -d "$pacotes/$nome" ]]; then echo "  falta o pacote $nome" >&2; falhas=1; continue; fi
    atual=$(git -C "$pacotes/$nome" rev-parse HEAD 2>/dev/null || echo "?")
    if [[ "$atual" != "$rev" ]]; then echo "  $nome em $atual, manifesto pede $rev" >&2; falhas=1; fi
  done < <(revisoes "$manifesto")
  return $falhas
}

mesmo_disco() { [[ "$(stat -c %d "$1")" == "$(stat -c %d "$2")" ]]; }

cmd_onde() {
  local wt; wt=$(raiz_worktree)
  echo "$(raiz_cache)/$(rev_mathlib "$wt/lake-manifest.json")/packages"
}

cmd_semear() {
  local origem=${1:-} wt manifesto destino
  [[ -n "$origem" && -d "$origem" ]] || erro "uso: semear <pasta .lake/packages completa>"
  wt=$(raiz_worktree); manifesto="$wt/lake-manifest.json"
  destino=$(cmd_onde)
  [[ -e "$destino" ]] && erro "o cache já existe em $destino (apague com 'rm -rf' antes de semear de novo)"
  conferir_revisoes "$manifesto" "$origem" || erro "a origem não bate com $manifesto"
  mkdir -p "$(dirname "$destino")"
  mesmo_disco "$origem" "$(dirname "$destino")" || erro "origem e cache em discos diferentes: hardlink impossível"
  cp -al "$origem" "$destino"
  cp "$manifesto" "$(dirname "$destino")/lake-manifest.json"
  echo "cache criado em $destino; calculando sha256 dos .olean (uma vez)..."
  (cd "$destino" && find . -name '*.olean' -type f -print0 | sort -z | xargs -0 sha256sum) \
    > "$(dirname "$destino")/oleans.sha256"
  echo "ok: $(wc -l < "$(dirname "$destino")/oleans.sha256") .olean registrados"
}

cmd_verificar() {
  local wt destino base
  wt=$(raiz_worktree); destino=$(cmd_onde); base=$(dirname "$destino")
  [[ -d "$destino" ]] || erro "não há cache em $destino (rode 'semear')"
  conferir_revisoes "$wt/lake-manifest.json" "$destino" || erro "revisões do cache divergem do manifesto"
  [[ -f "$base/oleans.sha256" ]] || erro "sem $base/oleans.sha256 para conferir"
  (cd "$destino" && sha256sum --quiet -c "$base/oleans.sha256") || erro "algum .olean do cache mudou"
  echo "ok: revisões e $(wc -l < "$base/oleans.sha256") .olean íntegros em $destino"
}

cmd_ligar() {
  local forcar=0 wt destino alvo
  [[ "${1:-}" == "--forcar" ]] && forcar=1
  wt=$(raiz_worktree); destino=$(cmd_onde); alvo="$wt/.lake/packages"
  [[ -d "$destino" ]] || erro "não há cache em $destino (rode 'semear' a partir de um checkout completo)"
  if [[ -L "$alvo" ]]; then
    # Symlink para a pasta de outro worktree é exatamente o atalho que quebrou; troca pela cópia.
    echo "trocando o symlink $alvo -> $(readlink "$alvo") pela cópia por hardlink"
    rm "$alvo"
  elif [[ -e "$alvo" ]]; then
    [[ $forcar == 1 ]] || erro "$alvo já existe; use --forcar para apagá-lo e ligar o cache"
    rm -rf "$alvo"
  fi
  mkdir -p "$wt/.lake"
  mesmo_disco "$destino" "$wt/.lake" || erro "worktree e cache em discos diferentes: hardlink impossível"
  cp -al "$destino" "$alvo"
  echo "ok: $alvo ligado ao cache $destino (hardlink, sem cópia de dados)"
}

cmd_desligar() {
  local alvo; alvo="$(raiz_worktree)/.lake/packages"
  # Apagar hardlinks só baixa a contagem de links: o cache e os outros worktrees ficam intactos.
  if [[ -L "$alvo" ]]; then rm "$alvo"; else rm -rf "$alvo"; fi
  echo "ok: $alvo removido; o cache continua em $(cmd_onde)"
}

case "${1:-}" in
  ligar) shift; cmd_ligar "$@" ;;
  desligar) cmd_desligar ;;
  semear) shift; cmd_semear "$@" ;;
  verificar) cmd_verificar ;;
  onde) cmd_onde ;;
  *) sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//'; exit 2 ;;
esac
