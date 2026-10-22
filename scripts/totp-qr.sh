#!/bin/bash
# totp-qr.sh: muestra el QR del segundo factor (TOTP) de un usuario de la web de OPNsense, para darlo de alta en
# la app del móvil (Google Authenticator, Aegis, 2FAS...). La semilla se deriva del Vault (filtro totp_semillas),
# así que es siempre la misma: si se pierde el móvil, se vuelve a escanear.
# Ejecútalo en tu propia terminal (SSH): el QR es un secreto, que no quede en registros ni en conversaciones.
# Uso (en el nodo de control, como root): scripts/totp-qr.sh [usuario]   (por defecto yassin)
set -euo pipefail
cd "$(dirname "$0")/.."
USUARIO=${1:-yassin}
SEMILLA=$(ansible localhost -o -m debug \
  -a "msg={{ (opnsense_root_clave | totp_semillas(['$USUARIO'], 'opnsense-web'))['$USUARIO'] }}" \
  -e @inventories/sede/group_vars/all/main.yml -e @inventories/sede/group_vars/all/vault.yml 2>/dev/null \
  | grep -o '"msg": "[A-Z2-7]*"' | cut -d'"' -f4)
[ -n "$SEMILLA" ] || { echo "No he podido calcular la semilla"; exit 1; }
URI="otpauth://totp/NoSub%20OPNsense:$USUARIO?secret=$SEMILLA&issuer=NoSub%20OPNsense&digits=6&period=30"
echo "Escanea este QR con la app del móvil (usuario $USUARIO de la web de OPNsense):"
qrencode -t ANSIUTF8 "$URI"
echo "Si no puedes escanearlo, mete esta clave a mano (tipo: basada en tiempo): $SEMILLA"
echo
echo "Para entrar en la web: usuario $USUARIO y, en contraseña, tu contraseña seguida del código de 6 cifras"
echo "(por ejemplo: MiContraseña123456)."
