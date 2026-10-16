#!/bin/bash
# probar-vpn.sh: simula un usuario de la VPN conectándose "desde casa" y comprueba a dónde llega.
# Crea un espacio de red "casa" que llega al firewall por su WAN, levanta WireGuard con el .conf
# del usuario y hace pings. Lo borra todo al terminar.
# Uso (en Proxmox, como root): scripts/probar-vpn.sh [/root/nosub-wireguard/teletrabajo-prueba.conf]
set -u
CONF=${1:-/root/nosub-wireguard/teletrabajo-prueba.conf}
TMP=$(mktemp -d); chmod 700 $TMP; grep -v '^DNS' "$CONF" > $TMP/wgt.conf
limpiar(){ ip netns exec casa wg-quick down $TMP/wgt.conf >/dev/null 2>&1; for n in casa tsrv temp; do ip netns del $n 2>/dev/null; done
           for l in vcasa vtsrv vtemp; do ip link del $l 2>/dev/null; done; rm -rf $TMP; }
trap limpiar EXIT
ip netns add casa; ip link add vcasa type veth peer name pcasa; ip link set pcasa netns casa
ip addr add 192.168.250.1/30 dev vcasa; ip link set vcasa up
ip netns exec casa ip addr add 192.168.250.2/30 dev pcasa; ip netns exec casa ip link set pcasa up
ip netns exec casa ip route add default via 192.168.250.1
mk(){ n=$1; v=$2; ip=$3; ip netns add $n; ip link add v$n type veth peer name p$n; ip link set p$n netns $n
      ip link set v$n master vmbr1 up; bridge vlan del dev v$n vid 1; bridge vlan add dev v$n vid $v pvid untagged
      ip netns exec $n ip addr add $ip/24 dev p$n; ip netns exec $n ip link set p$n up; ip netns exec $n ip route add default via ${ip%.*}.1
      ip netns exec $n ping -c1 -W1 ${ip%.*}.1 >/dev/null 2>&1 || true; }  # se presenta al firewall (ARP)
mk tsrv 20 10.10.20.50; mk temp 40 10.10.40.50
ip netns exec casa wg-quick up $TMP/wgt.conf >/dev/null 2>&1; sleep 2
fallos=0
p(){ ip netns exec casa ping -c1 -W3 $1 >/dev/null 2>&1 && r=LLEGA || r=bloqueado
     [ "$r" = "$3" ] && ok="✓" || { ok="✗"; fallos=$((fallos+1)); }; printf ' %s VPN -> %-12s %-20s %s\n' "$ok" $1 "($2)" $r; }
p 10.99.0.1 firewall LLEGA; p 10.10.20.50 servidores LLEGA; p 10.10.40.50 empleados bloqueado; p 10.10.10.2 Proxmox bloqueado
ip netns exec casa wg show | grep -E 'handshake' || { echo " ✗ sin handshake"; fallos=$((fallos+1)); }
[ $fallos -eq 0 ] && echo "Todo como se esperaba." || { echo "$fallos comprobación(es) no coinciden."; exit 1; }
