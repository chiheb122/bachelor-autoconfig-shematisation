#!/bin/bash
# Lance le build natif
bash build.sh || exit 1

echo "Post-build: détection et copie du module natif..."

PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')

if [[ "$PLATFORM" == "darwin" ]]; then
    SOFILE=$(ls build/lib.*${PYVER}*/pka2core.cpython-*-darwin.so 2>/dev/null | head -n1)
elif [[ "$PLATFORM" == "linux" ]]; then
    SOFILE=$(ls build/lib.*${PYVER}*/pka2core.cpython-*-linux-gnu.so 2>/dev/null | head -n1)
else
    echo "!! Plateforme non supportée: $PLATFORM"
    exit 1
fi

if [[ -f "$SOFILE" ]]; then
    cp "$SOFILE" ../$(basename "$SOFILE")
    echo "Félicitations ! Module natif copié: $(basename "$SOFILE")"
    echo "Vous pouvez maintenant utiliser l'application avec Packet Tracer."
else
    echo "!! Module natif introuvable!"
    exit 1
fi