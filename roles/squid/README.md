# Rol squid

**Proxy de salida de la sede** (Squid) en el contenedor `red-int` (CT 221), puerto **3128**.

- Lo pueden usar gestión, servidores, empleados y lab cajas (`proxy_vlans` en `group_vars/all/servicios_red.yml`). Invitados y DMZ no.
- Guarda una copia (caché) de lo que se descarga: 64 MB en RAM y 1 GB en disco. Los paquetes `.deb` se guardan mucho tiempo, así que las actualizaciones de varias máquinas solo se descargan una vez.
- Solo deja usar HTTPS (CONNECT) hacia el puerto 443. No descifra el tráfico.
- De momento es un proxy **explícito**: cada equipo tiene que configurarlo (`http://proxy.nosub.lan:3128`). Si más adelante se quiere obligar a usarlo, se bloquea la salida web directa en OPNsense.

**Comprobar:** `curl -x http://proxy.nosub.lan:3128 -I https://debian.org` y mirar `/var/log/squid/access.log`.
