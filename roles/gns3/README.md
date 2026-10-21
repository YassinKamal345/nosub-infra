# Rol gns3

Monta **GNS3 2.2** en la VM `gns3` (VM 210, Ubuntu Server 24.04, VLAN 10, 10.10.10.20) y, dentro, el **ensayo de la
red física** de la sede: R1, R2, R3 y SW1, con los mismos datos que la configuración de los equipos reales
(`inventories/sede/group_vars/all/red_fisica.yml`, ver `docs/red.md`).

| Qué | Dónde |
|---|---|
| Web de GNS3 | `http://10.10.10.20:3080/` (por Tailscale), usuario `admin`. Contraseña: `/root/gns3-admin.clave` en la VM |
| Proyecto | "NoSub - red fisica" |
| Entrar en un equipo | En la VM: `nosub-gns3-en R2 vtysh -c "show ip ospf neighbor"` |

**La topología:**
- **Centro** (nodo Cloud): la "red del centro" de R1. Es una tarjeta de la VM en la **VLAN 50 de la sede real**:
  R1 coge IP por DHCP de Kea y sale a Internet de verdad. Es la integración de GNS3 con el sistema real.
- **R1** (borde): troncal a SW1 con las VLANs 99 (enlace con la sede) y 100 ("Internet" de los clientes), NAT y OSPF
  (da la ruta por defecto y la WAN de la sede).
- **SW1**: troncal hacia R1; VLAN 100 hacia R2 y R3; VLAN 99 hacia **Sede-WAN** (172.31.255.2, como la WAN de OPNsense).
- **R2 y R3** (clientes): NAT, DHCP para su red y OSPF. **Caja-A** y **Caja-B**: un equipo en cada red de cliente.

**Routers con FRRouting**, no Cisco: las imágenes de IOS son de pago. Se ensaya lo mismo (VLANs, OSPF, NAT y DHCP) con
los mismos datos. Si el centro tiene imágenes IOS, se pueden añadir a GNS3 y usar `network/generado/*.cfg`.

**Pruebas** (`tasks/pruebas.yml`, en cada pasada): R2 y R3 ven a R1 como vecino OSPF; R2 aprende la ruta por defecto
y la WAN de la sede; R1 tiene IP del centro; las cajas reciben IP (con su máscara) por DHCP; la caja A llega a la sede
y a Internet; la caja A no llega a la red del cliente B; la sede llega a R2.

**A demanda:** la VM no arranca sola con Proxmox (3 GB de RAM). `ansible-playbook playbooks/gns3.yml` la enciende,
la configura y monta el ensayo. Para apagarla: `qm shutdown 210`. Prometheus la vigila sin avisar si está apagada.

**Seguridad:** la web solo se abre desde la red de gestión y los administradores por Tailscale, y pide contraseña.
Ojo: GNS3 mete el usuario y la contraseña en la dirección al redirigir a su web (comportamiento de GNS3 2.2).
No copies esa dirección en ningún sitio.
