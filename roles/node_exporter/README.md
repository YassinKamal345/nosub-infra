# Rol node_exporter

Instala **node_exporter** (métricas de CPU, RAM, disco, red y servicios) en todas las máquinas de la sede: Proxmox y cada contenedor.
Prometheus (rol `monitorizacion`) las recoge cada 15 s por el puerto 9100.

- Es el binario oficial, comprobado con su sha256. Es igual en Debian y en Rocky Linux.
- Corre con un usuario propio, sin permisos.
- En Proxmox escucha solo en la red de gestión (10.10.10.2), nunca en la red de la oficina. La regla `[nosub] metricas` del firewall de Proxmox solo deja entrar a `monitor` (10.10.20.13).

**Cambiar de versión:** `node_exporter_version` y su `node_exporter_sha256` (del `sha256sums.txt` de la versión).
