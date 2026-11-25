# CLAUDE.md — nosub-infra

Proyecto de ASIX del grupo **Jeff Bezos** (Yassin, Edmundo y Ramanvir): **NoSub**, una sede central más una «caja sin
suscripciones» en casa del cliente. Qué es y qué hay montado: `README.md`. Todo se habla y se escribe en **español**.

## Quién trabaja aquí
Los tres entran en `prx` como root y usan la misma sesión de Claude. **Si no se ha presentado nadie, pregunta
primero quién es** (Yassin, Edmundo o Ramanvir) y pon su nombre en los commits y en el registro de cambios.

| Persona | Área |
|---|---|
| Edmundo | Red: routers R1-R3, switches SW1/SW2, AP, OPNsense, VPN, entrada segura de la alta automática |
| Ramanvir | Servicios de la sede: DNS, DHCP, proxy, PostgreSQL, intranet, portal, pedidos y servidor de alta |
| Yassin | Plataforma (Proxmox, Ansible, copias, monitorización, cloud) e imagen base y agente de la caja |

## Normas
1. **Lo que no está en Git no existe.** Nada se configura a mano: se cambia el rol y se aplica con Ansible.
2. **Los playbooks se lanzan siempre desde `playbooks/`** (`ansible-playbook playbooks/…`). No los copies a otra
   carpeta: el rol `opnsense` busca con `playbook_dir` las claves de las cajas y del VPS, y desde otro sitio
   quitaría sus túneles.
3. **Antes de lanzar `playbooks/sede.yml` se avisa al grupo**: cambia el laboratorio en directo.
4. **Secretos solo en el Vault** (`inventories/sede/group_vars/all/vault.yml`, con `ansible-vault`). Nunca en claro
   en el repositorio, en commits ni en mensajes.
5. Antes de un cambio grande en una máquina, foto de seguridad (`qm snapshot` / `pct snapshot`) y borrarla al terminar.
6. Commits en `main`, con mensaje en español que diga qué y por qué; `git push gitea main` (Gitea hace espejo en GitHub).
7. **Solo las máquinas 200 en adelante son del proyecto.** Los CT 101-104 de `prx` (Navidrome, inicio, DNS/Caddy,
   Jellyfin) y lo que hay fuera de Proxmox son servicios personales de Yassin: no se tocan.

## Máquinas del laboratorio (en prx)
| ID | Nombre | Qué es |
|---|---|---|
| VM 200 | opnsense | Firewall, VLANs 10-60, DMZ, WireGuard. Web con contraseña + código TOTP (`scripts/totp-qr.sh <usuario>`) |
| VM 210 | gns3 | GNS3, se enciende a demanda (`playbooks/gns3.yml`) |
| CT 220 | gitea | Repositorio Git |
| CT 221 | red-int | DNS (Bind9), DHCP (Kea), proxy (Squid) |
| CT 222 | bbdd | PostgreSQL (Rocky Linux) |
| CT 223 | monitor | Prometheus, Grafana, Alertmanager |
| CT 224 | intranet | Wiki.js y Nextcloud |
| CT 230 | extranet | Portal de clientes y Traefik (DMZ) |
| VM 231 | k3s | Kubernetes para los proyectos DAM/DAW |
| CT 261-262 | caja-garcia, caja-ruiz | Cajas de prueba |
| CT 290 | vps | VPS del cloud simulado |

## Comprobar que todo va
`scripts/probar-red.sh`, `probar-dhcp.sh`, `probar-vpn.sh` y `probar-cajas.sh`. Una segunda pasada de
`sede.yml` debe dar 0 cambios.

## Documentos
`docs/`: `plan.md`, `red.md`, `riesgos.md`, `contingencia.md`, `simulacro.md`, `rgpd.md`, `defensa.md`. Si un cambio
contradice uno de ellos (por ejemplo, una medida de seguridad), actualízalo en el mismo commit.

**Ante los tutores, el proyecto está en fase de planificación.** Los documentos de entrega de clase no deben decir
que algo ya está montado o medido en el laboratorio.
