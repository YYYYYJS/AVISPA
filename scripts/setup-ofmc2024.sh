#!/usr/bin/env bash
set -euo pipefail
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || { echo "Requires Linux x86_64" >&2; exit 2; }
SPAKA_OFMC2024_RUNTIME="${1:?Pass an absolute isolated runtime directory}"
[[ "$SPAKA_OFMC2024_RUNTIME" == /* ]] || { echo "Use an absolute path" >&2; exit 2; }
mkdir -p "$SPAKA_OFMC2024_RUNTIME"
cd "$SPAKA_OFMC2024_RUNTIME"
curl --fail --location --retry 3 --output ofmc2024.zip 'https://www2.compute.dtu.dk/~samo/ofmc2024.zip'
printf '%s  %s\n' 'e69cda4731b570da9ee5c14057a589e2a5e96fcfc9edd30669062e939cbe8c08' 'ofmc2024.zip' | sha256sum --check -
unzip -q -o ofmc2024.zip 'ofmc2024/*'
export OFMC2024="$SPAKA_OFMC2024_RUNTIME/ofmc2024/executables/linux/ofmc"
chmod +x "$OFMC2024"
printf 'export OFMC2024=%q\n' "$OFMC2024" > "$SPAKA_OFMC2024_RUNTIME/activate.sh"
ldd "$OFMC2024"
# Official binary reports --version and --help through an exception, hence exit 1.
"$OFMC2024" --version > "$SPAKA_OFMC2024_RUNTIME/version.txt" 2>&1 || true
cat "$SPAKA_OFMC2024_RUNTIME/version.txt"
grep -q 'version 2024' "$SPAKA_OFMC2024_RUNTIME/version.txt"
"$OFMC2024" --help > "$SPAKA_OFMC2024_RUNTIME/help.txt" 2>&1 || true
# The old OFMC stays on PATH. Call the new binary explicitly as "$OFMC2024".
