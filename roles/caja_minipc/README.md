# Rol caja_minipc

Crea la **caja de verdad** dentro de un mini PC con Proxmox (en el laboratorio, eso lo hace `caja_lab` en prx) y la
deja lista para llevarla a casa del cliente.

**Antes (a mano, una vez por mini PC):**
1. Instalar Proxmox en el mini PC, conectado a la sede en un puerto de la VLAN 60 (SW1 Fa0/6-8), con una IP fija
   de la VLAN 60 fuera del DHCP (p. ej. `10.10.60.50/24`, puerta `10.10.60.1`).
2. Desde el nodo de control: `ssh-copy-id -i ~/.ssh/nosub_ansible.pub root@<IP del mini PC>` (pide la contraseña
   de root del mini PC una vez y apunta su huella).
3. Añadir la caja a `inventories/cajas/hosts.yml` con su apartado `minipc` (ver `defaults/main.yml`):
   `minipc: { ip: 10.10.60.50, ip_casa: <IP del mini PC en casa> }`.

**Después:**
- `ansible-playbook playbooks/caja_nueva.yml -e caja=<caja>`: crea el contenedor de la caja en el mini PC
  (Debian 13, `nesting` y `keyctl` para Docker), la prepara y la da de alta en la sede (túnel, portal, monitorización).
- `ansible-playbook playbooks/caja_entregar.yml -e caja=<caja>`: pasa la caja y el mini PC a sus IPs de casa
  (copia de la red anterior en `/etc/network/interfaces.antes-de-casa`) y apaga el mini PC. En casa: enchufarlo
  al router, encenderlo y poner la IP de la caja como DNS en el DHCP del router.

Probado el 2026-10-22 usando prx como mini PC (caja de prueba en la casa simulada del cliente A): creación,
preparación, alta, entrega, túnel desde casa y bloqueo de anuncios bien. El cambio de IP del propio mini PC,
probado sobre una copia del `/etc/network/interfaces` que deja el instalador de Proxmox. Falta probarlo con un mini PC real.
