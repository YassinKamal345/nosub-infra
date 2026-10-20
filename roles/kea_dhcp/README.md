# Rol kea_dhcp

**DHCP centralizado de la sede** (ISC Kea) en el contenedor `red-int` (CT 221, 10.10.20.11).

- Kea no está en las VLANs de los usuarios. OPNsense recoge las peticiones de cada VLAN y se las pasa (**DHCP relay**, en el rol `opnsense`). Kea sabe de qué VLAN viene cada una por la IP del relay (10.10.X.1).
- Reparte de la .100 a la .199 en las VLANs de `dhcp_vlans` (`group_vars/all/servicios_red.yml`): gestión, empleados, invitados y lab cajas. Servidores y DMZ llevan IPs fijas.
- DNS que da: Bind9 (10.10.20.11). A los invitados les da el DNS del firewall, porque no pueden llegar a los servidores.
- Concesiones: `/var/lib/kea/kea-leases4.csv`.

**Comprobar:** `journalctl -u kea-dhcp4-server` (una línea `DHCP4_LEASE_ALLOC` por cada IP dada) o mirar el fichero de concesiones.
