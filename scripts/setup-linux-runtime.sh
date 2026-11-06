#!/usr/bin/env bash
set -euo pipefail
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || { echo "Requires Linux x86_64" >&2; exit 2; }
SPAKA_AVISPA_RUNTIME="${1:?Pass an absolute isolated runtime directory}"
[[ "$SPAKA_AVISPA_RUNTIME" == /* ]] || { echo "Use an absolute path" >&2; exit 2; }
mkdir -p "$SPAKA_AVISPA_RUNTIME/downloads" "$SPAKA_AVISPA_RUNTIME/compat"
cd "$SPAKA_AVISPA_RUNTIME/downloads"
fetch() {
  local url="$1" name="$2" hash="$3"
  curl --fail --location --retry 3 --output "$name" "$url"
  printf '%s  %s\n' "$hash" "$name" | sha256sum --check -
}
fetch 'https://people.irisa.fr/Thomas.Genet/span/span-1.6-linux64-ubuntu.tar.gz' 'span-1.6-linux64-ubuntu.tar.gz' '6178c665898fce64e536838349caae4f7b510eeb2eb195a1dae7b2debe653211'
fetch 'https://archive.ubuntu.com/ubuntu/pool/main/libf/libffi/libffi6_3.2.1-8_amd64.deb' 'libffi6.deb' 'fa26945b0aadfc72ec623c68be9cc59235a7fe42e2388f7015fd131f4fb06dc9'
fetch 'https://archive.ubuntu.com/ubuntu/pool/main/n/ncurses/libtinfo5_6.1-1ubuntu1.18.04.1_amd64.deb' 'libtinfo5.deb' 'f7a59966bba0f997dd1bee0994c43cd563026a81e791cacc6540a2a8c9a49e53'
tar -xzf span-1.6-linux64-ubuntu.tar.gz -C "$SPAKA_AVISPA_RUNTIME"
dpkg-deb -x libffi6.deb "$SPAKA_AVISPA_RUNTIME/compat"
dpkg-deb -x libtinfo5.deb "$SPAKA_AVISPA_RUNTIME/compat"
export AVISPA_PACKAGE="$SPAKA_AVISPA_RUNTIME/span"
export LD_LIBRARY_PATH="$SPAKA_AVISPA_RUNTIME/compat/lib/x86_64-linux-gnu:$SPAKA_AVISPA_RUNTIME/compat/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PATH="$AVISPA_PACKAGE/bin/translator:$AVISPA_PACKAGE/bin/backends/ofmc:$AVISPA_PACKAGE/bin/backends/cl:$PATH"
{
  printf 'export AVISPA_PACKAGE=%q\n' "$AVISPA_PACKAGE"
  printf 'export LD_LIBRARY_PATH=%q\n' "$LD_LIBRARY_PATH"
  printf 'export PATH=%q\n' "$PATH"
} > "$SPAKA_AVISPA_RUNTIME/activate.sh"
for executable in hlpsl2if ofmc cl-atse; do
  command -v "$executable"
  ldd "$(command -v "$executable")"
  sha256sum "$(command -v "$executable")"
  # Legacy binaries may use different version/help flags; log without aborting setup.
  "$executable" --version || true
  "$executable" --help || true
 done
