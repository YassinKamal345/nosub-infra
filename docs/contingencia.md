# Plan de contingencia

El plan de riesgos (`docs/riesgos.md`) dice qué puede salir mal y cómo lo evitamos. Este documento dice
**qué hacer cuando ya ha pasado**: cómo seguir trabajando, cómo recuperar los servicios y los datos, y
cómo comprobar que todo ha vuelto.

Cada paso usa lo que ya está montado en el repositorio `nosub-infra`. Los comandos se lanzan en el
**nodo de control** (hoy, Proxmox), desde la carpeta del repositorio, salvo que se diga otra cosa.

## 1. La idea en una frase

**La configuración vuelve con Ansible y los datos vuelven de las copias.** Ansible rehace cualquier
servidor (o la sede entera) desde Git en minutos. Lo que Ansible no puede inventar (repositorios, wiki,
ficheros de Nextcloud, clientes del portal) sale de las copias de seguridad.

## 2. Qué tenemos para recuperar

| Qué | Dónde | Cada cuánto | Cuánto se guarda |
|---|---|---|---|
| Recetas de toda la infraestructura | Repositorio `nosub-infra` en Gitea (CT 220), con espejo privado en GitHub | Cada cambio | Todo el historial |
| Secretos | `vault.yml` en el repositorio (cifrado). La **contraseña del Vault**, en el nodo de control y en el gestor de contraseñas del administrador | Cada cambio | — |
| Bases de datos (Gitea, Grafana, Wiki.js, Nextcloud, portal) | `pg_dump` en `bbdd`: `/var/lib/pgsql/copias/` | Diaria, 03:30 | 7 días |
| Datos de Gitea, Nextcloud y las copias de PostgreSQL | **restic** en el VPS del cloud: cifradas y en modo solo añadir (rol `copias_externas`) | Diaria, 04:15 | Todas (pendiente: borrar las antiguas desde el VPS) |
| Máquinas enteras (VMs y contenedores) | **vzdump** de Proxmox en el almacenamiento `backup` | Diaria, 03:00 | 7 diarias, 4 semanales, 3 mensuales |
| Configuración de Proxmox | `/mnt/backup/config/` | Diaria, 02:45 | 30 días |
| Datos de las cajas | En la propia caja (`/opt/caja/datos/`); son del cliente | — | No se copian en la sede |

> ⚠️ Hoy vzdump y Proxmox están en el **mismo disco** (riesgo RS-14). Al montar la centralita, la
> copia vzdump tiene que ir también a un disco USB o NAS.

## 3. Prioridades y objetivos de recuperación

- **RTO** (tiempo de recuperación): cuánto podemos tardar en volver a dar el servicio.
- **RPO** (punto de recuperación): cuántos datos podemos perder como máximo. Con copias diarias es,
  como mucho, **un día**.

Los tiempos salen de pruebas reales del laboratorio: la sede entera se reconstruyó desde cero en
11 minutos y OPNsense en menos de 2 (2026-10-21).

| Prioridad | Servicio | Por qué | RTO objetivo | RPO |
|---|---|---|---|---|
| 1 | Red: OPNsense, DNS y DHCP (`red-int`) | Sin red no funciona nada | 30 min | — (solo configuración) |
| 1 | VPN (teletrabajo y cajas) | El soporte a las cajas depende de ella | 30 min | — |
| 2 | PostgreSQL (`bbdd`) | Lo necesitan casi todos los servicios | 1 h | 24 h |
| 2 | Portal de clientes (extranet + Traefik) | Es lo que ven los clientes | 2 h | 24 h |
| 3 | Gitea | Sin él no se cambia la infraestructura (GitHub sirve mientras tanto) | 4 h | 24 h |
| 3 | Intranet (Wiki.js y Nextcloud) | Trabajo interno | 4 h | 24 h |
| 4 | Monitorización (Prometheus y Grafana) | La página de estado del cloud vigila lo básico mientras tanto | 1 día | Se aceptan perder las métricas |
| 4 | Hosting DAM/DAW (k3s) y GNS3 | No son críticos para la empresa | 1 día | Se vuelven a desplegar |

