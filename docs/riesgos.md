# Plan de riesgos de seguridad

Este documento dice **qué puede salir mal** en la infraestructura de NoSub, **cómo de grave sería**
y **qué hacemos para evitarlo**. Lo que hay que hacer cuando un riesgo ya ha ocurrido (recuperar
servicios, restaurar copias) está en el plan de contingencia (`docs/contingencia.md`).

Cada medida que se cita está montada en el repositorio, con el rol o el fichero donde vive,
para que se pueda comprobar.

## 1. Cómo se ha hecho

1. **Inventario:** qué tenemos que proteger (apartado 2).
2. **Riesgos:** qué amenaza a cada cosa (apartado 4).
3. **Valoración:** cada riesgo recibe una nota de **probabilidad** y otra de **impacto**, de 1 a 3.
   El nivel de riesgo es el producto de las dos.
4. **Tratamiento:** para cada riesgo se decide qué hacer y se apuntan las medidas.
5. **Pendientes:** lo que falta se ordena por prioridad (apartado 5).

### Escala

| Nota | Probabilidad | Impacto |
|---|---|---|
| 1 · Baja | Muy raro, hace falta un atacante con mucho interés o mala suerte | Molestia: un servicio secundario cae poco rato, sin pérdida de datos |
| 2 · Media | Puede pasar alguna vez al año | Un servicio importante cae horas, o se pierden datos recientes recuperables |
| 3 · Alta | Pasa a menudo o es fácil de provocar | Se pierden datos de clientes, se filtran o la sede entera se queda sin servicio |

| Nivel (P × I) | Valor | Qué significa |
|---|---|---|
| 🟢 Bajo | 1-2 | Se acepta y se revisa una vez al año |
| 🟡 Medio | 3-4 | Necesita medidas; si quedan pendientes, se planifican |
| 🔴 Alto | 6-9 | Hay que reducirlo antes de poner el sistema en producción |

La valoración del apartado 4 es el **riesgo actual**, con las medidas que ya están montadas.

### Tratamientos

- **Reducir:** poner medidas para que sea menos probable o menos grave.
- **Aceptar:** se asume, porque reducirlo cuesta más de lo que protege.
- **Transferir:** que lo cubra otro (un proveedor, un seguro).
- **Evitar:** no hacer la actividad que provoca el riesgo.

## 2. Qué protegemos

| Activo | Dónde está | Por qué importa |
|---|---|---|
| Datos de clientes (portal de la extranet) | PostgreSQL, CT 222 `bbdd` | Datos personales (nombre, correo). Una fuga tiene consecuencias legales (RGPD) |
| Documentos internos (wiki y ficheros) | CT 224 `intranet` | El trabajo de la empresa |
| Código y recetas (`nosub-infra`) | Gitea, CT 220, con espejo privado en GitHub | Sin él no se puede reconstruir nada |
| Secretos (contraseñas, claves, CA) | `vault.yml` cifrado + contraseña del Vault en el nodo de control | Con ellos se entra en todo |
| Cajas de los clientes | En casa del cliente, unidas a la sede por WireGuard | Están fuera de nuestro control físico |
| Red de la sede | OPNsense (VM 200), switches, routers y AP | Si cae, cae todo |
| Servidor físico | Proxmox (la centralita) | Todo lo virtual vive en él |
| Apps de DAM/DAW | k3s, VM 231 (DMZ) | Código de terceros que se publica |
| Copias de seguridad | vzdump (local) y restic (VPS del cloud) | La última línea de defensa |

## 3. Medidas que ya están montadas

Medidas comunes que reducen muchos riesgos a la vez. En la tabla del apartado 4 se citan por su código.

