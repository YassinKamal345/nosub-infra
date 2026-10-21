# Rol copias_externas

Cada noche (04:15, después de la copia de PostgreSQL) **restic** manda al VPS del cloud las carpetas de
`copias_rutas` de cada máquina del grupo `copias_externas` (Gitea, bbdd e intranet). Viajan por el enlace con la
sede y llegan a rest-server (rol `cloud`).

- **Cifradas** con la clave `vault_copias.clave` del Vault. Sin esa clave no se pueden leer ni recuperar:
  guarda también la contraseña del Vault fuera de prx.
- **Solo añadir:** desde la sede se pueden hacer copias, pero no borrarlas (rest-server `--append-only`).
  Un intruso o un ransomware en la sede no puede destruirlas.
- **Aviso:** cada copia avisa a la página de estado. Solo cuenta como buena si restic funciona, termina sin error y
  aparece una copia de hace menos de una hora. Si en 26 horas no llega ningún aviso bueno, sale en rojo.

**Recuperar** (en la máquina, como root):
```bash
. /etc/restic/entorno
restic snapshots                                  # qué copias hay
restic restore latest --target /tmp/recuperado    # la última, en una carpeta aparte
```

**Pendiente:** borrar copias antiguas. Desde la sede no se puede (es la protección); se hará desde el VPS.
