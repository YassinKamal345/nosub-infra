# Defensa del proyecto

Presentación (15 diapositivas con notas del ponente; se descarga en PDF o PowerPoint):
https://claude.ai/artifact/C77Kxh3fCDSYZckGf1y67g (privada: compartirla con el grupo desde su menú Compartir).

Guion para presentar NoSub: qué contar, en qué orden, la demostración en directo y las preguntas que es fácil que
hagan. Duración pensada: **20 minutos de presentación + 10 de preguntas**. Si el tiempo es otro, se recorta la parte 3.

## 1. Estructura

| # | Parte | Minutos | Idea que tiene que quedar |
|---|---|---|---|
| 1 | El problema y la empresa | 2 | Pagamos suscripciones por todo; NoSub vende una caja que se paga una vez y que alguien mantiene por ti |
| 2 | Arquitectura y red | 4 | Una sede con 6 VLANs, firewall con DMZ y VPN, y cajas en casa de los clientes unidas por WireGuard |
| 3 | Servicios de la sede | 3 | DNS, DHCP, base de datos, intranet, extranet, monitorización: todo lo que pide el enunciado, y conectado |
| 4 | El producto: la caja, el cloud y el hosting | 3 | La caja funciona sola en casa del cliente; el cloud vigila desde fuera; DAM/DAW publican sus apps en k3s |
| 5 | Automatización | 2 | Todo es Ansible y Git: la sede se rehace desde cero en 11 minutos |
| 6 | Seguridad y continuidad | 3 | Riesgos valorados, medidas montadas y **probadas** (simulacros de restauración y de corte de luz) |
| 7 | Demostración en directo | 5 | Ver que es real (apartado 2) |
| 8 | Conclusiones | 1 | Qué hemos aprendido y qué falta para producción |

### Mensajes clave (para repetir)

- **"Lo que no está en Git no existe."** No hay nada configurado a mano. Prueba: la reconstrucción desde cero.
- **"Lo hemos probado, no solo montado."** Cada pieza tiene su prueba (`scripts/probar-*.sh`) y hemos hecho
  simulacros que han encontrado fallos reales (Kea y node_exporter tras un corte de luz).
- **"Seguridad por capas."** VLANs + firewall + DMZ + VPN por persona + HTTPS + límite de intentos + segundo factor +
  parches automáticos + copias cifradas que no se pueden borrar desde la sede.
- **"Pensado para una empresa de verdad."** RGPD, plan de contingencia con tiempos, avisos al móvil y bajas de
  clientes y empleados automatizadas.

## 2. Demostración en directo

Preparación (antes de empezar): sede encendida, `scripts/probar-red.sh` pasado esa mañana, Grafana abierto en una
pestaña, el móvil con ntfy y la app TOTP a mano. Terminal en `/root/nosub-infra`.

| # | Qué se enseña | Cómo | Qué debe salir | Tiempo |
|---|---|---|---|---|
| 1 | Panel ADMIN | Grafana (`http://grafana.yk.internal`), panel "ADMIN · Sede NoSub" | Todos los equipos y servicios en verde | 30 s |
| 2 | Aislamiento de la red | `scripts/probar-red.sh` | Lista de ✓ y "Todo como se esperaba." (los invitados no llegan a los servidores, la DMZ no llega a la red interna…) | 45 s |
| 3 | La caja del cliente | `scripts/probar-cajas.sh caja-garcia` | Desde la casa, `doubleclick.net` → `0.0.0.0` (anuncio bloqueado); la caja no llega a la sede ni a otra caja | 45 s |
| 4 | Portal de clientes por HTTPS | `https://portal.nosub.lan`, entrar como `cliente-a` | Candado válido (NoSub CA); el cliente ve su caja y puede abrir una incidencia | 45 s |
| 5 | Ataque de fuerza bruta | Tres o cuatro contraseñas mal en el portal | Al 6.º intento: "Demasiados intentos"; Traefik corta al 11.º | 30 s |
| 6 | Aviso al móvil | `ansible red-int -m systemd -a "name=squid state=stopped"` y, al llegar el aviso, `state=started` | En unos 2,5 min llega "NoSub: ServicioCaido" al móvil; después, el de resuelto | (en paralelo) |
| 7 | Recuperar copias | `scripts/simulacro-restauracion.sh` | 14/14 en 1 minuto: ficheros y bases de datos desde el cloud y un contenedor entero desde vzdump | 1 min |
| 8 | Infraestructura como código | `ansible-playbook playbooks/sede.yml` | Todo en verde y `changed=0`: lo que hay es exactamente lo que dice Git | 1-2 min |

