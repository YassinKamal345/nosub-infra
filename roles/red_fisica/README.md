# Rol red_fisica

Genera la configuración de los equipos de red del centro (R1-R3, SW1-SW2 y el AP) en `network/generado/`.
**No se conecta a ningún equipo:** solo escribe ficheros. Cómo aplicarlos: `network/README.md`. Diseño: `docs/red.md`.

| Qué | Dónde |
|---|---|
| Datos (puertos, IPs, VLANs, WiFi) | `inventories/sede/group_vars/all/red_fisica.yml` y `main.yml` (lista `vlans`) |
| Contraseñas (enable, admin, WiFi) | Vault: `vault_red_fisica` |
| Plantillas Cisco IOS | `templates/R1.cfg.j2` (borde), `cliente.cfg.j2` (R2 y R3), `switch.cfg.j2` (SW1 y SW2) |
| Valores del AP | `templates/AP.txt.j2` (se configura por web) |

Uso: `ansible-playbook playbooks/red_fisica.yml`
