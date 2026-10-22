# Simulacro de restauración

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
