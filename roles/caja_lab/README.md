# Rol caja_lab

**Solo para el laboratorio.** Hace en prx lo que en la realidad es físico:

- `crear`: crea el contenedor que hace de mini PC de la caja (Debian, con `nesting` y `keyctl` para Docker) y lo
  conecta a la **VLAN 60** (laboratorio de cajas), con `ip_preparacion`. Es como enchufar un N100 nuevo en la sede.
- `entregar`: lo cambia a la **casa simulada** del cliente (bridge `vmbr8N` del rol `red_lab`, con `ip_casa`).
  Es como llevar la caja a casa del cliente. Desde allí la caja abre el túnel con la sede.

Las casas simuladas son como una conexión doméstica. Proxmox hace de router de casa: salida a Internet con NAT
y llegada a la sede solo por su WAN (como una IP pública). No ven la red de la oficina, ni la sede por dentro,
ni las otras casas, y desde fuera no se puede abrir ninguna conexión hacia ellas.

Lo usa `playbooks/caja_nueva.yml` solo con las cajas que tienen `lab` en `inventories/cajas/hosts.yml`.
