# Simulacros

Actas de los simulacros de la fase 5: restauración de copias (apartado A) y corte de luz (apartado B).

# A · Simulacro de restauración

Acta del simulacro de la fase 5.3. Comprueba que **las copias de seguridad sirven de verdad**: no basta con
que se hagan cada noche, hay que poder recuperar de ellas. Los pasos siguen el plan de contingencia
(`docs/contingencia.md`, escenarios E3 y E4).

## Cómo se hace

Con un script del repositorio que se puede repetir cuando se quiera:

```bash
scripts/simulacro-restauracion.sh      # en Proxmox, como root; tarda 1 minuto
```

Recupera datos reales, pero **siempre aparte**: en carpetas temporales, en bases de datos `simulacro_*` y
en un contenedor nuevo (CT 9221) desconectado de la red. No toca nada de lo que está en marcha, nadie
nota nada y al terminar lo borra todo.

| Parte | Copia que se prueba | Qué se recupera | Cómo se sabe que está bien |
|---|---|---|---|
| 1 | **restic** en el VPS del cloud | Ficheros de Gitea: repositorios y configuración | `restic check` sin errores; `app.ini` recuperado; `git fsck` del repositorio `nosub-infra` sin errores |
| 2 | **restic** en el cloud → copias de PostgreSQL | Las bases de Gitea y del portal de clientes, cargadas en bases nuevas | Mismo número de filas que las bases en marcha (repositorios, correos, espejo, clientes, cajas) |
| 3 | **vzdump** local | El contenedor `red-int` entero (DNS, DHCP y proxy) | Arranca; Bind9 en marcha y responde (`gitea.nosub.lan` → 10.10.20.10); configuración de Kea y Squid válida |

## Resultado (2026-10-22)

**14 de 14 comprobaciones bien.** Copias usadas: restic de las 04:16-04:27 y vzdump de las 03:02 del mismo día.

| Parte | Resultado | Tiempo |
|---|---|---|
| 1 · Ficheros de Gitea desde el cloud | ✓ 3/3 | 9 s |
| 2 · Bases de datos desde el cloud | ✓ 5/5 | 21 s |
| 3 · Contenedor entero desde vzdump | ✓ 6/6 | 18 s hasta funcionar |

Los tiempos están muy por debajo de los objetivos de recuperación (RTO) del plan de contingencia
(1-4 horas). Esos objetivos dejan margen para lo que el script no hace: darse cuenta del problema,
decidir qué copia usar y comprobar a mano.

## Lo que hemos aprendido

1. **El RPO se ve con un ejemplo real.** La copia de Gitea tiene el commit `cbacaa7` (21/10, 23:08). Los 4
   commits de hoy no están, porque se hicieron después de la copia de las 04:27: con solo esta copia se
   perderían. En el caso del repositorio no se pierden, porque **también están en el espejo de GitHub**,
   que se actualiza en cada cambio. Para el resto de datos (wiki, archivos, portal) se pierde lo hecho
   desde la última copia: hasta 24 horas.
2. **La primera vez falló, y no por las copias.** En la primera pasada salieron 7 comprobaciones mal.
   Todas eran fallos del procedimiento, no de las copias:
   - `git fsck` no acepta la opción `-q`;
   - el usuario `postgres` no podía abrir la carpeta temporal donde root había dejado las copias
     (solución: `pg_restore` lee la copia por la entrada estándar);
   - Kea no arranca sin su interfaz de red (solución: dejar la red, pero con el cable "desenchufado",
     `link_down=1`, para no chocar con el `red-int` de verdad).

   Por eso se hacen simulacros: si esto hubiera pasado durante una avería de verdad, habríamos perdido
   tiempo. Ahora el procedimiento ya está corregido en el script.
3. **Las copias restic no se pueden leer sin la clave del Vault.** La contraseña del Vault está en el gestor
   de contraseñas (riesgo RS-17), así que una avería de prx no las deja inservibles.

## Qué falta

- **Copia vzdump fuera del disco del servidor** (riesgo RS-14). Hoy vzdump está en el mismo disco que
  Proxmox: si se rompe el disco, solo quedan las copias de restic (datos, no máquinas enteras). En la
  centralita: disco USB o NAS, y repetir la parte 3 desde ese disco.
- **Nextcloud desde restic**: sus archivos también se copian, pero este simulacro no los recupera. Se puede
  añadir como parte 4.
- **Repetirlo**: una vez al año como mínimo, después de cada cambio en las copias y antes de pasar a la
  centralita.