| Código | Medida | Dónde |
|---|---|---|
| M1 | **Red separada en 6 VLANs** y cortafuegos entre ellas: cada red solo llega a lo que necesita (tabla en `docs/red.md`). Probado con `scripts/probar-red.sh` | rol `opnsense` |
| M2 | **DMZ**: lo que se publica (portal, k3s) está en la VLAN 30 y solo puede salir a Internet. Única excepción: la extranet llega a PostgreSQL por el puerto 5432 | rol `opnsense` |
| M3 | **VPN WireGuard** con una clave por persona y por caja. El teletrabajo no llega a la administración del firewall; las cajas no llegan a nada de la sede | rol `opnsense`, rol `caja` |
| M4 | **Todo con Ansible y Git**: nada se configura a mano, cada cambio queda en el historial, `--check` simula antes de aplicar y una segunda pasada da 0 cambios | repositorio entero |
| M5 | **Secretos cifrados** con Ansible Vault; la contraseña del Vault no está en el repositorio. Las claves privadas de WireGuard de las cajas se crean en la propia caja y nunca salen de ella | `vault.yml`, rol `caja` |
| M6 | **Copias externas** con restic al VPS: cifradas y en modo solo añadir (desde la sede no se pueden borrar, probado: 403). Copia diaria de PostgreSQL | roles `copias_externas`, `postgresql` |
| M7 | **Reconstrucción probada**: la sede entera se rehace desde cero en 11 minutos (prueba del 2026-10-21) | `playbooks/sede.yml` |
| M8 | **Monitorización**: Prometheus y Grafana con alertas (equipo caído, servicio caído, caja sin conexión, disco y memoria casi llenos, certificado a punto de caducar) y página de estado externa en el cloud (Gatus), que avisa al móvil por ntfy si la sede, el portal, el latido o las copias fallan | roles `monitorizacion`, `cloud` |
| M9 | **HTTPS con CA propia** ("NoSub CA", limitada a `nosub.lan` y `10.10.0.0/16`); los certificados se renuevan solos cuando les quedan menos de 30 días | rol `traefik` |
| M10 | **Acceso de administración solo con clave SSH** (root no puede entrar con contraseña) y solo desde gestión o la VPN de administración. Usuario de Ansible en Proxmox con permisos limitados (rol `NoSubAnsible`) | roles `proxmox_vms`, `opnsense` |
| M11 | **Protección del portal**: contraseñas con *scrypt*, protección CSRF en todos los formularios, cookies `Secure`, cabeceras de seguridad en Traefik y la misma respuesta (y el mismo tiempo) tanto si el usuario no existe como si la contraseña es incorrecta | rol `extranet`, rol `traefik` |
| M12 | **Seguridad de la red física**: solo SSH en los equipos, *BPDU guard* y *portfast* en los puestos, troncales sin negociación y VLAN nativa "aparcada" (999) | rol `red_fisica`, `docs/red.md` |
| M13 | **k3s aislado por proyecto**: un namespace, una cuota y una NetworkPolicy por proyecto; contenedores sin root; secretos cifrados en disco | rol `k3s` |
| M14 | **Bloqueo de fuerza bruta en el firewall**: OPNsense bloquea la IP tras varios intentos de acceso fallidos a su web o SSH | OPNsense (de serie) |
| M15 | **Parches de seguridad automáticos** cada día en Debian, Ubuntu y Rocky (servidores, VPS y cajas), sin reinicio automático. Prometheus avisa si una máquina lleva 3 días sin actualizarse bien (`ActualizacionesParadas`) o una semana esperando un reinicio (`ReinicioPendiente`). Proxmox, OPNsense y las apps con versión fijada se revisan a mano una vez al mes | rol `actualizaciones` |
| M16 | **Sin contraseñas débiles de administrador**: el rol de OPNsense no aplica la configuración si una contraseña de administrador tiene menos de 16 caracteres. El resto de contraseñas las genera Ansible (aleatorias, en el Vault) | rol `opnsense`, `vault.yml` |

## 4. Riesgos

### 4.1 Ataques desde fuera

| # | Riesgo | P | I | Nivel | Tratamiento y medidas | Pendiente |
|---|---|---|---|---|---|---|
| RS-01 | Fuerza bruta contra el inicio de sesión del portal de clientes | 2 | 2 | 🟡 4 | Reducir: M11 (contraseñas fuertes con hash lento) | **Limitar los intentos** (en Traefik o en el portal) antes de abrir el portal a Internet |
| RS-02 | Un fallo en el portal o en una app de k3s permite entrar en ese servidor | 2 | 2 | 🟡 4 | Reducir: M2 (el atacante queda dentro de la DMZ), M13 | — (M15 desde el 2026-10-22) |
| RS-03 | Desde un servidor de la DMZ ya comprometido, saltar a la red interna | 1 | 3 | 🟡 3 | Reducir: M1, M2. La extranet solo llega a su propia base de datos y PostgreSQL solo acepta cada usuario desde su IP (`pg_hba`) | — |
| RS-04 | Denegación de servicio (DoS) contra la conexión de la sede | 1 | 2 | 🟢 2 | Aceptar: no podemos parar un ataque grande con una sola línea. La entrada de la VPN puede pasar por el VPS del cloud | — |

### 4.2 Accesos y credenciales