**Las cajas de los clientes siguen funcionando aunque caiga la sede**: AdGuard y las apps son locales.
Lo único que se pierde es el soporte remoto y la monitorización.

## 4. Cómo actuar ante cualquier incidente

1. **Detectar.** Llega un aviso al móvil (ntfy, desde la página de estado del cloud), una alerta en
   Grafana o la llamada de un usuario o cliente.
2. **Evaluar.** ¿Qué falla? ¿A quién afecta? Buscar el escenario en el apartado 5. Mirar la página de
   estado y el panel ADMIN de Grafana.
3. **Contener.** Si es un ataque: **aislar primero y recuperar después** (escenario E6).
4. **Recuperar.** Seguir los pasos del escenario.
5. **Comprobar.** Hacer las pruebas del apartado 6 y esperar a que se ponga en verde en Grafana y en la
   página de estado.
6. **Cerrar.** Rellenar el registro del incidente (apartado 8). Si algo del plan no ha funcionado,
   corregirlo en este documento.

**Regla de oro:** nada se arregla a mano en un servidor. Si hace falta un cambio, se hace en el
repositorio y se aplica con Ansible. Así el arreglo no se pierde en la siguiente reconstrucción.

## 5. Escenarios

### E1 · Corte de luz en la sede

- **Qué pasa:** la centralita no tiene SAI y se apaga de golpe. A los 2-3 minutos llega al móvil el aviso
  "Sede / Conexión con la sede" desde el VPS del cloud (3 comprobaciones fallidas seguidas).
- **Qué hacer:**
  1. Cuando vuelva la luz, la centralita se enciende sola (BIOS: *encender al volver la corriente*)
     y arranca las máquinas **en orden**: OPNsense, espera 45 s, DNS/DHCP, PostgreSQL y el resto.
     No hay que hacer nada.
  2. Si a los 10 minutos no ha llegado el aviso de "resuelto", ir a la sede y encender la centralita
     a mano.
  3. Si un servicio no arranca, ver el escenario E3.
- **Comprobar:** apartado 6. Si una base de datos no arranca después del corte, restaurarla (E4).
- **Tiempo:** unos 3 minutos desde que vuelve la luz (simulacro del 2026-10-22: todo arriba en 3 min y
  aviso de "resuelto" en el móvil; `scripts/simulacro-corte-luz.sh`, acta en `docs/simulacro.md`).

### E2 · Cae OPNsense (la sede se queda sin red)

- **Qué pasa:** nadie de la sede navega, no funciona la VPN y la página de estado marca la sede en rojo.
- **Qué hacer:**
  1. Abrir la consola de la VM 200 desde la web de Proxmox. Si está colgada, reiniciarla: `qm reboot 200`.
  2. Si arranca pero algo de la configuración está mal, volver a aplicarla:
     `ansible-playbook playbooks/sede.yml -l proxmox` (el rol `opnsense` sube la configuración del
     repositorio; a veces necesita dos pasadas).
  3. Si la VM está rota, se borra y se rehace: el mismo comando la crea desde cero en menos de 2 minutos.
  4. Si el nodo de control se ha quedado bloqueado (OPNsense bloquea una IP tras varios intentos fallidos),
     entrar por la consola serie, opción 8 (shell), y vaciar la tabla: `pfctl -t sshlockout -T flush`.
- **Comprobar:** `scripts/probar-red.sh` y `scripts/probar-vpn.sh`.
- **Tiempo:** 5-15 minutos.

### E3 · Cae un servicio o un contenedor

- **Qué pasa:** una alerta de Grafana ("servicio caído") o un aviso del cloud (el portal).
- **Qué hacer:**
  1. Mirar si el contenedor está encendido: `pct list`. Si no, `pct start <id>`.
  2. Ver por qué ha fallado: entrar (`pct enter <id>`) y mirar `systemctl status <servicio>` y
     `journalctl -u <servicio> -n 50`.
  3. Volver a aplicar su receta, que deja todo como debe estar:
     `ansible-playbook playbooks/sede.yml -l <máquina>`.
  4. Si el contenedor está roto: borrarlo, crearlo con la misma orden (el play `proxmox` lo crea) y
     recuperar sus datos (E4). Otra opción, más rápida: restaurar su vzdump del día anterior:
     `pct restore <id> /mnt/backup/dump/vzdump-lxc-<id>-<fecha>.tar.zst --storage local-lvm --force`.
