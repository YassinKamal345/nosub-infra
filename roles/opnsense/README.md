# Rol opnsense

Firewall de la sede: **OPNsense** en una VM, con las 6 VLANs, la DMZ y las reglas entre redes.

## Qué hace
1. Descarga la imagen oficial ya instalada (*nano*) y comprueba su sha256.
2. Crea la VM (`opnsense_vmid`, 2 núcleos, 1,5 GB): `vtnet0` → `vmbr1` (troncal con VLANs), `vtnet1` → `vmbr2` (WAN).
3. **Primera vez:** OPNsense arranca con su configuración de fábrica (192.168.1.1 sin VLAN). El rol crea un
   espacio de red temporal (`opnboot`) para llegar a esa IP sin tocar la red de Proxmox.
   **Siguientes veces:** entra por la red de gestión (`https://10.10.10.1`).
4. `opnsense-aplicar.py` descarga el `config.xml`, le aplica la especificación y, si cambia, lo sube
   ("Restaurar"). Después el rol reinicia la VM (`qm reboot`) y espera a que vuelva por gestión.

Lo que gestiona el repositorio lleva uuid fijos y las reglas empiezan por `[nosub]`;
lo demás que se configure a mano en OPNsense no se toca.

## Red resultante
| VLAN | Interfaz | IP del firewall | Puede ir a |
|---|---|---|---|
| 10 Gestión | lan (vlan01) | 10.10.10.1 | todo |
| 20 Servidores | opt1 (vlan02) | 10.10.20.1 | todo menos gestión |
| 30 DMZ | opt2 (vlan03) | 10.10.30.1 | solo Internet |
| 40 Empleados | opt3 (vlan04) | 10.10.40.1 | servidores, DMZ, Internet |
| 50 Invitados | opt4 (vlan05) | 10.10.50.1 | solo Internet |
| 60 Lab cajas | opt5 (vlan06) | 10.10.60.1 | servidores, Internet |
| WAN | wan (vtnet1) | 172.31.255.2/30 | puerta: Proxmox 172.31.255.1 |

Todas las VLANs pueden usar el DNS del firewall y hacerle ping. La web y el SSH del firewall solo
desde gestión (SSH solo con clave: `~/.ssh/nosub_ansible`).

## Variables
`defaults/main.yml` (VM, versión, IPs, reglas). La contraseña de root está en el Vault
(`vault_opnsense_root_clave`): `ansible-vault view inventories/sede/group_vars/all/vault.yml`.

## Comprobarlo
```bash
ansible-playbook playbooks/sede.yml        # 2.ª pasada y siguientes: changed=0
scripts/probar-red.sh                      # aislamiento entre VLANs
ssh -i ~/.ssh/nosub_ansible root@10.10.10.1
```
Nota: tras crear la VM desde cero, la segunda pasada aún aplica un pequeño ajuste (OPNsense
retoca su configuración en el primer arranque); a partir de la tercera no cambia nada.

## Reconstruir desde cero
`qm stop 200 && qm destroy 200 --purge && ansible-playbook playbooks/sede.yml` (unos 2 minutos).
