# Protección de datos (RGPD)

Registro de las actividades de tratamiento de NoSub (artículo 30 del RGPD) y cómo se cumplen los principios
del reglamento en la infraestructura. Riesgo RS-23 del plan de riesgos.

> NoSub es una empresa ficticia del proyecto. Los clientes del laboratorio (`cliente-a`, `cliente-b`) son de
> prueba, con correos `example`.

## 1. Responsable

| | |
|---|---|
| Responsable del tratamiento | NoSub |
| Contacto para protección de datos | privacidad@nosub.lan |
| Delegado de protección de datos (DPD) | No es obligatorio: NoSub no trata datos a gran escala ni categorías especiales (art. 37) |
| Información a los clientes (art. 13) | Página **Privacidad** del portal de clientes (`/privacidad`, enlazada en el pie de todas las páginas) |

## 2. Registro de actividades de tratamiento

### T1 · Clientes y área de clientes

| | |
|---|---|
| Finalidad | Dar acceso al área de clientes, prestar el servicio de la caja y dar soporte |
| Base jurídica | Ejecución del contrato (art. 6.1.b) |
| Personas | Clientes |
| Datos | Nombre, usuario, correo, contraseña (solo su hash *scrypt*), cajas contratadas (nombre, red de la casa, apps) e incidencias |
| Dónde | PostgreSQL (`bbdd`, base `extranet`); el portal está en la DMZ (`extranet`) |
| Quién accede | El cliente (solo a lo suyo) y los administradores de NoSub |
| Cuánto tiempo | Mientras dure el contrato. Al darse de baja, Ansible borra el cliente, sus cajas y sus incidencias (contingencia, E11). Las copias que aún los contengan caducan solas (apartado 4) |

### T2 · Seguridad del área de clientes

| | |
|---|---|
| Finalidad | Frenar ataques de fuerza bruta contra las cuentas de los clientes |
| Base jurídica | Interés legítimo en proteger el servicio y las cuentas (art. 6.1.f) |
| Personas | Cualquiera que intente entrar en el portal |
| Datos | Usuario escrito e IP de cada inicio de sesión fallido; IP en los registros de Traefik |
| Dónde | Base `extranet` (tabla `intentos_fallidos`); registros del sistema de `extranet` |
| Cuánto tiempo | Intentos fallidos: **1 día** (limpieza cada hora, `extranet-limpiar.timer`). Registros del sistema: **30 días** (rol `registros`) |

### T3 · Soporte y monitorización de las cajas

| | |
|---|---|
| Finalidad | Mantener la caja del cliente funcionando y actualizada, y avisarle si falla |
| Base jurídica | Ejecución del contrato (art. 6.1.b) |
| Personas | Clientes |
| Datos | IP de la caja en la VPN, red de la casa, apps instaladas, métricas técnicas (CPU, memoria, disco, servicios) y hora de la última conexión |
| Dónde | Inventario (`inventories/cajas`), Prometheus (`monitor`), base `extranet` |
| Cuánto tiempo | Métricas: 30 días. El resto, mientras dure el contrato |
| **Lo que no se trata** | **El tráfico de la casa no pasa por la sede** (por el túnel solo pasa el soporte). El registro de consultas DNS de AdGuard (qué webs visita la casa) **se queda en la caja**, lo ve el cliente y solo guarda **24 horas** (AdGuard guarda 90 días de serie; rol `caja`, `caja_adguard_registro_horas`) |

NoSub puede entrar en la caja para darle soporte, así que respecto a lo que hay dentro de la caja actúa como
**encargado del tratamiento** del cliente: el contrato del servicio tiene que incluir las cláusulas del artículo 28
(solo se entra para dar soporte, con confidencialidad y borrando lo que haga falta al acabar el contrato).

### T4 · Empleados y teletrabajo