# B · Simulacro de corte de luz

La centralita **no tiene SAI** (riesgo RS-15). Este simulacro comprueba que, si se va la luz, **nos enteramos**
y que, cuando vuelve, **la sede se levanta sola, en orden y sin perder datos** (plan de contingencia, E1).

## Cómo se hace

```bash
scripts/simulacro-corte-luz.sh      # en Proxmox, como root; unos 8-10 minutos
```

1. **Corte:** para de golpe (sin apagado ordenado, como un corte de verdad) todas las máquinas con la etiqueta
   `sede`: OPNsense, los 6 contenedores y k3s. No toca las cajas, el VPS del cloud ni otros servicios de Proxmox.
2. **Aviso:** espera a que la página de estado del cloud cuente 3 fallos seguidos, que es cuando avisa al móvil por
   ntfy. La luz sigue cortada 1 minuto más.
3. **Vuelve la luz:** arranca las máquinas como lo hace Proxmox al encenderse (`startall`), con el orden y las esperas
   del inventario, y apunta cuándo arranca cada una.
4. **Vuelta a la normalidad:** espera a que Prometheus (con datos de verdad, no recién arrancado) vea todo arriba y a
   que la página de estado dé el aviso de "resuelto". Mira cómo se recuperó PostgreSQL.
5. **Pruebas de la red:** `probar-red.sh` y `probar-vpn.sh`.

Que el aviso llega al móvil lo confirma una persona: el script solo ve que Gatus lo ha disparado.

**Límite del laboratorio:** en prx no se puede apagar Proxmox entero (tiene otros servicios), así que se cortan las
máquinas de la sede y Proxmox sigue encendido. En la centralita habrá que comprobar también la BIOS (*encender al
volver la corriente*) con un corte de verdad.

## Resultado (2026-10-22, tercer intento)

**11 de 11 comprobaciones bien.** Avisos al móvil confirmados: "Gatus: Sede/Conexión con la sede" y su "resuelto".

| Momento | Qué pasa |
|---|---|
| 0 s | Corte: las 8 máquinas apagadas en 5 s |
| 140 s | La página de estado lleva 3 fallos seguidos: **aviso al móvil** |
| +1 min | Vuelve la luz |
| 8 s | Arranca OPNsense; Proxmox espera 45 s |
| 54 s | Arranca red-int (DNS, DHCP y proxy); espera 10 s |
| 60 s | Arranca bbdd. PostgreSQL ve que no se apagó bien y **se recupera solo con su registro (WAL)** en milisegundos |
| 82-90 s | Arrancan el resto: extranet, gitea, monitor, intranet y, por último, k3s |
| 179 s | **Todo arriba** en Prometheus y aviso de **"resuelto"** al móvil |
| después | Red (aislamiento entre VLANs) y VPN bien; las dos cajas, bien; ningún servicio en fallo en ninguna máquina |

## Lo que hemos aprendido

1. **El simulacro encontró un fallo real.** En los dos primeros cortes, el `node_exporter` (métricas) de `intranet` y
   de `extranet` se quedó parado: arrancaba antes de que el contenedor tuviera su IP, lo reintentaba 5 veces en un
   segundo y systemd se rendía. Sin el simulacro lo habríamos descubierto en el primer corte de luz de verdad.
   **Arreglo:** reintentar cada 5 segundos sin rendirse (`Restart=always`, `RestartSec=5`), como ya hacían Gitea,
   Traefik, Wiki.js y la extranet. En el tercer corte, 4 contenedores tuvieron que reintentarlo una vez y todos se
   recuperaron solos.
2. **El script también tenía fallos.** En el primer intento confundió un error con el aviso y solo dejó la sede
   apagada 66 segundos, así que Gatus nunca llegó a avisar. En el segundo dio "todo arriba" cuando Prometheus
   llevaba 6 segundos encendido y lanzó la prueba de red con OPNsense aún asentándose. Corregido: ahora espera a
   los datos de verdad. **Lección:** una prueba que dice "bien" demasiado pronto es peor que no tener prueba.
3. **Hay dos sistemas de aviso, y no se pisan.** Los avisos de "VM o contenedor apagado" que también llegaron
   salen del vigilante propio de prx, por otro canal. El de la sede sale del cloud, que sigue en pie aunque la
   sede se quede sin luz.
4. **El orden de arranque funciona tal como está escrito en el inventario**, y los servicios que dependen de
   PostgreSQL esperan y reintentan.
