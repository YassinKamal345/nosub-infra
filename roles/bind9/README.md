# Rol bind9

**DNS de la sede** en el contenedor `red-int` (CT 221, 10.10.20.11).

- Es el dueño de la zona `nosub.lan` y de su zona inversa (`10.10.in-addr.arpa`). Las dos se generan con los datos del inventario: los equipos fijos (`dns_nombres` y `dns_alias`, en `group_vars/all/servicios_red.yml`) y todos los contenedores (lista `contenedores`). Al crear un contenedor nuevo, su nombre aparece solo.
- También resuelve los nombres de Internet (empezando por los servidores raíz y comprobando DNSSEC), pero solo para la sede: `bind_redes_permitidas`.
- No hace transferencias de zona a nadie.

**Comprobar:** `dig @10.10.20.11 gitea.nosub.lan`, `dig @10.10.20.11 -x 10.10.20.10`, `dig @10.10.20.11 debian.org`.
