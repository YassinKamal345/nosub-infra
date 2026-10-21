#!/bin/sh
# Ejecuta una orden dentro de un equipo del ensayo de GNS3:  nosub-gns3-en R2 vtysh -c "show ip ospf neighbor"
# (GNS3 llama a los contenedores "GNS3.<equipo>.<id>")
set -e
equipo=$1; shift
id=$(docker ps -q --filter "name=^GNS3\.$equipo\." | head -1)
[ -n "$id" ] || { echo "No encuentro el equipo $equipo (¿está arrancado el proyecto?)" >&2; exit 2; }
exec docker exec "$id" "$@"
