# Rol actualizaciones

**Parches de seguridad automáticos** en todos los servidores de la sede, el VPS del cloud, GNS3 y las cajas
(riesgo RS-09 del plan de riesgos).

| Distribución | Herramienta | Qué instala sola | Cuándo |
|---|---|---|---|
| Debian 13 (contenedores y cajas) | `unattended-upgrades` | Parches de seguridad y correcciones de la versión estable (los orígenes de serie) | Cada día (`apt-daily-upgrade.timer`, hacia las 06:00) |
| Ubuntu 24.04 (k3s, GNS3, VPS) | `unattended-upgrades` | Parches de seguridad | Cada día |
| Rocky Linux 10 (`bbdd`) | `dnf-automatic` | Solo actualizaciones marcadas como de seguridad | Cada día (`dnf-automatic.timer`) |

- **Nunca reinicia sola.** Si un parche necesita reiniciar (núcleo, glibc, systemd), Prometheus avisa con
  `ReinicioPendiente` cuando lleva una semana esperando, y se reinicia a mano en un momento tranquilo
  (`pct reboot <id>` o `qm reboot <id>`). Los servicios que dependen de otros reintentan solos.
- **Se vigila que funcione.** Cada 15 minutos, `nosub-estado-actualizaciones` deja para Prometheus (node_exporter,
  carpeta `/var/lib/node_exporter`) la hora de la última pasada buena, si la última falló y si falta reiniciar.
  Aviso `ActualizacionesParadas` si una máquina lleva más de 3 días sin una pasada buena o si la última falló.
- **Excluir un paquete** (que solo se actualice a mano): `actualizaciones_excluidos`.

**Lo que no se actualiza solo** (se revisa una vez al mes, a mano):
- **Proxmox** (`apt full-upgrade` en el servidor, después de leer las notas de la versión) y **OPNsense**
  (System → Firmware). Son la base de todo: un fallo en una actualización automática pararía la sede.
- **Las aplicaciones con versión fijada en el repositorio** (Gitea, Grafana, Prometheus, node_exporter, Traefik,
  k3s, Wiki.js, Nextcloud, restic, Gatus): se cambia la versión en el rol y se aplica con Ansible.

**Comprobar:**
```bash
ansible 'all:!proxmox' -m shell -a 'cat /var/lib/node_exporter/actualizaciones.prom | grep -v "#"'
```
