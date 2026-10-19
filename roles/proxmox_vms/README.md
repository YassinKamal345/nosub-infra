# Rol proxmox_vms

Crea los contenedores LXC de la sede **por la API de Proxmox**, a partir de la lista `contenedores`
de `inventories/sede/group_vars/all/main.yml`.

**Cómo se conecta a la API (sin usar root):**
- Crea el usuario `ansible@pve` con el rol `NoSubAnsible`, que solo tiene los permisos para crear,
  configurar y encender máquinas (lista en `defaults/main.yml`).
- Le crea el token `nosub`. Proxmox solo enseña el secreto una vez: se guarda en
  `/root/.nosub-pve-token` (permisos 0600) y **nunca entra en el repositorio**. Si se borra el fichero,
  la siguiente pasada crea un token nuevo.

**Cada contenedor:**
- VMID = 2 + VLAN + número: servidores (VLAN 20) 220-229, DMZ (VLAN 30) 230-239. OPNsense es la 200.
- Conectado a `vmbr1` con la etiqueta de su VLAN; puerta de enlace y DNS = OPNsense (`.1` de su red).
- Sin privilegios (`unprivileged`), arranca solo después de OPNsense, entra la clave SSH del nodo de control.
- Sistema: `debian` (por defecto), `ubuntu` o `rocky`. Las plantillas se descargan si faltan.

**Detalle importante:** si un contenedor se borra y se vuelve a crear, tiene otra MAC y el firewall
aún recuerda la antigua. Por eso el rol hace que cada contenedor haga un ping a su puerta de enlace
al arrancar ("se presenta"); si no, no se le puede llegar durante unos minutos.

Probado: crear desde cero tarda ~20 s y una segunda pasada no cambia nada.

Deshacer un contenedor: `pct stop <vmid> && pct destroy <vmid> --purge`.
Deshacer el acceso a la API: `pveum user delete ansible@pve && pveum role delete NoSubAnsible && rm /root/.nosub-pve-token`.
