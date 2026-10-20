# Rol monitorizacion

**Monitorización de la sede** en el contenedor `monitor` (CT 223, 10.10.20.13): Prometheus recoge los datos y Grafana los enseña.

| Pieza | Qué hace | Dónde escucha |
|---|---|---|
| Prometheus (Debian) | Recoge métricas cada 15 s y las guarda 30 días. Avisos en `reglas-nosub.yml` | 127.0.0.1:9090 |
| node_exporter (rol aparte) | Métricas de cada máquina: CPU, RAM, disco, red | cada máquina :9100 |
| blackbox_exporter (Debian) | Comprueba desde fuera que cada servicio responde (`monitor_comprobaciones`) | 127.0.0.1:9115 |
| postgres_exporter (Debian) | Estadísticas de PostgreSQL (usuario `prometheus`, solo lectura) | 127.0.0.1:9187 |
| Grafana (apt.grafana.com) | Paneles. Guarda sus datos en PostgreSQL (base `grafana`) | :3000 |

Solo Grafana se puede abrir desde fuera, con usuario y contraseña (`yassin`, contraseña en `vault_grafana.admin_clave`). En el laboratorio se entra por `http://grafana.yk.internal`.

**Paneles** (carpeta *NoSub*, salen del repositorio y no se pueden cambiar desde la web):
- **ADMIN · Sede NoSub** (`files/paneles/admin.json`, página de inicio): equipos encendidos, servicios caídos, avisos, PostgreSQL, CPU/RAM/disco de cada máquina, red y una franja de tiempo con el estado de cada servicio.
- **Equipos (Node Exporter Full)** (`files/paneles/nodos.json`): el detalle de cada máquina. Es el panel 1860 de grafana.com (revisión 45).

**Avisos:** equipo sin respuesta, servicio caído, disco por encima del 85 % y RAM por encima del 90 %. De momento solo se ven en Grafana; enviarlos (correo o ntfy) queda pendiente.

**Añadir una comprobación:** una línea en `monitor_comprobaciones` (`group_vars/all/servicios_red.yml`) y lanzar `sede.yml`.
