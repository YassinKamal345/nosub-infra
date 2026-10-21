#!/bin/bash
# probar-cajas.sh: comprueba el aislamiento de una caja ya entregada (laboratorio).
# Pone un "vecino" en la casa del cliente y prueba qué llega a la caja desde la casa, desde la sede y
# desde la propia caja. Lo borra todo al terminar.
# Uso (en Proxmox, como root): scripts/probar-cajas.sh [caja] (por defecto caja-garcia)
set -u
CAJA=${1:-caja-garcia}
cd "$(dirname "$0")/.."
dato(){ ansible-inventory --host "$CAJA" | python3 -c "import json,sys;d=json.load(sys.stdin);print(eval(sys.argv[1]))" "$1"; }
IP_VPN=$(dato 'd["ip_vpn"]'); IP_CASA=$(dato 'd["ip_casa"]'); PUENTE=$(dato 'd["lab"]["puente_casa"]')
VECINO=${IP_CASA%.*}.50; PUERTA=${IP_CASA%.*}.1
limpiar(){ ip netns del vecino 2>/dev/null; ip link del vvec 2>/dev/null; }
trap limpiar EXIT; limpiar
ip netns add vecino; ip link add vvec type veth peer name pvec; ip link set pvec netns vecino; ip link set vvec master $PUENTE up
ip netns exec vecino ip addr add $VECINO/24 dev pvec; ip netns exec vecino ip link set pvec up; ip netns exec vecino ip route add default via $PUERTA
fallos=0
r(){ [ "$2" = "$3" ] && ok="✓" || { ok="✗"; fallos=$((fallos+1)); }; printf ' %s %-52s %s\n' "$ok" "$1" "$2"; }
tcp(){ timeout 4 bash -c "</dev/tcp/$1/$2" 2>/dev/null && echo abierto || echo cerrado; }
casa(){ ip netns exec vecino bash -c "$(declare -f tcp); tcp $1 $2"; }
sede(){ pct exec $1 -- timeout 4 bash -c "</dev/tcp/$IP_VPN/$2" 2>/dev/null && echo abierto || echo cerrado; }
caja(){ ansible "$CAJA" -m shell -a "timeout 4 bash -c '</dev/tcp/$1/$2' 2>/dev/null && echo abierto || echo cerrado" 2>/dev/null | tail -1; }
echo "Caja $CAJA (casa $IP_CASA, VPN $IP_VPN)"
echo "Desde la casa del cliente:"
r "DNS de la casa (AdGuard)"            "$(ip netns exec vecino dig +short +time=2 +tries=1 @$IP_CASA debian.org | grep -q . && echo responde || echo no)" responde
r "Anuncios bloqueados (doubleclick.net)" "$(ip netns exec vecino dig +short +time=2 +tries=1 @$IP_CASA doubleclick.net)" 0.0.0.0
r "Página de inicio (80)"               "$(casa $IP_CASA 80)" abierto
r "SSH de la caja (22)"                 "$(casa $IP_CASA 22)" cerrado
r "Métricas de la caja (9100)"          "$(casa $IP_CASA 9100)" cerrado
r "La oficina (192.168.1.210)"          "$(casa 192.168.1.210 22)" cerrado
r "La sede por dentro (monitor)"        "$(casa 10.10.20.13 9100)" cerrado
echo "Desde la sede, por la VPN:"
r "Monitor -> métricas (9100)"          "$(sede 223 9100)" abierto
r "Monitor -> SSH (22)"                 "$(sede 223 22)" cerrado
r "Gitea (nodo de control) -> SSH (22)" "$(sede 220 22)" abierto
r "Otro servidor (red-int) -> SSH (22)" "$(sede 221 22)" cerrado
r "Proxmox (nodo de control) -> SSH"    "$(tcp $IP_VPN 22)" abierto
r "Monitor -> apps de la caja (80)"     "$(sede 223 80)" cerrado
echo "Desde la caja:"
r "A la sede (monitor, por su IP de VPN)" "$(ansible "$CAJA" -m shell -a "ping -c1 -W2 -I $IP_VPN 10.10.20.13 >/dev/null && echo llega || echo bloqueado" 2>/dev/null | tail -1)" bloqueado
r "A la oficina (192.168.1.210)"        "$(caja 192.168.1.210 22)" cerrado
r "A Internet (debian.org:443)"         "$(caja debian.org 443)" abierto
for otra in $(ansible-inventory --graph cajas | grep -oE 'caja-[a-z0-9-]+' | grep -vx "$CAJA"); do
  o_vpn=$(ansible-inventory --host $otra | python3 -c 'import json,sys;print(json.load(sys.stdin)["ip_vpn"])')
  o_casa=$(ansible-inventory --host $otra | python3 -c 'import json,sys;print(json.load(sys.stdin)["ip_casa"])')
  r "A otra caja ($otra) por la VPN"     "$(ansible "$CAJA" -m shell -a "ping -c1 -W2 -I $IP_VPN $o_vpn >/dev/null && echo llega || echo bloqueado" 2>/dev/null | tail -1)" bloqueado
  r "A la casa de otra caja ($otra)"     "$(caja $o_casa 80)" cerrado
done
r "Túnel con saludo reciente (< 3 min)" "$(ansible "$CAJA" -m shell -a 'echo $(( $(date +%s) - $(wg show wg0 latest-handshakes | cut -f2) ))' 2>/dev/null | tail -1 | awk '{print ($1<180)?"sí":"no"}')" sí
[ $fallos -eq 0 ] && echo "Todo como se esperaba." || { echo "$fallos comprobación(es) no coinciden."; exit 1; }
