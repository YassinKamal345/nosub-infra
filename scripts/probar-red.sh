#!/bin/bash
# probar-red.sh: comprueba el aislamiento entre VLANs con "PCs de prueba" temporales.
# Crea un espacio de red por VLAN conectado a vmbr1, hace pings y lo borra todo al final.
# Uso (en Proxmox, como root): scripts/probar-red.sh [red_local]   (por defecto 192.168.1.0/24)
set -u
LOCAL_GW=${1:-192.168.1.1}
declare -A VLAN=([emp]=40 [inv]=50 [dmz]=30 [srv]=20)
limpiar(){ for n in "${!VLAN[@]}"; do ip netns del t$n 2>/dev/null; ip link del vt$n 2>/dev/null; done; }
trap limpiar EXIT
for n in "${!VLAN[@]}"; do
  v=${VLAN[$n]}; ip=10.10.$v.50
  ip netns add t$n; ip link add vt$n type veth peer name pt$n; ip link set pt$n netns t$n
  ip link set vt$n master vmbr1 up; bridge vlan del dev vt$n vid 1; bridge vlan add dev vt$n vid $v pvid untagged
  ip netns exec t$n ip addr add $ip/24 dev pt$n; ip netns exec t$n ip link set pt$n up
  ip netns exec t$n ip route add default via 10.10.$v.1
done
sleep 3
fallos=0
p(){ # origen destino descripción esperado(LLEGA|bloqueado)
  ip netns exec t$1 ping -c1 -W2 $2 >/dev/null 2>&1 && r=LLEGA || r=bloqueado
  [ "$r" = "$4" ] && ok="✓" || { ok="✗"; fallos=$((fallos+1)); }
  printf ' %s %-4s -> %-14s %-18s %s\n' "$ok" $1 $2 "($3)" $r
}
for n in emp inv dmz srv; do
  p $n 9.9.9.9 Internet LLEGA; p $n $LOCAL_GW "red local" bloqueado; p $n 10.10.10.2 "Proxmox" bloqueado
done
p emp 10.10.20.50 servidores LLEGA; p emp 10.10.30.50 DMZ LLEGA; p emp 10.10.50.50 invitados bloqueado
p inv 10.10.20.50 servidores bloqueado; p inv 10.10.40.50 empleados bloqueado
p dmz 10.10.20.50 servidores bloqueado; p srv 10.10.30.50 DMZ LLEGA
[ $fallos -eq 0 ] && echo "Todo como se esperaba." || { echo "$fallos comprobación(es) no coinciden."; exit 1; }
