# nosub-infra

Receta de la infraestructura de **NoSub** (proyecto ASIX): la sede central y las cajas de cliente.

**Regla del proyecto:** lo que no está en Git no existe. Todo se monta con Ansible desde aquí;
nada se configura a mano. Con un solo comando se reconstruye la sede o se prepara una caja nueva.

## Carpetas

| Carpeta | Qué hay |
|---|---|
| `inventories/sede/` | Las máquinas de la sede y sus datos (IPs, VLANs). Secretos cifrados en `group_vars/all/vault.yml` |
| `inventories/cajas/` | Una entrada por caja de cliente |
| `roles/` | Un rol por servicio: cómo se instala y configura |
| `playbooks/` | Las órdenes: `sede.yml`, `caja_nueva.yml`, `actualizar_cajas.yml` |
| `network/` | Configuración de routers, switches y AP |
| `gns3/` | Topologías de GNS3 exportadas |
| `k8s/` | Manifiestos de las apps de DAM/DAW |
| `docs/` | Planos de red, plan de riesgos, plan de contingencia |
| `scripts/` | Lo poco que no puede hacer Ansible (arranque inicial) |

## Uso

```bash
ansible-playbook playbooks/sede.yml              # monta o actualiza toda la sede
ansible-playbook playbooks/sede.yml --check      # simula: dice qué cambiaría, sin tocar nada
ansible-playbook playbooks/red_fisica.yml        # genera las configs de routers, switches y AP (network/generado/)
ansible-vault edit inventories/sede/group_vars/all/vault.yml   # editar secretos
```

La contraseña de Ansible Vault **no está en el repositorio**: se guarda en `~/.nosub-vault-pass`
(permisos 600) en el nodo de control. Sin ella no se pueden leer los secretos.

## Fases

1. Propuesta y diseño ✅
2. Base de la sede: red, Proxmox, OPNsense, Gitea y Ansible
3. Servicios de la sede: DNS, DHCP, BBDD, intranet y extranet, proxies, monitorización y panel ADMIN
4. Producto e integración: caja, WireGuard, k3s, cloud, GNS3
5. Cierre: planes de riesgos y contingencia, simulacro, documentación
