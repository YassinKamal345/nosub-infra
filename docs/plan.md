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
- [ ] Prometheus + Grafana (panel ADMIN) + Uptime Kuma (sin Zabbix: decidido 2026-10-16 para ahorrar RAM)
- [ ] Intranet y extranet con PostgreSQL · Traefik con HTTPS en la DMZ
- [ ] Prueba: borrar la sede y reconstruirla con `sede.yml`