| # | Riesgo | P | I | Nivel | Tratamiento y medidas | Pendiente |
|---|---|---|---|---|---|---|
| RS-05 | Contraseñas débiles o de laboratorio que llegan a producción | 1 | 3 | 🟡 3 | Reducir: todas las contraseñas son aleatorias y van en el Vault (M5). La única de laboratorio (usuario web de OPNsense, 4 caracteres) se cambió el 2026-10-22 por una aleatoria de 20, y Ansible ya no deja volver a poner una corta (M16) | — |
| RS-06 | Robo o pérdida del portátil de un teletrabajador (con su clave de VPN) | 2 | 2 | 🟡 4 | Reducir: M3 (cada clave es personal y no llega a la administración). Se revoca quitando su clave de la lista y aplicando `sede.yml` (contingencia, E10; OPNsense borra su peer) | — |
| RS-07 | Robo de las credenciales de un administrador (su equipo o su clave SSH) | 1 | 3 | 🟡 3 | Reducir: M10, M14 | **Segundo factor (TOTP)** en Proxmox y OPNsense. Desactivar del todo el acceso SSH con contraseña (hoy solo está bloqueado para root) |
| RS-08 | Fuga de secretos por el repositorio (Gitea o espejo de GitHub) | 1 | 3 | 🟡 3 | Reducir: M5. El repositorio es privado y el token de GitHub solo puede escribir en ese repositorio | — |

### 4.3 Software y configuración

| # | Riesgo | P | I | Nivel | Tratamiento y medidas | Pendiente |
|---|---|---|---|---|---|---|
| RS-09 | Vulnerabilidades sin parchear en los sistemas o en las apps | 1 | 3 | 🟡 3 | Reducir: parches de seguridad automáticos y vigilados (M15; primera pasada el 2026-10-22 en las 10 máquinas, sin fallos). Las apps con versión fijada se actualizan con Ansible (M4) | Revisar una vez al mes Proxmox, OPNsense y las versiones de Gitea, Grafana, Nextcloud, Wiki.js, Traefik y k3s |
| RS-10 | Un error humano de configuración rompe un servicio o abre un agujero | 2 | 2 | 🟡 4 | Reducir: M4 (todo pasa por Git, se simula con `--check` y se puede volver atrás), scripts de prueba (`scripts/probar-*.sh`) | — |
| RS-11 | Un certificado caduca y los servicios HTTPS dejan de funcionar | 1 | 2 | 🟢 2 | Reducir: M9 y alerta `CertificadoCaducaPronto` (M8) | — |
| RS-12 | Una app de DAM/DAW maliciosa o con errores afecta a las demás o se come los recursos | 2 | 1 | 🟢 2 | Reducir: M13 (cuota, aislamiento de red y sin root), M2 | — |

### 4.4 Disponibilidad y datos

| # | Riesgo | P | I | Nivel | Tratamiento y medidas | Pendiente |
|---|---|---|---|---|---|---|
| RS-13 | Ransomware o borrado malicioso de los datos | 1 | 3 | 🟡 3 | Reducir: M6 (copia fuera de la sede, cifrada y que no se puede borrar desde la sede) | — |
| RS-14 | Avería del servidor físico o de su disco (Proxmox es un único equipo) | 2 | 3 | 🔴 6 | Reducir: M7 (todo se rehace en minutos en otro equipo con Proxmox) y M6. Aceptar el resto: un segundo servidor no se justifica para una empresa de este tamaño | Que la copia local (vzdump) no esté solo en el mismo disco: **disco USB o NAS**. El simulacro (2026-10-22, `docs/simulacro.md`) ya prueba que las copias se pueden recuperar; falta repetirlo desde ese disco |
| RS-15 | Corte de luz. **La centralita no tiene SAI**: se apaga de golpe | 2 | 2 | 🟡 4 | Aceptar el corte (no hay SAI) y reducir el daño: (1) **vuelve sola y en orden**: Proxmox enciende OPNsense, espera 45 s, luego DNS/DHCP, PostgreSQL y el resto (`arranque`/`espera` en el inventario); (2) **los servicios reintentan** si la base de datos aún no está (Gitea, Wiki.js, extranet, Grafana, node_exporter: `Restart=always`); (3) **nada se corrompe sin remedio**: ext4 con diario, PostgreSQL con su registro (WAL) y copias diarias (M6); (4) **avisa el VPS del cloud**, que está fuera: si la sede no responde 3 minutos llega un aviso al móvil (ntfy) y otro cuando vuelve | **BIOS de la centralita: encender al volver la corriente** (si no, se queda apagada). El corte simulado ya está hecho en el laboratorio (2026-10-22, `docs/simulacro.md`) |
| RS-16 | Cae OPNsense y la sede se queda sin red | 1 | 3 | 🟡 3 | Reducir: su configuración está en Git y se rehace en menos de 2 minutos (M4, M7) | — |
| RS-17 | Se pierde la contraseña del Vault: los secretos quedan inaccesibles | 1 | 3 | 🟡 3 | Reducir: guardada también en el gestor de contraseñas del administrador (comprobada byte a byte el 2026-10-22) | — |
| RS-18 | Algo falla y nadie se entera a tiempo | 2 | 2 | 🟡 4 | Reducir: M8. Lo gordo (sede caída, portal caído, sin latido, sin copias) ya avisa al móvil desde el cloud | **Avisos de las alertas de Prometheus** (disco, memoria, un servicio interno caído): hoy solo se ven en Grafana |
| RS-19 | Un servicio externo deja de estar disponible (VPS del cloud, GitHub) | 2 | 1 | 🟢 2 | Aceptar: la sede funciona sin ellos. Gitea es el repositorio principal; GitHub solo es una copia | — |

