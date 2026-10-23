# Rol caja

Monta la **caja del cliente**: el producto de NoSub. En la realidad es un mini PC N100 con Proxmox y la caja
es un contenedor Debian dentro de él. En el laboratorio, ese contenedor está en prx (rol `caja_lab`);
con un mini PC de verdad, lo crea el rol `caja_minipc`.
El rol es el mismo en los dos casos.

| Qué | Dónde (en la red de casa del cliente) |
|---|---|
| Página de inicio con todas las apps | `http://<ip_casa>` (Homepage) |
| Bloqueo de anuncios: DNS de toda la casa | `<ip_casa>`, puerto 53 (AdGuard Home) |
| Administración de AdGuard | `http://<ip_casa>:8080`, usuario `admin`. Contraseña: `/root/caja-admin.clave` en la caja |
| Apps elegidas por el cliente | `http://<ip_casa>:<puerto>` (Docker, `/opt/caja/compose.yml`) |
| Datos de las apps | `/opt/caja/datos/<app>/` |
| Túnel con la sede | `wg0`, IP `ip_vpn` (10.99.0.128/25) |

**Qué lleva cada caja:** lo dice su entrada en `inventories/cajas/hosts.yml`. AdGuard y la página de inicio
van siempre; el resto de apps se eligen en `apps` del catálogo `cajas_catalogo`
(`inventories/sede/group_vars/all/cajas.yml`). Cambiar las apps = editar `apps` y lanzar `actualizar_cajas.yml`.

**El túnel con la sede (WireGuard):**
- La caja abre el túnel hacia la sede. En casa del cliente no hace falta abrir ningún puerto del router.
- La **clave privada se crea en la caja y nunca sale de ella**. La clave pública se guarda en el repositorio
  (`inventories/cajas/wireguard/<caja>.pub`) y OPNsense la usa para dar de alta el túnel.
- Solo pasan por el túnel las respuestas al soporte de NoSub: el nodo de control (Ansible) y la monitorización.
  El tráfico de la casa nunca entra en la sede.

**Seguridad:**
- En el firewall de la sede (OPNsense), una caja no puede abrir conexiones hacia la sede ni hacia otras cajas.
  Solo el nodo de control (SSH) y el monitor (métricas) pueden entrar en ellas.
- En la caja, el cortafuegos (`/etc/nftables.conf`) deja entrar por SSH y métricas solo al soporte. Desde la casa
  solo se llega al DNS, a la web de AdGuard, a la página de inicio y a las apps. Desde el túnel no se llega a las apps.
- La contraseña de AdGuard se genera en la propia caja.

**Monitorización:** Prometheus lee las métricas de cada caja por el túnel (grupo `cajas`, con el cliente).
Si una caja no responde en 5 minutos salta el aviso `CajaSinConexion`.

**Si se cae la sede**, la caja sigue funcionando: AdGuard y las apps son locales.

**Playbooks:**
- `playbooks/caja_nueva.yml -e caja=<nombre>`: prepara la caja en la VLAN 60, da de alta su túnel, la extranet y la
  monitorización, y la entrega en casa del cliente (en el laboratorio, la cambia de red).
- `playbooks/actualizar_cajas.yml [-l <caja>]`: actualiza las cajas ya entregadas, por la VPN.
