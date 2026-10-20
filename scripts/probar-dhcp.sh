#!/bin/bash
# probar-dhcp.sh: comprueba el DHCP de la sede (Kea a través del relay de OPNsense) y el DNS que reparte.
# Crea un "PC de prueba" temporal en cada VLAN con DHCP, pide IP y lo borra todo al final.
# Uso (en Proxmox, como root): scripts/probar-dhcp.sh
set -u
declare -A VLAN=([ges]=10 [emp]=40 [inv]=50 [lab]=60)
declare -A DNS=([ges]=10.10.20.11 [emp]=10.10.20.11 [inv]=10.10.50.1 [lab]=10.10.20.11)
limpiar(){ for n in "${!VLAN[@]}"; do ip netns pids d$n 2>/dev/null | xargs -r kill; ip netns del d$n 2>/dev/null; ip link del vd$n 2>/dev/null; done; }
trap limpiar EXIT
fallos=0
for n in ges emp inv lab; do
  v=${VLAN[$n]}
  ip netns add d$n; ip link add vd$n type veth peer name pd$n; ip link set pd$n netns d$n
  ip link set vd$n master vmbr1 up; bridge vlan del dev vd$n vid 1; bridge vlan add dev vd$n vid $v pvid untagged
  ip netns exec d$n ip link set lo up; ip netns exec d$n ip link set pd$n up
  # dhcpcd en modo prueba: pide IP, imprime lo que le dan y no toca nada
  r=$(ip netns exec d$n timeout 30 dhcpcd -4 -T -t 25 pd$n 2>/dev/null)
  ip=$(sed -n "s/^new_ip_address='\(.*\)'/\1/p" <<<"$r")
  gw=$(sed -n "s/^new_routers='\(.*\)'/\1/p" <<<"$r")
  dns=$(sed -n "s/^new_domain_name_servers='\(.*\)'/\1/p" <<<"$r")
  if [[ $ip == 10.10.$v.* && $gw == 10.10.$v.1 && $dns == ${DNS[$n]} ]]; then ok="✓"; else ok="✗"; fallos=$((fallos+1)); fi
  printf ' %s VLAN %-3s IP %-14s puerta %-12s DNS %s\n' "$ok" $v "${ip:-(ninguna)}" "${gw:--}" "${dns:--}"
done
[ $fallos -eq 0 ] && echo "Todo como se esperaba." || { echo "$fallos VLAN(s) no coinciden."; exit 1; }
