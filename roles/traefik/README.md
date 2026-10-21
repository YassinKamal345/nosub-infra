# Rol traefik

Monta **Traefik** (proxy inverso con HTTPS) en el contenedor `extranet` (CT 230, 10.10.30.10, **DMZ**),
delante del portal de clientes. Es la única puerta de entrada a las webs de la DMZ.

| Qué | Dónde |
|---|---|
| Portal de clientes | `https://portal.nosub.lan` (el HTTP del puerto 80 redirige a HTTPS) |
| Configuración fija | `/etc/traefik/traefik.yml` |
| Webs publicadas | `/etc/traefik/dinamica/sitios.yml` (sale de `traefik_sitios`; Traefik la relee sola) |
| Certificado | `/etc/traefik/certs/` (la clave privada se crea aquí y no sale de la máquina) |
| Métricas y `/ping` | `http://10.10.30.10:8082` (solo para la monitorización) |

**Certificados: autoridad propia "NoSub CA".** En el laboratorio no hay dominio público, así que no se puede
usar Let's Encrypt. Ansible firma el certificado con la CA de la sede:
- Certificado público de la CA: `inventories/sede/ca/nosub-ca.crt` (se instala en los equipos que tienen que fiarse de ella).
- Clave de la CA: en el Vault (`vault_ca.clave`). La firma se hace en el nodo de control: la clave nunca llega a la DMZ.
- La CA solo puede firmar para `nosub.lan` y `10.10.0.0/16` (*name constraints*): instalarla no permite suplantar otras webs.
- Certificados de 397 días; `sede.yml` los renueva solos cuando les quedan menos de 30. Grafana avisa si alguno caduca en menos de 21.

**Seguridad:** solo TLS 1.2 o superior; `sniStrict` (rechaza nombres que no están en el certificado);
HSTS de un año; cabeceras disfrazadas borradas (`aliasHeadersStrategy: delete`); el portal solo escucha en
`127.0.0.1`, así que no se puede saltar Traefik.

**Publicar otra web:** añadirla a `traefik_sitios` (nombre, nombres y dirección interna) y lanzar `sede.yml`;
el certificado se vuelve a firmar con el nombre nuevo.

**Cambiar de versión:** poner `traefik_version` y `traefik_sha256` (fichero `traefik_v<versión>_checksums.txt`
de GitHub) y lanzar `sede.yml`.

**En la sede real:** con dominio público, el certificado se pediría a Let's Encrypt, y OPNsense redirigiría los
puertos 80 y 443 de su WAN a 10.10.30.10 para que los clientes entren desde Internet (fase 4, con R2 y R3).
