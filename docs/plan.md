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
- [ ] 2.3 Rol `proxmox_vms`: crea VMs y LXC por la API de Proxmox
- [ ] 2.4 OPNsense: VLANs 10-60, DMZ, WireGuard
- [ ] 2.5 Gitea + nodo de control Ansible; espejo en GitHub
- [ ] 2.6 Planos de red y configs de routers/switches/AP

## Fase 3 · Servicios de la sede
- [ ] Bind9 + Kea DHCP + Squid · PostgreSQL (Rocky) · Prometheus + Grafana (panel ADMIN) + Uptime Kuma
- [ ] Intranet y extranet con PostgreSQL · Traefik con HTTPS en la DMZ
- [ ] Prueba: borrar la sede y reconstruirla con `sede.yml`
