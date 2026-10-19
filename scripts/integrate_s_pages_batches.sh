#!/usr/bin/env bash
# Checkout per-batch slug files from feat/s-pages-batch-* commits.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

checkout_slug() {
  local ref="$1" slug="$2"
  git checkout "$ref" -- "onepagers/data/${slug}.json" 2>/dev/null || true
  git checkout "$ref" -- "onepagers/sites/${slug}" 2>/dev/null || true
  git checkout "$ref" -- "onepagers/media/${slug}" 2>/dev/null || true
}

declare -A BATCH_REFS=(
  [0]="2e305a9"
  [1]="758e6c3"
  [2]="5fdd211"
  [3]="80ca55c"
  [4]="a91df06"
  [5]="82b5da4"
  [6]="5803c86"
  [7]="5fa290a"
  [8]="5dc3502"
  [9]="6f505ae"
  [10]="e774cc5"
  [11]="08b0058"
  [12]="40c1d9f"
)

declare -A BATCH_SLUGS=(
  [0]="b-kapz elastic-energy mubon novatio plasticos-ambientales"
  [1]="ainwater air4u suncolombia weia zhana-solutions"
  [2]="alfe-aseo-sas baruk-company bioarea calojabones"
  [3]="ciclorganicos cobox-logistic greenify habitat-a-vibe-company"
  [4]="ala-terra compostpack cr-tejas deposito-global-recycling deterquin"
  [5]="dexon-software-sas-bic eco-biosis eco-industria embergy fluvia"
  [6]="galaxy-pack glooba glu-energy griin-energy grupo-natural-andino"
  [7]="greendex hunter-tecnologia i-can-jump ilikko isd-ingenieria-y-servicios"
  [8]="istmo-verde kigui kimsa kleantab linko-workers"
  [9]="mayugo mitsidi monte-jazmin moviltronics myma"
  [10]="nina-energy nuevas-tecnologias-fisicoquimicas oasis-group pacaceite parsons-kinetics"
  [11]="kelab plasfacol pleia purest-fuels simbiotic"
  [12]="tavi-technology tr-global-group valopes wheelo"
)

for b in "${!BATCH_REFS[@]}"; do
  ref="${BATCH_REFS[$b]}"
  for slug in ${BATCH_SLUGS[$b]}; do
    checkout_slug "$ref" "$slug"
  done
done

# Sheet metadata (latest batches.json from data branch)
git checkout origin/data/sheet-s-pages -- data/sheet-s-pages/batches.json 2>/dev/null || \
  git checkout 40c1d9f -- data/sheet-s-pages/batches.json 2>/dev/null || true

# Template + builder from batch-12 (newest s-pages pipeline)
git checkout 40c1d9f -- onepagers/template/styles.css scripts/build_onepagers.py 2>/dev/null || true

# Batch-0 image sources if present
git checkout 2e305a9 -- data/sheet-s-pages/image-sources-batch0.json 2>/dev/null || true
git checkout e774cc5 -- onepagers/data/s-pages-batch-10-image-sources.json 2>/dev/null || true

echo "Integrated slug trees from batch commits."
