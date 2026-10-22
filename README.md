# nosub-infra

Infraestructura de **NoSub**, el proyecto de ASIX: una empresa ficticia que vende una **"caja sin suscripciones"**.
Es un mini PC que el cliente tiene en casa, con bloqueo de anuncios y sus propias apps (música, PDF…), y que la
empresa mantiene a distancia desde su **sede central**.

Este repositorio es **la receta completa**: con él se monta desde cero la sede entera (unos 11 minutos) o una caja
nueva. **Regla del proyecto: lo que no está en Git no existe.** Nada se configura a mano: todo pasa por Ansible.

## Qué hay montado

```
             Internet ── VPS en el cloud (página de estado, copias, entrada de la VPN)
                │                 │ túnel WireGuard
          ┌─────┴──────┐          │
          │  OPNsense  │──────────┘          Casa del cliente
          │ firewall · │ ◄── WireGuard ───── Caja (AdGuard + apps)
          │ DMZ · VPN  │ ◄── WireGuard ───── Teletrabajo
          └─────┬──────┘
   ┌────────────┼──────────────┬─────────────┬───────────┬──────────────┐
 VLAN 10      VLAN 20        VLAN 30       VLAN 40     VLAN 50        VLAN 60
 gestión      servidores     DMZ           empleados   invitados      lab de cajas
 Proxmox      Gitea          portal +      (puestos)   (solo          (preparar
 GNS3         DNS·DHCP·proxy Traefik HTTPS             Internet)      cajas)
              PostgreSQL     k3s (DAM/DAW)
              Prometheus+Grafana
              Wiki.js+Nextcloud
```

Todo corre en **un servidor Proxmox** (laboratorio: `prx`; definitivo: la centralita del centro). Los servidores
son contenedores LXC y algunas VMs, con **3 distribuciones**: Debian 13, Rocky Linux 10 y Ubuntu Server 24.04.

## Requisitos del proyecto y dónde se cumplen

| Requisito | Solución | Dónde |
|---|---|---|
| Servidor físico con hipervisor de tipo 1 | Proxmox VE | `roles/proxmox_vms` |
| 3 distribuciones Linux | Debian (casi todo), Rocky Linux (PostgreSQL), Ubuntu (k3s, GNS3, VPS) | `inventories/sede/hosts.yml` |
| Diseño de red lógico y físico | Planos y tablas | `docs/red.md` |
| Material de red del centro (2 switches, 3 routers, AP) | Configuraciones generadas con Ansible | `roles/red_fisica`, `network/` |
| GNS3 sobre el sistema real | VM con GNS3; ensayo de R1-R3 y SW1 conectado a una VLAN real | `roles/gns3`, `playbooks/gns3.yml` |
| 3 VLANs como mínimo | 6 VLANs + red de la VPN | `roles/opnsense`, `docs/red.md` |
| Firewall con DMZ y VPN | OPNsense: DMZ en la VLAN 30, WireGuard (personas, cajas y cloud) | `roles/opnsense` |
| DNS | Bind9 (zona `nosub.lan`) en la sede; AdGuard en cada caja | `roles/bind9`, `roles/caja` |
| DHCP centralizado | Kea, con relay en OPNsense para cada VLAN | `roles/kea_dhcp` |
| Intranet y extranet con base de datos | Wiki.js + Nextcloud; portal de clientes propio (Python). Todo con PostgreSQL | `roles/intranet`, `roles/extranet`, `roles/postgresql` |
| Panel de estadísticas ADMIN | Grafana: panel "ADMIN · Sede NoSub" | `roles/monitorizacion` |
| Monitorización | Prometheus + blackbox + avisos al móvil (Alertmanager → ntfy) | `roles/monitorizacion` |
| Proxy inverso y proxy | Traefik con HTTPS (CA propia) en la DMZ; Squid de salida | `roles/traefik`, `roles/squid` |
| Repositorio Git | Gitea propio con espejo privado en GitHub | `roles/gitea` |
| Hosting de contenedores para DAM/DAW | k3s, un espacio aislado y con cuota por proyecto | `roles/k3s` |
| Plan de riesgos de seguridad | 23 riesgos valorados, 19 medidas, plan de acción | `docs/riesgos.md` |
| Plan de contingencia | 12 escenarios con pasos, RTO/RPO y simulacros | `docs/contingencia.md`, `docs/simulacro.md` |
| Algún servicio en el cloud | VPS: página de estado, copias externas cifradas, entrada de la VPN | `roles/cloud`, `roles/copias_externas` |
| Todo desplegable con Ansible | 24 roles, secretos con Ansible Vault | este repositorio |

## Uso

```bash
ansible-playbook playbooks/sede.yml                       # monta o actualiza toda la sede (una 2.ª pasada: 0 cambios)
ansible-playbook playbooks/caja_nueva.yml -e caja=<caja>   # prepara una caja nueva y la entrega al cliente
ansible-playbook playbooks/actualizar_cajas.yml            # actualiza las cajas ya entregadas, por la VPN
ansible-playbook playbooks/gns3.yml                        # enciende GNS3 y monta el ensayo de la red física
ansible-playbook playbooks/red_fisica.yml                  # genera las configs de routers, switches y AP
ansible-vault edit inventories/sede/group_vars/all/vault.yml   # editar secretos
```

La contraseña del Vault **no está en el repositorio**: está en `~/.nosub-vault-pass` (permisos 600) en el nodo de
control y en el gestor de contraseñas del administrador. Sin ella no se pueden leer los secretos ni las copias.

## Pruebas

| Script | Qué comprueba |
|---|---|
| `scripts/probar-red.sh` | Aislamiento entre las VLANs (quién llega a quién) |
| `scripts/probar-dhcp.sh` | Que cada VLAN recibe IP, puerta de enlace y DNS de Kea |
| `scripts/probar-vpn.sh` | Teletrabajo por WireGuard: a qué llega y a qué no |
| `scripts/probar-cajas.sh <caja>` | Una caja: DNS y anuncios en la casa, aislamiento, túnel con la sede |
| `scripts/simulacro-restauracion.sh` | Recupera copias reales (restic y vzdump) aparte, sin tocar nada |
| `scripts/simulacro-corte-luz.sh` | Apaga la sede de golpe y comprueba que vuelve sola y avisa |
| `scripts/totp-qr.sh <usuario>` | QR del segundo factor de la web de OPNsense |

## Documentación

| Documento | Contenido |
|---|---|
| `docs/plan.md` | Plan de montaje por fases, con lo hecho en cada una |
| `docs/red.md` | Diseño de red lógico y físico |
| `docs/riesgos.md` | Plan de riesgos de seguridad |
| `docs/contingencia.md` | Plan de contingencia |
| `docs/simulacro.md` | Actas de los simulacros (restauración y corte de luz) |
| `docs/rgpd.md` | Protección de datos: registro de tratamientos, plazos y derechos |
| `docs/defensa.md` | Guion de la defensa y demostración |
| `roles/*/README.md` | Cómo funciona cada pieza |

## Estado (2026-10-22)

Las 5 fases están hechas en el laboratorio. Queda pendiente (ver `docs/plan.md`):
- pasar el VPS simulado al de Oracle Cloud (falta la IP);
- montar la centralita y aplicar las configuraciones en el material de red del centro (faltan los modelos);
- un disco aparte para las copias vzdump (riesgo RS-14, el único que sigue en rojo);
- la parte individual de cada miembro del grupo.
