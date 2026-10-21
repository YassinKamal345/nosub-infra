# Rol cloud

Monta el **VPS del cloud** (Ubuntu 24.04; Oracle Cloud Free Tier, ARM o AMD). Está fuera de la sede y hace tres cosas:

| Qué | Cómo |
|---|---|
| **Página de estado** | `https://estado.<ip-con-guiones>.sslip.io` (Gatus + Caddy con HTTPS). Sigue en línea aunque la sede se caiga |
| **Entrada de la VPN** | Las cajas y el teletrabajo se conectan al VPS (UDP 51820) y el VPS lo reenvía a la sede por el enlace |
| **Copias externas** | rest-server en `10.98.0.1:8000`, solo por el enlace y en modo "solo añadir" (rol `copias_externas`) |

**El enlace con la sede** (WireGuard, `wgsede`, 10.98.0.0/30) lo abre **la sede** (OPNsense, interfaz CLOUD) hacia
el VPS. Así la sede no necesita IP pública ni abrir puertos. La clave privada del VPS se crea en el VPS y no sale de él
(su pública está en `inventories/sede/cloud/vps.pub`). La de OPNsense se deriva de la del servidor, que está en el Vault.

**Qué muestra la página de estado:**
- Conexión con la sede: ping por el enlace.
- Portal de clientes: HTTPS por el enlace, con certificado válido de NoSub CA.
- Latido de la sede: el monitor avisa cada minuto. Si en 5 minutos no llega, sale en rojo.
- Copias externas: cada copia nocturna avisa. Si en 26 horas no llega ninguna, sale en rojo.

**Seguridad:**
- Cortafuegos propio (`/etc/nftables.conf`): desde Internet solo SSH (con clave), 80/443 y los puertos de WireGuard.
- Por el VPS no pasa nada más: desde Internet no se llega a la sede, y la sede no sale a Internet por aquí.
- A rest-server solo llegan las máquinas del grupo `copias_externas`, y no pueden borrar copias.
- En OPNsense, desde el enlace solo se puede hacer ping al firewall, entrar a la VPN y comprobar el portal.
- En las imágenes de Oracle se añaden los puertos a sus reglas de iptables, sin tocar las de sus servicios internos.

**Pasar al VPS de verdad (Oracle):** en `inventories/sede/group_vars/all/cloud.yml`, poner `cloud_laboratorio: false`
y `cloud_ip_publica: <IP de Oracle>`, y lanzar `sede.yml`. Antes, en la consola de Oracle, crear la VM con la clave
pública de Ansible y abrir TCP 22, 80, 443 y UDP 51820-51821. Con la IP pública, Caddy saca un certificado de Let's Encrypt.

**Si el VPS se cae:** las cajas pierden el túnel (no la casa: AdGuard y las apps son locales). Para volver a la
entrada directa: `vpn_entrada: sede` en `cloud.yml`, `sede.yml` y `actualizar_cajas.yml`.
