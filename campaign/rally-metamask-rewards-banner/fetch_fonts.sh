#!/usr/bin/env bash
# Downloads the display/UI fonts used by make_banner.py (Archivo + Inter, SIL OFL).
# Placeholders for Rally's real brand typeface — swap in the licensed files when available.
set -euo pipefail
cd "$(dirname "$0")" && mkdir -p fonts && cd fonts
dl() {
  url=$(curl -sS -A "Mozilla/5.0" "https://fonts.googleapis.com/css2?family=$1" \
        | grep -o "https://fonts.gstatic.com[^)]*" | head -1)
  curl -sS -A "Mozilla/5.0" "$url" -o "$2.ttf"
}
dl "Archivo:ital,wdth,wght@1,75,900" archivo_it900   # display / headline
dl "Archivo:wdth,wght@75,700"        archivo_700
dl "Archivo:wght@600"                archivo_600     # UI / sub / CTA
dl "Inter:wght@600"                  inter600
echo "fonts ready"