**Plan B:** si algo falla en directo, no se arregla delante del tribunal. Se enseña la salida guardada del mismo
script (actas en `docs/simulacro.md`, capturas en la presentación) y se explica qué tendría que salir.

**Lo que no se hace en directo:** el corte de luz y la reconstrucción desde cero (tardan demasiado). Se cuentan con
sus resultados: aviso al móvil a los 140 s y sede entera de vuelta en 3 min; reconstrucción en 11 min sin errores.

## 3. Preguntas probables

| Pregunta | Respuesta corta |
|---|---|
| ¿Por qué OPNsense y no iptables a mano? | Es un firewall completo (VLANs, reglas por interfaz, WireGuard, relay DHCP) con interfaz web, y lo configuramos igualmente desde Ansible: el script descarga su `config.xml`, aplica lo del repositorio y lo vuelve a subir |
| ¿Por qué contenedores LXC y no VMs? | El servidor tiene 16 GB de RAM. Un LXC gasta mucho menos que una VM y para servicios Linux da el mismo aislamiento práctico. Usamos VMs donde hace falta otro núcleo o kernel: OPNsense (FreeBSD), k3s y GNS3 |
| ¿Qué pasa si se rompe el servidor? | Plan de contingencia E5: se instala Proxmox en otro equipo, se baja el repositorio del espejo de GitHub, `sede.yml` rehace todo y los datos vuelven de las copias del cloud. Unas 2-3 horas. Es el único riesgo en rojo (falta un disco aparte para vzdump) |
| ¿Y si os roban el servidor o hay ransomware? | Las copias del cloud están cifradas y en modo "solo añadir": desde la sede se pueden crear pero no borrar (probado: 403) |
| ¿Cómo se da de baja a un cliente o a un empleado? | Se quita del inventario y se aplica `sede.yml`: OPNsense borra su túnel y el portal borra sus datos. Probado con una caja de prueba |
| ¿Cómo sabéis que las copias sirven? | Simulacro de restauración: se recuperan de verdad (ficheros, bases de datos y un contenedor entero) y se comparan con lo que está en marcha |
| ¿Por qué un VPS? ¿No basta con la sede? | Si la sede se queda sin luz, no puede avisar de ello. El VPS está fuera: avisa al móvil, guarda las copias lejos y sirve de entrada a la VPN sin abrir puertos en la sede |
| ¿Cómo se protege la extranet si está expuesta? | Está en la DMZ (solo llega a Internet y a su base de datos), detrás de Traefik con HTTPS, con contraseñas *scrypt*, CSRF, cookies seguras y límite de intentos en dos capas |
| ¿Por qué la caja no manda el tráfico del cliente a la sede? | Por privacidad (RGPD) y por diseño: el túnel solo sirve para el soporte. Si la sede cae, la caja sigue funcionando |
| ¿Qué es eso del segundo factor en OPNsense? | Para entrar en el firewall hace falta la contraseña y el código del móvil. Si alguien roba la contraseña, no entra |
| ¿Qué cambiaría para producción? | Dominio real con Let's Encrypt en vez de la CA propia, disco aparte para las copias, VPS en Oracle, contrato del art. 28 con los clientes y gestión de clientes desde una herramienta en vez de en Git |
| ¿Qué os ha costado más? | Ver `docs/plan.md` y las lecciones de los simulacros: los fallos que solo aparecen en situaciones reales (servicios que arrancan antes que la red, un servicio "activo" que no funciona) |

## 4. Antes del día

- [ ] Ensayar la demo entera con cronómetro, dos veces.
- [ ] Pasar `scripts/probar-red.sh`, `probar-dhcp.sh`, `probar-vpn.sh` y `probar-cajas.sh` esa mañana.
- [ ] Comprobar que llegan los avisos al móvil (ntfy) y que el TOTP funciona.
- [ ] Tener la presentación también en PDF, sin depender de la red del aula.
- [ ] Repartir las partes entre los tres miembros del grupo y preparar cada uno su parte individual.
