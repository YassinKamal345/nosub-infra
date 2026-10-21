# Rol extranet

Monta el **portal de clientes** de NoSub en el contenedor `extranet` (CT 230, 10.10.30.10, en la **DMZ**).
Es una aplicación propia en Python (Flask), con el código en `files/portal/` y los datos en PostgreSQL (`bbdd`, base `extranet`).

| Qué | Dónde |
|---|---|
| Portal | `http://portal.nosub.lan:8080` · laboratorio: `http://portal.yk.internal` |
| Comprobación | `http://10.10.30.10:8080/salud` (la usa la monitorización) |
| Clientes de prueba | `cliente-a` (Familia García) y `cliente-b` (Estudio Ruiz); contraseñas en `vault_extranet.clientes` |

**Qué puede hacer un cliente:** entrar con su usuario, ver sus cajas (dirección en la VPN, red de su casa,
servicios y última conexión) y abrir incidencias sobre ellas.

**Cómo está hecho:**
- `portal.py`: la web. `bd.py`: la conexión y las tablas (`clientes`, `cajas`, `incidencias`).
  `gestion.py`: lo usa Ansible para crear las tablas y dar de alta los clientes de `extranet_clientes`.
- Corre con gunicorn y su propio usuario `extranet`, con systemd endurecido.
- Seguridad: contraseñas con hash (scrypt), sesión con cookie `HttpOnly`, protección CSRF en los formularios,
  cabeceras de seguridad y consultas SQL con parámetros (sin inyección SQL). Cada cliente solo ve lo suyo.
- **Por qué en la DMZ:** es lo único que verán los clientes desde Internet. Si alguien lo rompe, desde la DMZ
  solo llega a Internet y al puerto 5432 de `bbdd` (regla "Extranet: a su base de datos" en OPNsense), y
  PostgreSQL solo le deja entrar en su base (`pg_hba`).
- En la fase 3.5, Traefik pondrá HTTPS delante; en la fase 4, las cajas rellenarán su última conexión.

**Añadir un cliente:** añadirlo a `extranet_clientes` (en `defaults/main.yml` o en el inventario), poner su
contraseña en `vault_extranet.clientes.<usuario>` y lanzar `sede.yml`.
