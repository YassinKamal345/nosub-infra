# Rol k3s

Monta **k3s** (Kubernetes ligero) en la VM `k3s` (VM 231, 10.10.30.20, **DMZ**, Ubuntu Server 24.04).
Es el hosting de los proyectos DAM/DAW: cada proyecto es un contenedor que se publica en su propia web.

| Qué | Dónde |
|---|---|
| Proyectos | `https://<proyecto>.apps.nosub.lan` (por ejemplo, `https://demo.apps.nosub.lan`) |
| Configuración de k3s | `/etc/rancher/k3s/config.yaml` |
| Un fichero por proyecto | `/var/lib/rancher/k3s/server/manifests/` (k3s los aplica solo) |
| Acceso con `kubectl` | En la VM: `k3s kubectl get pods -A`. Desde fuera: kubeconfig en `/root/.kube/nosub-k3s.yaml` del nodo de control |
| API de Kubernetes | `https://10.10.30.20:6443` (la vigila la monitorización) |

**La VM** la crea el rol `proxmox_vms` (lista `maquinas_virtuales` del inventario) a partir de la imagen
"cloud" oficial de Ubuntu, comprobada con su sha256, y la configura con cloud-init: IP fija, clave SSH de
Ansible y el agente de QEMU. Es una VM y no un contenedor porque Kubernetes necesita su propio núcleo.

**Camino de una visita:** navegador → Traefik de la DMZ (`extranet`, HTTPS con certificado de NoSub CA) →
Traefik de k3s (HTTP, puerto 80 de la VM) → el proyecto que corresponde al nombre. El DNS apunta
`*.apps.nosub.lan` a `extranet`, así que siempre se entra por el Traefik de la DMZ.

**Cada proyecto tiene:**
- Su espacio propio (namespace `proyecto-<nombre>`).
- Una cuota: por defecto 1 CPU, 1 GiB de RAM y 10 contenedores (`k3s_cuota_defecto`). Así un proyecto no puede quedarse con toda la máquina.
- Aislamiento: solo recibe tráfico del Traefik de k3s, nunca de otros proyectos.

**Seguridad:** k3s guarda los Secrets cifrados en el disco; el kubeconfig solo lo lee root (0600); el
Traefik de k3s solo se fía de las cabeceras `X-Forwarded-*` del Traefik de la DMZ.

**Añadir un proyecto:** añadirlo a `k3s_proyectos` (nombre, imagen, puerto y, si hace falta, réplicas y
cuota) y lanzar `sede.yml`. La web `https://<nombre>.apps.nosub.lan` funciona sin tocar nada más: el DNS y
el certificado ya cubren todos los nombres `*.apps.nosub.lan`.

**Cambiar de versión:** poner `k3s_version` y `k3s_instalador_sha256` (sha256 del `install.sh` de esa
versión en GitHub) y lanzar `sede.yml`.
