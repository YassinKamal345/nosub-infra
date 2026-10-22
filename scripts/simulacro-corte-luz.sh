#!/bin/bash
# simulacro-corte-luz.sh: simulacro de corte de luz en la sede (plan de contingencia, E1; riesgo RS-15).
# La centralita no tiene SAI. Aquí se "corta la luz" de todas las máquinas de la sede a la vez (stop inmediato,
# sin apagado ordenado), se espera el aviso del VPS del cloud y se "vuelve la luz" arrancándolas como hace
# Proxmox al encenderse (startall: orden y esperas del inventario). Después se mide cuánto tarda todo en volver.
# No toca lo que no es de la sede (etiqueta "sede"): cajas, VPS del cloud ni otros servicios de Proxmox.
# Uso (en Proxmox, como root): scripts/simulacro-corte-luz.sh
set -u
cd "$(dirname "$0")/.."
NODO=$(hostname)
ESTADO=estado.203-0-113-10.sslip.io; IP_VPS=203.0.113.10     # página de estado del cloud (laboratorio)
fallos=0
r(){ [ "$2" = "$3" ] && ok="✓" || { ok="✗"; fallos=$((fallos+1)); }; printf ' %s %-52s %s\n' "$ok" "$1" "$2"; }
t(){ printf '%4d s' $(( $(date +%s) - T0 )); }
maquinas(){ pvesh get /cluster/resources --type vm --output-format json | python3 -c '
import json, sys
for v in json.load(sys.stdin):
    if "sede" in v.get("tags", "").split(";") and v["status"] == sys.argv[1]:
        print(("qm" if v["type"] == "qemu" else "pct"), v["vmid"], v["name"])' "$1"; }
# Comprobaciones seguidas, todas bien (+n) o todas mal (-n), de "Conexión con la sede" en la página de estado.
# Gatus avisa por ntfy con 3 fallos seguidos y da el aviso por resuelto con 2 aciertos seguidos (rol cloud).
racha(){ curl -sk -m5 --resolve $ESTADO:443:$IP_VPS https://$ESTADO/api/v1/endpoints/statuses | python3 -c '
import json, sys
r = [x["success"] for x in [e for e in json.load(sys.stdin) if e["key"] == "sede_conexión-con-la-sede"][0]["results"]]
n = 0
for x in reversed(r):
    if x != r[-1]: break
    n += 1
print(n if r[-1] else -n)' 2>/dev/null || echo 0; }
sede_en_gatus(){ [ "$(racha)" -gt 0 ] && echo bien || echo mal; }
caidos(){ ansible monitor -m shell -a "curl -s localhost:9090/api/v1/query --data-urlencode 'query=(up{job!=\"a_demanda\"}==0) or (probe_success==0)'" 2>/dev/null \
  | tail -1 | python3 -c 'import json,sys; print(" ".join(sorted(m["metric"].get("nombre", m["metric"].get("instance","?")) for m in json.load(sys.stdin)["data"]["result"])))' 2>/dev/null || echo "monitor sin responder"; }
# Segundos que lleva en marcha Prometheus: recién arrancado aún no ha mirado nada y "nada caído" no significa nada
prometheus_lleva(){ ansible monitor -m shell -a "curl -s localhost:9090/api/v1/status/runtimeinfo" 2>/dev/null | tail -1 \
  | python3 -c 'import json,sys,datetime as d; s=json.load(sys.stdin)["data"]["startTime"][:19]; print(int((d.datetime.utcnow()-d.datetime.fromisoformat(s)).total_seconds()))' 2>/dev/null || echo 0; }

mapfile -t SEDE < <(maquinas running)
[ ${#SEDE[@]} -gt 0 ] || { echo "No hay máquinas de la sede encendidas"; exit 1; }
echo "Máquinas de la sede encendidas: $(printf '%s\n' "${SEDE[@]}" | awk '{printf "%s(%s) ", $3, $2}')"
r "Antes: la página de estado ve la sede" "$(sede_en_gatus)" bien
r "Antes: Prometheus sin nada caído"     "$(caidos)" ""

echo "1. Corte de luz: todas a la vez, sin apagado ordenado"
T0=$(date +%s)
for m in "${SEDE[@]}"; do set -- $m; $1 stop $2 >/dev/null 2>&1 & done; wait
echo "   $(t) todo apagado"

echo "2. Aviso desde el cloud (Gatus -> ntfy)"
for i in $(seq 48); do [ "$(racha)" -le -3 ] && break; sleep 5; done
echo "   $(t) la página de estado lleva $(( -$(racha) )) fallos seguidos"
r "Gatus dispara el aviso (3 fallos seguidos, < 6 min)" "$([ "$(racha)" -le -3 ] && echo sí || echo no)" sí
echo "   >> Comprueba que ha llegado el aviso al móvil (ntfy)"
echo "   (la luz sigue cortada 1 minuto más)"; sleep 60

echo "3. Vuelve la luz: Proxmox arranca la sede (startall, orden y esperas del inventario)"
T0=$(date +%s)
pvesh create /nodes/$NODO/startall >/dev/null 2>&1 &
declare -A visto=()
while [ ${#visto[@]} -lt ${#SEDE[@]} ] && [ $(( $(date +%s) - T0 )) -lt 600 ]; do
  for m in "${SEDE[@]}"; do set -- $m
    [ -z "${visto[$2]:-}" ] && $1 status $2 2>/dev/null | grep -q running && { visto[$2]=1; echo "   $(t) arranca $3 ($2)"; }
  done; sleep 1
done
wait
r "Arrancan todas" "${#visto[@]}" "${#SEDE[@]}"

echo "4. Vuelta a la normalidad"
for i in $(seq 60); do c=$(caidos); [ -z "$c" ] && [ "$(prometheus_lleva)" -ge 90 ] && break; sleep 10; done
echo "   $(t) Prometheus: ${c:-todo arriba}"
r "Todos los equipos y servicios arriba (Prometheus)" "$c" ""
for i in $(seq 30); do [ "$(sede_en_gatus)" = bien ] && break; sleep 10; done
r "La página de estado vuelve a ver la sede" "$(sede_en_gatus)" bien
for i in $(seq 60); do [ "$(racha)" -ge 2 ] && break; sleep 5; done
echo "   $(t) la página de estado lleva $(racha) aciertos seguidos"
r "Gatus da el aviso por resuelto (2 aciertos seguidos)" "$([ "$(racha)" -ge 2 ] && echo sí || echo no)" sí
echo "   >> Comprueba que ha llegado el aviso de \"resuelto\" al móvil"
echo "   PostgreSQL tras el corte:"
ansible bbdd -m shell -a "grep -hE 'not properly shut down|redo done|ready to accept' \$(ls -t /var/lib/pgsql/data/log/*.log | head -1) | tail -3 | cut -c12-23,46-140" 2>/dev/null | tail -n +2 | sed 's/^/     /'

echo "5. Pruebas de la red"
r "Aislamiento entre VLANs (probar-red.sh)" "$(scripts/probar-red.sh >/dev/null 2>&1 && echo bien || echo mal)" bien
r "VPN (probar-vpn.sh)"                     "$(scripts/probar-vpn.sh >/dev/null 2>&1 && echo bien || echo mal)" bien
r "DHCP en las VLANs (probar-dhcp.sh)"      "$(scripts/probar-dhcp.sh >/dev/null 2>&1 && echo bien || echo mal)" bien
[ $fallos -eq 0 ] && echo "Todo como se esperaba." || { echo "$fallos comprobación(es) no coinciden."; exit 1; }