| | |
|---|---|
| Finalidad | Cuentas de trabajo (Gitea, wiki, Nextcloud, Grafana), acceso por VPN y administración |
| Base jurídica | Contrato de trabajo (art. 6.1.b) |
| Personas | Empleados |
| Datos | Nombre, usuario, correo, contraseña (hash), clave pública de la VPN, IP de conexión, documentos de trabajo |
| Dónde | Gitea, intranet (Wiki.js y Nextcloud), Grafana, OPNsense (VPN) |
| Cuánto tiempo | Mientras dure la relación laboral. Al irse, se le da de baja en la VPN (contingencia, E10) y en las aplicaciones |

## 3. Encargados y servicios externos

| Servicio | Para qué | Qué datos personales le llegan | Dónde | Medidas |
|---|---|---|---|---|
| Oracle Cloud (VPS) | Página de estado, entrada de la VPN y copias externas | Copias de seguridad **cifradas** (Oracle no puede leerlas: la clave está en el Vault de la sede); IP de quien se conecta a la VPN | Región de la UE (a elegir al crear la VM) | Cifrado (restic), solo añadir |
| GitHub | Copia del repositorio `nosub-infra` | **Ninguno de clientes reales** (regla: los datos de clientes viven en la base de datos, no en Git). Los secretos van cifrados (Vault) | EE. UU. (Data Privacy Framework) | Repositorio privado, token limitado |
| ntfy.sh | Avisos al móvil del administrador | Solo nombres de equipos y servicios de la sede. El aviso de una caja caída no dice de qué cliente es (se mira en Grafana) | EE. UU. | Canal con nombre secreto; avisos sin datos de clientes |

## 4. Plazos de conservación

| Qué | Cuánto | Cómo se cumple |
|---|---|---|
| Cuentas, cajas e incidencias de clientes | Mientras dure el contrato | Baja automática al quitarlo del inventario (E11) |
| Inicios de sesión fallidos | 1 día | `extranet-limpiar.timer` (cada hora) |
| Registros del sistema (IPs) | 30 días | journald, rol `registros` |
| Registro DNS de la caja | 24 horas | AdGuard, rol `caja` |
| Métricas (Prometheus) | 15 días | `prometheus_retencion` |
| Copias de PostgreSQL | 7 días | rol `postgresql` |
| Copias de máquinas (vzdump) | 7 diarias, 4 semanales, 3 mensuales (~3 meses) | Tarea de copias de Proxmox |
| Copias externas (restic) | **Hoy no caducan** | Pendiente: borrar las de más de 3 meses desde el VPS (apartado 6) |

## 5. Derechos de las personas

Se piden en privacidad@nosub.lan y se responden en **un mes** como máximo (art. 12).

| Derecho | Cómo se atiende |
|---|---|
| Acceso y portabilidad | Consulta en la base `extranet` de todo lo del cliente (cuenta, cajas, incidencias) y entrega en JSON |
| Rectificación | Nombre y correo: `extranet_clientes` y `sede.yml`. Datos de la caja: su entrada del inventario |
| Supresión | Baja del cliente (E11): se borra de la base al aplicar `sede.yml`. Las copias caducan solas |
| Limitación y oposición | Se estudia cada caso; si procede, se desactiva la cuenta |

## 6. Medidas de seguridad y pendientes

Las medidas técnicas (art. 32) están en el plan de riesgos (`docs/riesgos.md`, M1-M16): red separada por VLANs,
DMZ, VPN con clave por persona, cifrado de copias y secretos, HTTPS, contraseñas con hash, límite de intentos,
SSH solo con clave, parches automáticos y monitorización. **Brechas de seguridad:** contingencia, E6 (aviso a la
AEPD en 72 horas si afecta a datos personales, y a los clientes si el riesgo es alto).

Pendiente:
1. **Caducidad de las copias externas** (restic): borrar desde el VPS las de más de 3 meses. Desde la sede no se
   puede a propósito (modo solo añadir).
2. ~~Avisos sin nombres de clientes a ntfy.sh~~ (hecho 2026-10-22).
3. **En producción**, los clientes se dan de alta desde una herramienta de gestión, no en el repositorio:
   hoy `extranet_clientes` (con nombre y correo) está en Git porque son clientes de prueba.
4. **Contrato con cada cliente** con las cláusulas de encargo del artículo 28 (apartado T3).
