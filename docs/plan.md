# Plan de montaje

Copia resumida del plan (el detalle vive en Notion: "10. Proyecto ASIX — Plan de montaje").

- **Laboratorio:** prx (HP, 8 núcleos, 16 GB). Sede definitiva: la centralita. Caja del cliente: el mini PC.
- **Red de la sede:** virtual y aislada dentro del laboratorio (bridge con VLANs sin tarjeta física);
  sale a Internet con NAT a través de Proxmox. En la sede real, el bridge se conecta al switch SW1.
- **Límite real:** la RAM. Los núcleos se pueden repartir de más (casi no se usan); k3s y GNS3 solo
  se encienden cuando hacen falta.

## Fase 2 · Base de la sede
- [x] 2.1 Repositorio con la estructura, Ansible Vault y primer playbook (`sede.yml` llega a Proxmox)
- [x] 2.2 Red de laboratorio: bridges y NAT (rol `red_lab`)
- [x] 2.3 Rol `proxmox_vms`: crea los LXC por la API de Proxmox con un usuario limitado (primero: gitea, 220)
- [x] 2.4 OPNsense: VLANs 10-60, DMZ, reglas y WireGuard (VPN 10.99.0.0/24, puerto 51820)
- [x] 2.5 Gitea 28.2 en CT 220 (http://10.10.20.10:3000), repositorio subido. Espejo en GitHub hecho. Pendiente: mover aquí el nodo de control
- [x] 2.6 Planos de red (`docs/red.md`) y configs de routers/switches/AP generadas con Ansible (`playbooks/red_fisica.yml`). Pendiente: aplicarlas en el centro

## Fase 3 · Servicios de la sede
- [x] Bind9 + Kea DHCP + Squid en CT 221 `red-int` (10.10.20.11); relay DHCP en OPNsense; prueba `scripts/probar-dhcp.sh`
- [x] PostgreSQL 16 en Rocky Linux 10 (CT 222 `bbdd`, 10.10.20.12), copia diaria; Gitea pasado de SQLite a PostgreSQL
- [x] Prometheus + Grafana (panel ADMIN) en CT 223 `monitor`; node_exporter en todas las máquinas; blackbox comprueba cada servicio (sin Zabbix: decidido 2026-10-16)
- [x] Intranet (Wiki.js + Nextcloud, CT 224 `intranet`) y extranet (portal de clientes propio en la DMZ, CT 230 `extranet`) con PostgreSQL
- [x] Traefik 3.7 con HTTPS en la DMZ (CT 230) delante del portal; certificados de la CA propia "NoSub CA"
- [x] Prueba de reconstrucción (2026-10-21): copia vzdump, borrado de OPNsense y los 6 LXC, y `sede.yml`
  desde cero → sin errores a la primera (11 min); luego `git push` del repo a la Gitea nueva y pasada normal
  (crea el espejo de GitHub). Segunda pasada: 0 cambios. Pruebas de red, DHCP y VPN, 12/12 sondas y HTTPS del portal OK.
  Ansible rehace la **configuración**, no los **datos** (repos, wiki, ficheros): esos vuelven de las copias.

## Fase 4 · Producto e integración
- [x] k3s v1.36.5 en la VM 231 `k3s` (Ubuntu Server 24.04, la tercera distribución, 10.10.30.20, DMZ).
  La VM sale de la imagen "cloud" oficial con cloud-init (rol `proxmox_vms`, lista `maquinas_virtuales`).
  Cada proyecto DAM/DAW tiene namespace, cuota y aislamiento propios y se publica en
  `https://<proyecto>.apps.nosub.lan` a través del Traefik de la DMZ. Proyecto `demo` en marcha;
  14/14 sondas OK; segunda pasada de `sede.yml`: 0 cambios
- [ ] Caja del cliente (mini PC) y túneles con la sede
- [ ] Nube
- [ ] GNS3