- **Comprobar:** apartado 6.
- **Tiempo:** 5-30 minutos.

### E4 · Se borran o se estropean datos

Ejemplos: alguien borra una página de la wiki, un repositorio o un fichero de Nextcloud, o una base de
datos se corrompe.

- **Una base de datos** (copia de hace menos de 7 días), en `bbdd`:
  ```bash
  ls /var/lib/pgsql/copias/                         # elegir el día
  systemctl stop <app>                              # en la máquina de la app (gitea, wikijs...)
  sudo -u postgres pg_restore --clean --if-exists -d <base> /var/lib/pgsql/copias/<base>-<fecha>.dump
  systemctl start <app>
  ```
- **Ficheros (Gitea, Nextcloud) o copias de más de 7 días:** desde el cloud con restic, en la máquina:
  ```bash
  . /etc/restic/entorno
  restic snapshots                                  # qué copias hay
  restic restore <id> --target /tmp/recuperado      # en una carpeta aparte, nunca encima
  ```
  Después se copia a su sitio solo lo que se quiere recuperar. En Nextcloud, al acabar:
  `sudo -u www-data php /var/www/nextcloud/occ files:scan --all`.
- **La máquina entera tal como estaba ayer:** vzdump (escenario E3, paso 4).
- **Comprobar:** que el dato ha vuelto y que la app funciona (iniciar sesión).
- **Tiempo:** 15-60 minutos. Se pierde lo que se hizo desde la última copia.

### E5 · Avería del servidor (se pierde la centralita o su disco)

Es el peor caso. El plan es **montar otro Proxmox y rehacer la sede encima**.

1. Instalar Proxmox VE en el equipo de sustitución, con la IP de la centralita.
2. Instalar Ansible y Git y bajar el repositorio. Gitea estaba en el servidor averiado, así que se baja
   **del espejo de GitHub** (repositorio privado `YassinKamal345/nosub-infra`).
3. Copiar la **contraseña del Vault** del gestor de contraseñas a `~/.nosub-vault-pass` (permisos 600).
4. Crear el usuario de Ansible en Proxmox (`roles/proxmox_vms/README.md`) y lanzar:
   `ansible-playbook playbooks/sede.yml -e '{"gitea_espejos": []}'`
   (sin espejo, para que la Gitea nueva y vacía no sobrescriba GitHub).
5. Subir el repositorio a la Gitea nueva (`git push gitea main`) y lanzar `sede.yml` normal: vuelve
   a crear el espejo.
6. Recuperar los datos desde restic (E4): Gitea, las bases de datos y Nextcloud.
7. Si se conserva el disco de copias (USB o NAS), se pueden restaurar los vzdump directamente.
- **Comprobar:** apartado 6 completo.
- **Tiempo:** unas 2-3 horas (instalar Proxmox ~30 min, sede 11 min, datos ~1 h).

### E6 · Intrusión o ransomware

1. **Aislar:** cortar la entrada desde fuera (apagar la WAN de OPNsense o desenchufar el router).
   Si el ataque está en un solo servidor, apagarlo (`pct stop <id>`). **No borrar nada todavía:** sirve
   para saber qué ha pasado.
2. **Avisar:** al responsable de la empresa. Si se han visto datos de clientes, hay **72 horas** para
   notificarlo a la AEPD (RGPD).
3. **No pagar** ningún rescate. Las copias del cloud no se pueden borrar desde la sede.
4. **Recuperar en limpio:** rehacer los servidores afectados desde Git (E5, pasos 4-6) y restaurar los
   datos de una copia **anterior** al ataque.
5. **Cambiar todos los secretos:** contraseñas del Vault, claves de WireGuard, token de GitHub y
   contraseñas de los clientes del portal.
6. Revisar qué falló y añadir el riesgo o la medida al plan de riesgos.

### E7 · La sede se queda sin Internet

- **Qué pasa:** la página de estado marca la sede en rojo y los clientes no llegan al portal. Los empleados
  de la sede siguen trabajando con los servicios internos (wiki, Nextcloud, Gitea).