### 4.5 Red física y personas

| # | Riesgo | P | I | Nivel | Tratamiento y medidas | Pendiente |
|---|---|---|---|---|---|---|
| RS-20 | Alguien enchufa un equipo propio o un switch a un puerto de la oficina | 2 | 2 | 🟡 4 | Reducir: M12 (el puerto se apaga si detecta un switch) y M1 (un puesto solo llega a lo que llegan los empleados) | — |
| RS-21 | Un invitado de la WiFi intenta llegar a la red interna | 2 | 2 | 🟡 4 | Reducir: la VLAN 50 de invitados solo sale a Internet (M1) | — |
| RS-22 | Una caja de cliente es manipulada (está en casa del cliente) | 2 | 2 | 🟡 4 | Reducir: M3 (desde la VPN, las cajas no llegan a nada de la sede), cortafuegos propio en la caja. Se da de baja quitando su clave pública del inventario (contingencia, E11; Ansible la quita también del portal; probado 2026-10-22) | — |
| RS-23 | Fuga de datos personales de clientes (RGPD) | 1 | 3 | 🟡 3 | Reducir: M2, M11, M6. Solo se guardan los datos necesarios (nombre, usuario y correo) | Escribir el registro de tratamiento y cuánto tiempo se guardan los datos |

## 5. Plan de acción

Lo pendiente, en orden. Las tareas técnicas se hacen como el resto: un rol o una variable en el repositorio.

| Prioridad | Acción | Riesgos | Cuándo |
|---|---|---|---|
| 1 | ~~Cambiar las contraseñas de laboratorio por otras aleatorias del Vault~~ (hecho 2026-10-22, M16) | RS-05 | Hecho |
| 2 | Avisos de las alertas de Prometheus por ntfy (Alertmanager); los del cloud ya funcionan | RS-18 | Fase 5 |
| 3 | ~~Actualizaciones automáticas de seguridad en todos los servidores~~ (hecho 2026-10-22, M15) | RS-09, RS-02 | Hecho |
| 4 | Límite de intentos en el inicio de sesión del portal | RS-01 | Antes de publicar el portal en Internet |
| 5 | Segundo factor (TOTP) en Proxmox y OPNsense y SSH sin contraseña en todos los servidores | RS-07 | Fase 5 |
| 6 | Copia vzdump en un disco USB o NAS, además del disco del servidor | RS-14 | Al montar la centralita |
| 7 | BIOS de la centralita: encender al volver la corriente (~~prueba de corte simulado~~: hecha el 2026-10-22) | RS-15 | Al montar la centralita |
| 8 | ~~Contraseña del Vault en el gestor de contraseñas~~ (hecho 2026-10-22) | RS-17 | Hecho |
| 9 | ~~Procedimientos de baja en el plan de contingencia, automatizados y probados~~ (E10, E11; hecho 2026-10-22) | RS-06, RS-22 | Hecho |
| 10 | Registro de tratamiento de datos (RGPD) | RS-23 | Fase 5 |

Con las acciones 1 y 3 hechas (2026-10-22), solo queda un riesgo en 🔴 alto: RS-14 (servidor único con la copia vzdump en el mismo disco), que se resuelve con la acción 6 al montar la centralita, porque necesita un disco aparte.

## 6. Revisión

- Este plan se revisa **cada 6 meses** y **cada vez que se añade un servicio** o hay un incidente.
- En cada revisión: actualizar las notas, quitar lo que ya está hecho del plan de acción y añadir los riesgos nuevos.
- Los cambios de este documento quedan en el historial de Git, igual que los de la infraestructura.
