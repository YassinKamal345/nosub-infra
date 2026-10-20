# Configuración de routers, switches y AP

Las configuraciones **no se escriben a mano**: las genera Ansible a partir de los datos de la red
(`inventories/sede/group_vars/all/red_fisica.yml`) y las contraseñas del Vault (`vault_red_fisica`).
El diseño y los planos están en `docs/red.md`.

## 1. Generar las configuraciones

```bash
ansible-playbook playbooks/red_fisica.yml
```

Se crean en `network/generado/`: `R1.cfg`, `R2.cfg`, `R3.cfg`, `SW1.cfg`, `SW2.cfg` y `AP.txt`.
Esa carpeta **no se sube a Git** porque lleva las contraseñas.

## 2. Aplicarlas en el centro (primera vez, por consola)

Para cada router y switch:

1. Conectar el cable de consola y abrir la terminal (9600 baudios). Por ejemplo, en Linux o Mac: `screen /dev/ttyUSB0 9600`.
2. Dejar el equipo de fábrica: `write erase`, `delete flash:vlan.dat` (solo switches) y `reload`. Al preguntar por el asistente de configuración inicial, responder `no`.
3. Entrar en modo configuración: `enable` y `configure terminal`.
4. Pegar el contenido de su fichero `.cfg`.
5. Crear la clave de SSH (solo hace falta una vez): `crypto key generate rsa modulus 2048`.
6. Salir y guardar: `end` y `write memory`.

Para el AP: abrir su web (de fábrica suele estar en 192.168.0.1 o similar) y poner los valores de `AP.txt`.

**Orden recomendado:** SW1 → SW2 → R1 → R2 y R3 → AP. Así cada equipo tiene red cuando se configura.

## 3. Comprobar que funciona

| Dónde | Comando | Qué tiene que salir |
|---|---|---|
| SW1, SW2 | `show vlan brief` | Las VLANs con sus puertos |
| SW1, SW2 | `show interfaces trunk` | Los troncales con sus VLANs permitidas |
| SW1 | `show spanning-tree root` | SW1 es la raíz (prioridad 4096) |
| R1 | `show ip ospf neighbor` | R2 y R3 en estado FULL |
| R2, R3 | `show ip route` | Ruta por defecto `O*E2` aprendida de R1 |
| R2, R3 | `ping 172.31.255.2` | Responde la WAN de OPNsense |
| Puesto de administración | `ssh admin@10.10.10.3` | Entra en SW1 |
| Móvil en NoSub-Invitados | Navegar | Hay Internet, pero no llega a 10.10.x.x |

## 4. Cambios después

Se cambian los datos o las plantillas (`roles/red_fisica/templates/`), se vuelve a generar y se aplican
solo las líneas que cambian, por SSH. Más adelante se podrá hacer directamente desde Ansible
(colección `cisco.ios`, ya instalada).

## Si los equipos no son Cisco

Las plantillas están escritas para Cisco IOS (routers con dos puertos Gi0/0 y Gi0/1, y switches 2960 de 24 puertos).
- **Otro modelo Cisco:** cambiar los nombres de los puertos en `red_fisica.yml`. En un 3560/3750, poner `encapsulacion_troncal: true`.
- **Otra marca:** el diseño (`docs/red.md`) no cambia. Solo hay que escribir plantillas nuevas con los mismos datos.
