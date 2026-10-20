# Rol gitea

Monta **Gitea** (el GitHub propio de la sede) en el contenedor `gitea` (CT 220, 10.10.20.10).

| Qué | Dónde |
|---|---|
| Web | `http://10.10.20.10:3000` (desde la red de gestión o por Tailscale) |
| Git por SSH | `ssh://git@10.10.20.10:2222/nosub/<repo>.git` |
| Administrador | `yassin` (contraseña: `ansible-vault view inventories/sede/group_vars/all/vault.yml` → `vault_gitea.admin_clave`) |
| Datos | `/var/lib/gitea` (repositorios en `repositorios/`). Base de datos: PostgreSQL en `bbdd` (10.10.20.12, base `gitea`) |
| Configuración | `/etc/gitea/app.ini` (la genera Ansible; lleva secretos del Vault) |

**Qué hace:**
- Descarga el programa oficial (comprobando su sha256) y lo ejecuta con el usuario `git`, no como root.
- Usa su propio servidor SSH en el puerto 2222; el 22 sigue siendo el SSH del sistema (Ansible).
- Registro cerrado y nada visible sin iniciar sesión.
- Crea el administrador, la organización `nosub`, sus repositorios (privados) y añade la clave SSH del nodo de control.
- Copia `nosub-infra` en GitHub (`YassinKamal345/nosub-infra`, privado): cada push a Gitea se sube solo, y además cada 8 h (`gitea_espejos`).

**Cambiar de versión:** poner `gitea_version` y su `gitea_sha256` (de `https://dl.gitea.com/gitea/<versión>/`) y lanzar `sede.yml`.

**Base de datos:** PostgreSQL (`gitea_bd: postgres`) desde el 2026-10-20. Antes era SQLite; el fichero antiguo `data/gitea.db` se conserva como copia. Así se hizo el cambio: instantánea `antes_postgres` del CT 220 → parar Gitea → `gitea dump --database postgres` → cargar `gitea-db.sql` en la base `gitea` con `SET ROLE gitea` y en una sola transacción → lanzar el rol.

**Contraseña del administrador:** el rol la pone al crearlo; si se cambia en la web, Ansible no la vuelve a tocar.

**Subir el repositorio desde Proxmox:**
`git remote add gitea ssh://git@10.10.20.10:2222/nosub/nosub-infra.git && git push -u gitea main`
(la clave es `/root/.ssh/nosub_ansible`, configurada en `core.sshCommand` del repositorio).

**Copia en GitHub:** usa un token de GitHub con permiso solo de escritura de contenido en `nosub-infra`, guardado en `vault_gitea.github_token`. Si caduca, se crea otro igual, se cambia en el Vault y se borra el espejo en Gitea (repositorio → Ajustes → Espejos) para que `sede.yml` lo vuelva a crear.
