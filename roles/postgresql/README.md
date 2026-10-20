# Rol postgresql

**Base de datos de la sede** (PostgreSQL 16 de Rocky Linux 10) en el contenedor `bbdd` (CT 222, 10.10.20.12).

- Una base por aplicación, cada una con su propio usuario y contraseña (`scram-sha-256`). La lista está en `postgresql_bases` (`group_vars/all/servicios_red.yml`) y las contraseñas en el Vault (`vault_postgresql.<usuario>`).
- `pg_hba.conf`: cada base solo admite conexiones desde las IPs de su aplicación (`desde`). Todo lo demás se rechaza.
- Se registra cada conexión y desconexión (quién, a qué base y desde dónde).
- **Copia diaria** a las 03:30 (`postgresql-copia.timer`): cada base con `pg_dump` más los usuarios, en `/var/lib/pgsql/copias`. Se guardan 7 días.

| Base | Usuario | Desde |
|---|---|---|
| gitea | gitea | 10.10.20.10 (Gitea) |

**Añadir una base:** una línea en `postgresql_bases`, su contraseña en el Vault y lanzar `sede.yml`.

**Restaurar una base:** `su - postgres -c "pg_restore -d <base> --clean /var/lib/pgsql/copias/<base>-<fecha>.dump"`.

**Comprobar:** `su - postgres -c "psql -c '\l'"` (bases) y `systemctl list-timers postgresql-copia.timer` (próxima copia).
