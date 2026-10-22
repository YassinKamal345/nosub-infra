#!/bin/bash
# simulacro-restauracion.sh: simulacro de restauración (plan de contingencia, E3 y E4).
# Recupera datos de verdad desde las copias, pero siempre APARTE: carpetas temporales, bases de datos
# "simulacro_*" y un contenedor nuevo desconectado. No toca nada de lo que está en marcha y lo borra todo al final.
#   1. restic (cloud) -> ficheros de Gitea en una carpeta aparte; el repositorio tiene que estar sano
#   2. restic (cloud) -> copias de PostgreSQL; se cargan en bases nuevas y se comparan con las de verdad
#   3. vzdump (local) -> el contenedor red-int entero, con otro número y desconectado; tiene que arrancar y funcionar
# Uso (en Proxmox, como root): scripts/simulacro-restauracion.sh
set -u
cd "$(dirname "$0")/.."
CT=9221                      # contenedor del simulacro (número libre, fuera de los rangos de la sede)
fallos=0
r(){ [ "$2" = "$3" ] && ok="✓" || { ok="✗"; fallos=$((fallos+1)); }; printf ' %s %-52s %s\n' "$ok" "$1" "$2"; }
en(){ ansible "$1" -m shell -a "$2" 2>/dev/null | tail -n +2; }
sql(){ en bbdd "sudo -u postgres psql -d $1 -tAc \"$2\""; }
limpiar(){
  en gitea "rm -rf /tmp/simulacro" >/dev/null
  en bbdd "rm -rf /tmp/simulacro; for b in simulacro_gitea simulacro_extranet; do sudo -u postgres dropdb --if-exists \$b; done" >/dev/null
  pct status $CT >/dev/null 2>&1 && { pct stop $CT >/dev/null 2>&1; pct destroy $CT --purge >/dev/null; }
}
trap limpiar EXIT; limpiar

echo "1. Ficheros de Gitea desde el cloud (restic)"
SECONDS=0
r "Repositorio de copias íntegro (restic check)" "$(en gitea '. /etc/restic/entorno; restic check -q >/dev/null 2>&1 && echo sí || echo no')" sí
echo "   Copia: $(en gitea '. /etc/restic/entorno; restic snapshots --host gitea --latest 1 --compact | sed -n 3p')"
en gitea ". /etc/restic/entorno; restic restore latest --host gitea --target /tmp/simulacro -q" >/dev/null
GIT=/tmp/simulacro/var/lib/gitea/repositorios/nosub/nosub-infra.git
r "Configuración recuperada (app.ini)"         "$(en gitea 'test -s /tmp/simulacro/etc/gitea/app.ini && echo sí || echo no')" sí
r "Repositorio nosub-infra recuperado y sano"  "$(en gitea "git --git-dir=$GIT fsck --no-progress >/dev/null 2>&1 && echo sí || echo no")" sí
copia=$(en gitea "git --git-dir=$GIT log -1 --format='%h %ci' main")
ahora=$(git log -1 --format='%h %ci' main)
echo "   Último commit en la copia: $copia · hoy: $ahora (lo de después de la copia se perdería: RPO)"
echo "   Tiempo: ${SECONDS} s"

echo "2. Bases de datos desde el cloud (restic + pg_restore)"
SECONDS=0
en bbdd ". /etc/restic/entorno; restic restore latest --host bbdd --target /tmp/simulacro -q" >/dev/null
C=/tmp/simulacro/var/lib/pgsql/copias
for b in gitea extranet; do
  f=$(en bbdd "ls -t $C/$b-*.dump | head -1")
  echo "   $b: ${f##*/}"
  en bbdd "sudo -u postgres createdb simulacro_$b && sudo -u postgres pg_restore --no-owner --no-privileges -d simulacro_$b < $f" >/dev/null
done
for q in gitea.repository gitea.email_address gitea.push_mirror extranet.clientes extranet.cajas; do
  b=${q%%.*}; t=${q#*.}
  c=$(sql simulacro_$b "SELECT count(*) FROM $t"); v=$(sql $b "SELECT count(*) FROM $t")
  r "$b: filas de $t (copia / en marcha: $v)" "$c" "$v"
done
echo "   Tiempo: ${SECONDS} s"

echo "3. Contenedor entero desde vzdump (red-int, como CT $CT desconectado)"
SECONDS=0
f=$(ls -t /mnt/backup/dump/vzdump-lxc-221-*.tar.zst | head -1)
echo "   Copia: ${f##*/}"
pct restore $CT "$f" --storage local-lvm --unique 1 >/dev/null 2>&1
r "Restaurado" "$(pct status $CT >/dev/null 2>&1 && echo sí || echo no)" sí
# Misma red pero con el cable "desenchufado": la configuración ve su interfaz y no choca con el de verdad
pct set $CT --net0 "$(pct config $CT | sed -n 's/^net0: //p'),link_down=1" --onboot 0 --hostname simulacro-red-int >/dev/null 2>&1
pct start $CT >/dev/null 2>&1
for i in $(seq 30); do pct exec $CT -- systemctl is-system-running 2>/dev/null | grep -qE 'running|degraded' && break; sleep 2; done
dentro(){ pct exec $CT -- bash -c "$1" 2>/dev/null; }
r "Arranca"                                    "$(pct status $CT | awk '{print $2}')" running
r "DNS (Bind9) en marcha"                      "$(dentro 'systemctl is-active named')" active
r "DNS responde: gitea.nosub.lan"              "$(dentro 'dig +short +time=2 @127.0.0.1 gitea.nosub.lan')" 10.10.20.10
r "Configuración de DHCP (Kea) válida"         "$(dentro '/usr/sbin/kea-dhcp4 -t /etc/kea/kea-dhcp4.conf >/dev/null 2>&1 && echo sí || echo no')" sí
r "Configuración del proxy (Squid) válida"     "$(dentro '/usr/sbin/squid -k parse >/dev/null 2>&1 && echo sí || echo no')" sí
echo "   Tiempo hasta funcionar: ${SECONDS} s"

echo "Limpieza: carpetas temporales, bases simulacro_* y CT $CT"
[ $fallos -eq 0 ] && echo "Todo como se esperaba." || { echo "$fallos comprobación(es) no coinciden."; exit 1; }