- **Cajas:** siguen funcionando en casa del cliente; solo se pierde el soporte remoto.
- **Qué hacer:** llamar al operador. Si va para largo, los teletrabajadores pueden ir a la sede.
- **Comprobar:** cuando vuelve, la página de estado lo dice sola y los túneles se reconectan solos.

### E8 · Cae el VPS del cloud

- **Qué pasa:** se pierde la página de estado y los avisos. Las copias externas no se hacen (el aviso
  "Copias externas" no llega). Como hoy la VPN entra por el VPS (`vpn_entrada: cloud`), **el teletrabajo
  y las cajas pierden el túnel**.
- **Qué hacer:**
  1. Para recuperar la VPN ya: cambiar `vpn_entrada: sede` en `inventories/sede/group_vars/all/cloud.yml`
     y aplicar `sede.yml` y `actualizar_cajas.yml`. Los teletrabajadores reciben su `.conf` nuevo.
  2. Recuperar el VPS: crear otro (Oracle u otro proveedor), poner su IP en `cloud_ip_publica` y lanzar
     `sede.yml`; el rol `cloud` lo deja como estaba. Volver a `vpn_entrada: cloud`.
  3. Las copias antiguas del VPS se pierden si se pierde su disco; las nuevas empiezan de cero. Mientras
     tanto quedan las copias locales (pg_dump y vzdump).
- **Tiempo:** VPN por la sede, 15 minutos; VPS nuevo, 1 hora.

### E9 · Se pierde un secreto clave

| Qué se pierde | Qué pasa | Qué hacer |
|---|---|---|
| Contraseña del Vault | No se pueden leer los secretos ni aplicar Ansible | Copiarla del gestor de contraseñas. Si se perdiera también allí: generar secretos nuevos para todo y rehacer, y **las copias restic serían ilegibles** |
| Gitea (el repositorio) | No se pueden aplicar cambios | Usar el espejo de GitHub (E5, pasos 2 y 5) |
| Token de GitHub | El espejo deja de actualizarse (la sede sigue igual) | Crear un token nuevo en GitHub, guardarlo en el Vault y aplicar el rol `gitea` |
| Clave SSH de Ansible (`nosub_ansible`) | Ansible no entra en los servidores | Crear otra y meterla por la consola de Proxmox (`pct exec`) o rehacer los contenedores |

### E10 · Baja de un teletrabajador o robo de su portátil

Cada persona tiene su propia clave de VPN, así que se corta solo a esa persona.

1. Quitar su línea de `opnsense_wg_usuarios` (`roles/opnsense/defaults/main.yml`).
2. Borrar su clave privada del Vault: `ansible-vault edit inventories/sede/group_vars/all/vault.yml`,
   apartado `vault_wg_privadas`.
3. Aplicar: `ansible-playbook playbooks/sede.yml -l proxmox`. OPNsense borra su peer (Ansible solo deja
   los que están en la lista) y deja de aceptar su clave.
4. Borrar su fichero `.conf` de `/root/nosub-wireguard/`.
5. Si se ha **robado** el portátil: cambiar también las contraseñas a las que tenía acceso (Gitea,
   intranet) y revisar los registros de acceso.
6. Hacer commit con el motivo.
- **Comprobar:** en OPNsense (VPN → WireGuard) su peer ya no aparece; en el firewall,
  `wg show wg0 allowed-ips` ya no muestra su IP.

### E11 · Baja, avería o robo de una caja

**Baja del cliente o caja robada:**
1. Quitar la caja de `inventories/cajas/hosts.yml` y borrar su clave pública
   `inventories/cajas/wireguard/<caja>.pub`.
2. Si el cliente se da de baja del todo, quitarlo también de `extranet_clientes`
   (`roles/extranet/defaults/main.yml`) y su contraseña del Vault (`vault_extranet.clientes`).
3. Aplicar `ansible-playbook playbooks/sede.yml`. Con eso:
   - OPNsense borra su peer y deja de aceptar su túnel;
   - Prometheus deja de vigilarla;
   - el portal borra la caja y, si se ha quitado el cliente, también al cliente, con sus cajas e
     incidencias (quedan en las copias el tiempo que se guardan).
