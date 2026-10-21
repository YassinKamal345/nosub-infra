# Rol intranet

Monta la **intranet** de los empleados en el contenedor `intranet` (CT 224, 10.10.20.14, VLAN de servidores).
Sus datos van en PostgreSQL (`bbdd`, bases `wikijs` y `nextcloud`).

| Qué | Dónde |
|---|---|
| **Wiki.js** (documentación interna) | `http://wiki.nosub.lan:3000` · laboratorio: `http://wiki.yk.internal` |
| **Nextcloud** (archivos, calendario, contactos) | `http://nube.nosub.lan` · laboratorio: `http://nube.yk.internal` |
| Administrador de Wiki.js | `yassin@nosub.lan` (contraseña: `vault_intranet.wiki_admin_clave`) |
| Administrador de Nextcloud | `yassin` (contraseña: `vault_intranet.nube_admin_clave`) |
| Archivos de Nextcloud | `/var/lib/nextcloud` (fuera de la carpeta web) |

Contraseñas: `ansible-vault view inventories/sede/group_vars/all/vault.yml`.
Quién puede entrar: empleados, gestión, VPN y servidores (reglas de OPNsense); invitados y DMZ no.

**Qué hace:**
- **Wiki.js 2** (la 3 sigue en beta) con el Node.js de Debian, con su propio usuario `wikijs`. La primera vez
  termina la instalación por su API (administrador y dirección) para que no haya que pasar por el asistente web.
- **Nextcloud** con nginx y PHP-FPM de Debian. Lo instala con `occ maintenance:install`; los ajustes
  (nombres permitidos, idioma, caché APCu) van en `config/nosub.config.php`, que genera Ansible.
  Las tareas de fondo las lanza un temporizador de systemd cada 5 minutos (`nextcloud-tareas.timer`).
- Sin HTTPS dentro: en la sede lo pondrá Traefik (fase 3.5).

**Cambiar de versión:**
- Wiki.js: poner `wiki_version` y `wiki_sha256` y lanzar `sede.yml` (cada versión va en su carpeta y el enlace `actual` apunta a la que se usa).
- Nextcloud: el rol solo lo descomprime la primera vez. Para actualizar:
  `runuser -u www-data -- php /var/www/nextcloud/updater/updater.phar` y después
  `runuser -u www-data -- php /var/www/nextcloud/occ upgrade`. Luego, cambiar `nube_version` y `nube_sha256` en el rol.
