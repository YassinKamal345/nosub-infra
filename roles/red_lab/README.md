# Rol red_lab

Crea en Proxmox la red de la sede **de laboratorio**: virtual y aislada.

| Bridge | Para qué |
|---|---|
| `vmbr1` | Troncal de la sede: bridge con VLANs (10-60) **sin tarjeta física**. En la sede real se le pone el puerto que va al switch SW1. |
| `vmbr2` | Enlace privado Proxmox ↔ OPNsense (WAN de OPNsense, `172.31.255.0/30`). Proxmox hace NAT hacia Internet. |

Reglas de aislamiento (en `vmbr2`, al levantarse):
- NAT de la WAN de OPNsense hacia Internet por `vmbr0`.
- **Bloqueado** el paso de la sede a la red local donde está Proxmox (`red_local`, en el laboratorio la de la oficina).
- `vmbr1.10`: Proxmox dentro de la VLAN de gestión (`10.10.10.2`); llega al resto de la sede por OPNsense (`10.10.10.1`).
- La sede tampoco puede usar a Proxmox como router hacia la red local (bloqueo también en `vmbr1*`).

Variables en `defaults/main.yml`. Deshacer: borrar el bloque `NOSUB red_lab` de `/etc/network/interfaces`, `/etc/sysctl.d/90-nosub-red-lab.conf` y `ifreload -a`.