4. Hacer commit con el motivo.
5. Si se recupera el mini PC: borrar el disco antes de volver a usarlo.
- **Comprobar:** `wg show wg0 allowed-ips` en el firewall ya no muestra su IP y el cliente ya no la ve
  en el portal. **Probado el 2026-10-22** con una caja de prueba: alta con `caja_nueva.yml`, baja
  así, y las otras cajas y la VPN siguieron bien (segunda pasada sin cambios).

**Avería de la caja (mismo cliente, mini PC nuevo):**
1. Instalar Proxmox en el mini PC nuevo y llevarlo a la VLAN 60 de la sede.
2. `ansible-playbook playbooks/caja_nueva.yml -e caja=<caja>`: crea una clave nueva en la caja,
   sustituye la pública en el repositorio y OPNsense acepta la nueva. La clave del mini PC averiado deja
   de servir.
3. Los datos de las apps del cliente estaban en la caja: si el disco se puede leer, copiar
   `/opt/caja/datos/`; si no, se pierden (se avisa al cliente al contratar).
- **Comprobar:** `scripts/probar-cajas.sh <caja>`.

### E12 · Disco lleno o certificado a punto de caducar

- **Disco lleno:** salta la alerta de Grafana antes de llenarse. Mirar qué ocupa (`du -xh / | sort -h | tail`),
  borrar copias o registros viejos o ampliar el disco del contenedor: `pct resize <id> rootfs +5G`.
- **Certificado:** se renueva solo al aplicar `sede.yml` cuando le quedan menos de 30 días. Si salta la
  alerta `CertificadoCaducaPronto`, lanzar `sede.yml -l extranet`.

## 6. Comprobar que todo ha vuelto

Después de cualquier recuperación:

| Prueba | Cómo | Bien si |
|---|---|---|
| Ansible deja todo como debe | `ansible-playbook playbooks/sede.yml` dos veces | La segunda pasada da 0 cambios |
| Aislamiento de la red | `scripts/probar-red.sh` | Todas las pruebas bien |
| DHCP | `scripts/probar-dhcp.sh` | 4/4 |
| VPN | `scripts/probar-vpn.sh` | Todas bien |
| Cajas | `scripts/probar-cajas.sh` | 19/19 por caja |
| Servicios | Grafana, panel ADMIN | Todas las sondas y equipos en verde |
| Desde fuera | Página de estado del cloud | Todo en verde |
| Datos | Iniciar sesión en Gitea, wiki, Nextcloud y portal | Están los datos de la última copia |

## 7. Mantener el plan vivo

- **Simulacros:** una vez al año como mínimo, y siempre antes de la puesta en producción:
  - Restaurar una base de datos y unos ficheros desde restic y desde vzdump: `scripts/simulacro-restauracion.sh`
    (hecho el 2026-10-22: 14/14 bien, 1 minuto; acta en `docs/simulacro.md`).
  - Corte de luz simulado: `scripts/simulacro-corte-luz.sh` (hecho el 2026-10-22: 11/11 bien a la tercera;
    los dos primeros destaparon un fallo real, ya corregido; acta en `docs/simulacro.md`).
  - Reconstrucción de la sede desde cero (hecha el 2026-10-21: 11 minutos, sin errores).
- **Revisión:** cada 6 meses, junto con el plan de riesgos, y después de cada incidente.
- **Actualizaciones:** los parches de seguridad se instalan solos cada día (rol `actualizaciones`). Una vez al mes,
  a mano: Proxmox, OPNsense y las apps con versión fijada; y reiniciar las máquinas con `ReinicioPendiente`.
- **Que funcione sin nosotros:** este documento, el repositorio y la contraseña del Vault en el gestor de
  contraseñas tienen que bastar para que otro administrador recupere la sede.

## 8. Registro de incidentes

Cada incidente se apunta en la wiki de la intranet con esta plantilla:

```
Fecha y hora:            inicio / fin
Qué pasó:
Cómo nos enteramos:      (aviso ntfy, Grafana, usuario...)
A quién afectó:          (servicios, clientes)
Qué se hizo:             (escenario y pasos)
Datos perdidos:          (desde qué hora)
Tiempo hasta recuperar:  (comparado con el RTO)
Qué cambiamos para que no vuelva a pasar:
```
