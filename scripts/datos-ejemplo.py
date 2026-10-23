#!/usr/bin/python3
"""Rellena la intranet con contenido de ejemplo de NoSub (para pruebas y la demostración).

  scripts/datos-ejemplo.py            # crea lo que falte (se puede repetir: no duplica nada)

Wiki.js: páginas de la empresa (procedimientos, IT, RRHH). Nextcloud (usuario administrador): carpetas con
documentos de ejemplo y los diagramas de docs/diagramas. Todo es inventado: no hay datos de personas reales.
Las contraseñas se leen del Vault con Ansible y no se muestran.
"""
import base64, json, os, subprocess, sys, urllib.error, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IP_INTRANET = "10.10.20.14"
WIKI = f"http://{IP_INTRANET}:3000/graphql"
NUBE = f"http://{IP_INTRANET}/remote.php/dav/files"
NUBE_HOST = "nube.nosub.lan"


def vault(var):
    """Lee una variable del Vault (p. ej. "vault_intranet.wiki_admin_clave") sin mostrarla."""
    r = subprocess.run(["ansible-vault", "view", "inventories/sede/group_vars/all/vault.yml"], cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("No puedo abrir el Vault")
    import yaml
    valor = yaml.safe_load(r.stdout)
    for parte in var.split("."):
        valor = valor[parte]
    return valor


def peticion(url, datos=None, cabeceras=None, metodo=None):
    pet = urllib.request.Request(url, data=datos, headers=cabeceras or {}, method=metodo)
    try:
        with urllib.request.urlopen(pet, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


# ---------------------------------------------------------------- Wiki.js
PAGINAS = {
    "home": ("Intranet de NoSub", "Punto de entrada a la documentación interna", """
# Bienvenido a la intranet de NoSub

NoSub vende una **caja para casa** (un mini PC) que sustituye suscripciones: música, documentos, bloqueo de anuncios… sin pagar cada mes.

## Secciones
- **Empresa**: [Quiénes somos](/empresa/quienes-somos) · [Catálogo de la caja](/empresa/catalogo)
- **Procedimientos**: [Alta de un cliente](/procedimientos/alta-cliente) · [Baja de un cliente](/procedimientos/baja-cliente) · [Atender una incidencia](/procedimientos/incidencias)
- **Sistemas**: [Servicios internos](/sistemas/servicios) · [Red de la sede](/sistemas/red) · [Teletrabajo por VPN](/sistemas/teletrabajo) · [Contraseñas](/sistemas/contrasenas)
- **RRHH**: [Primer día](/rrhh/primer-dia) · [Vacaciones y ausencias](/rrhh/vacaciones)

> ¿Falta algo? Edita la página o avisa a sistemas.
"""),
    "empresa/quienes-somos": ("Quiénes somos", "Misión y equipo de NoSub", """
# Quiénes somos

**Misión:** que cualquier casa pueda tener sus propios servicios digitales sin depender de suscripciones.

| Área | Qué hace |
|---|---|
| Sistemas | Sede, red, seguridad y monitorización |
| Producto | La caja: apps, actualizaciones y soporte |
| Comercial | Clientes, pedidos y facturación |

**Valores:** privacidad (los datos del cliente se quedan en su casa), transparencia y software libre.
"""),
    "empresa/catalogo": ("Catálogo de la caja", "Qué lleva la caja y qué apps se pueden añadir", """
# Catálogo de la caja

## Incluido en todas las cajas
- **Bloqueo de anuncios** para toda la casa (AdGuard Home).
- **Página de inicio** con todas las apps.
- **Soporte remoto** por túnel cifrado (WireGuard).

## Apps opcionales
| App | Sustituye a | Notas |
|---|---|---|
| Música (Navidrome) | Spotify | Con la música del propio cliente |
| PDF (Stirling PDF) | Adobe Acrobat | Unir, firmar y convertir PDFs |

Próximamente: fotos (Immich), películas (Jellyfin) y contraseñas (Vaultwarden).
"""),
    "procedimientos/alta-cliente": ("Alta de un cliente", "Pasos para preparar y entregar una caja", """
# Alta de un cliente

1. Comercial crea el pedido y da al cliente su usuario del **portal de clientes**.
2. Sistemas añade la caja al inventario (`inventories/cajas/hosts.yml`) con sus apps.
3. Se enchufa el mini PC en el **laboratorio de cajas** (VLAN 60) y se lanza:
   ```bash
   ansible-playbook playbooks/caja_nueva.yml -e caja=<nombre>
   ansible-playbook playbooks/caja_entregar.yml -e caja=<nombre>
   ```
4. Se entrega la caja: el cliente la enchufa a su router y pone su IP como DNS.
5. Comprobar en Grafana (fila *Clientes y cajas*) que el túnel está **conectado**.
"""),
    "procedimientos/baja-cliente": ("Baja de un cliente", "Cómo dar de baja una caja o un cliente", """
# Baja de un cliente

1. Quitar la caja (o el cliente) del inventario.
2. Lanzar `ansible-playbook playbooks/sede.yml`: el túnel se borra del firewall y el cliente desaparece del portal.
3. Recoger la caja y **borrar su disco** antes de reutilizarla.
4. Anotar la baja en la hoja de clientes (Nextcloud → Comercial).
"""),
    "procedimientos/incidencias": ("Atender una incidencia", "Qué hacer cuando un cliente abre una incidencia", """
# Atender una incidencia

Los clientes abren incidencias desde el **portal de clientes**.

| Estado | Significa |
|---|---|
| abierta | Nadie la ha mirado todavía |
| en curso | Alguien de soporte la está resolviendo |
| cerrada | Resuelta y comunicada al cliente |

**Pasos:** mirar en Grafana si su caja está conectada → entrar por la VPN si hace falta → resolver → cerrar la incidencia con una nota.
**Tiempo objetivo de respuesta:** 1 día laborable.
"""),
    "sistemas/servicios": ("Servicios internos", "Dónde está cada servicio de la sede", """
# Servicios internos

| Servicio | Dirección | Para qué |
|---|---|---|
| Wiki | http://wiki.nosub.lan:3000 | Esta documentación |
| Nextcloud | http://nube.nosub.lan | Archivos, calendario y contactos |
| Gitea | http://gitea.nosub.lan:3000 | Código de la infraestructura (nosub-infra) |
| Grafana | http://monitor.nosub.lan:3000 | Estado de la sede y de las cajas |
| Portal de clientes | https://portal.nosub.lan | Lo que ven los clientes |

Los avisos de caídas llegan al móvil de guardia (ntfy).
"""),
    "sistemas/red": ("Red de la sede", "Resumen de las VLANs y quién puede hablar con quién", """
# Red de la sede

| VLAN | Red | Uso | Puede ir a |
|---|---|---|---|
| 10 | 10.10.10.0/24 | Gestión | Todo |
| 20 | 10.10.20.0/24 | Servidores | Todo menos gestión |
| 30 | 10.10.30.0/24 | DMZ | Solo Internet |
| 40 | 10.10.40.0/24 | Empleados | Servidores, DMZ e Internet |
| 50 | 10.10.50.0/24 | Invitados (WiFi) | Solo Internet |
| 60 | 10.10.60.0/24 | Laboratorio de cajas | Servidores e Internet |

WiFi: **NoSub-Empleados** (VLAN 40) y **NoSub-Invitados** (VLAN 50). La contraseña de invitados está en recepción.
"""),
    "sistemas/teletrabajo": ("Teletrabajo por VPN", "Cómo conectarse a la sede desde casa", """
# Teletrabajo por VPN

1. Instala **WireGuard** (Windows, macOS, Linux o móvil).
2. Sistemas te da tu fichero de configuración (`.conf`); impórtalo en WireGuard.
3. Activa el túnel: ya puedes abrir la wiki, Nextcloud y el resto de servicios.

- Con la VPN llegas a los **servidores** y a la **DMZ**, igual que desde la oficina.
- Si pierdes el portátil, **avisa enseguida**: se revoca tu clave y ya no sirve.
"""),
    "sistemas/contrasenas": ("Política de contraseñas", "Normas básicas de seguridad", """
# Política de contraseñas

- Mínimo **12 caracteres**; mejor una frase.
- Una contraseña distinta para cada servicio: usa un **gestor de contraseñas**.
- Activa el **doble factor** donde se pueda (el firewall ya lo exige).
- Nunca compartas contraseñas por chat o correo.
- Si crees que una contraseña se ha filtrado, cámbiala y avisa a sistemas.
"""),
    "rrhh/primer-dia": ("Primer día", "Lista para las personas que se incorporan", """
# Tu primer día

- [ ] Recoger el portátil y conectarte a la WiFi **NoSub-Empleados**.
- [ ] Entrar en Nextcloud y en esta wiki con tu usuario.
- [ ] Configurar la **VPN** para teletrabajar.
- [ ] Leer la [política de contraseñas](/sistemas/contrasenas).
- [ ] Conocer el [catálogo de la caja](/empresa/catalogo).
"""),
    "rrhh/vacaciones": ("Vacaciones y ausencias", "Cómo pedir días libres", """
# Vacaciones y ausencias

- **22 días laborables** al año.
- Pídelas con al menos **2 semanas** de antelación en el calendario compartido de Nextcloud (*Vacaciones*).
- Siempre tiene que quedar **una persona de guardia** de sistemas.
"""),
}


def wiki():
    correo = "yassin@nosub.lan"           # wiki_admin_correo (roles/intranet)
    clave = vault("vault_intranet.wiki_admin_clave")
    q = {"query": "mutation($u:String!,$p:String!){authentication{login(username:$u,password:$p,strategy:\"local\"){responseResult{succeeded message} jwt}}}",
         "variables": {"u": correo, "p": clave}}
    _, r = peticion(WIKI, json.dumps(q).encode(), {"Content-Type": "application/json"})
    login = json.loads(r)["data"]["authentication"]["login"]
    if not login["responseResult"]["succeeded"]:
        sys.exit("Wiki.js: no se pudo entrar: " + login["responseResult"]["message"])
    cab = {"Content-Type": "application/json", "Authorization": "Bearer " + login["jwt"]}

    def gql(query, variables=None):
        _, r = peticion(WIKI, json.dumps({"query": query, "variables": variables or {}}).encode(), cab)
        return json.loads(r)

    locale = gql("{localization{config{locale}}}")["data"]["localization"]["config"]["locale"]
    existentes = {p["path"] for p in gql("{pages{list{path}}}")["data"]["pages"]["list"]}
    creadas = 0
    for ruta, (titulo, desc, texto) in PAGINAS.items():
        if ruta in existentes:
            continue
        r = gql("mutation($c:String!,$d:String!,$p:String!,$t:String!,$l:String!,$tags:[String]!){pages{create(content:$c,description:$d,editor:\"markdown\","
                "isPublished:true,isPrivate:false,locale:$l,path:$p,tags:$tags,title:$t){responseResult{succeeded message}}}}",
                {"c": texto.strip() + "\n", "d": desc, "p": ruta, "t": titulo, "l": locale, "tags": [ruta.split("/")[0]] if "/" in ruta else ["inicio"]})
        res = r["data"]["pages"]["create"]["responseResult"]
        if not res["succeeded"]:
            sys.exit(f"Wiki.js: {ruta}: {res['message']}")
        creadas += 1
    print(f"Wiki.js: {creadas} páginas creadas, {len(PAGINAS) - creadas} ya estaban (idioma {locale})")


# ---------------------------------------------------------------- Nextcloud
TEXTOS = {
    "Comercial/Tarifas 2026.csv": "Producto;Pago único (€);Cuota mensual (€)\nCaja básica (bloqueo de anuncios + inicio);149;0\nApp Música;0;0\nApp PDF;0;0\nSoporte ampliado (opcional);0;4\n",
    "Comercial/Clientes de prueba.csv": "Usuario;Nombre;Caja;Apps;Alta\ncliente-a;Familia García (ficticio);caja-garcia;Música;2026-10-21\ncliente-b;Oficina Ruiz (ficticio);caja-ruiz;PDF;2026-10-21\n",
    "Comercial/Argumentario de venta.md": "# Argumentario de venta\n\n- **Ahorro:** una caja se paga sola en menos de un año frente a varias suscripciones.\n- **Privacidad:** los datos se quedan en casa del cliente.\n- **Sin anuncios** en toda la casa, también en la tele y el móvil.\n",
    "Técnico/Checklist antes de entregar una caja.md": "# Checklist antes de entregar una caja\n\n- [ ] caja_nueva.yml terminado sin errores\n- [ ] Túnel conectado en Grafana\n- [ ] Apps abren desde la página de inicio\n- [ ] caja_entregar.yml lanzado\n- [ ] Etiqueta con el nombre de la caja pegada\n",
    "RRHH/Calendario de guardias.csv": "Semana;Guardia de sistemas\n2026-W44;Persona 1\n2026-W45;Persona 2\n2026-W46;Persona 3\n",
    "RRHH/Plantilla de solicitud de vacaciones.md": "# Solicitud de vacaciones\n\n- Nombre:\n- Días solicitados (desde / hasta):\n- Persona que cubre la guardia:\n- Visto bueno del responsable:\n",
    "Plantillas/Acta de reunión.md": "# Acta de reunión\n\n- Fecha:\n- Asistentes:\n\n## Temas\n1.\n\n## Acuerdos y tareas\n| Tarea | Responsable | Fecha |\n|---|---|---|\n|  |  |  |\n",
    "Léeme.md": "# Archivos de NoSub\n\nCarpetas compartidas de la empresa: Comercial, Técnico, RRHH y Plantillas.\nLos diagramas de la red están en Técnico/Diagramas.\n",
}


def nextcloud():
    usuario = "yassin"
    clave = vault("vault_intranet.nube_admin_clave")
    aut = "Basic " + base64.b64encode(f"{usuario}:{clave}".encode()).decode()
    base = f"{NUBE}/{usuario}"
    cab = {"Authorization": aut, "Host": NUBE_HOST}

    def url(ruta):
        return base + "/" + urllib.request.quote(ruta)

    def existe(ruta):
        return peticion(url(ruta), cabeceras={**cab, "Depth": "0"}, metodo="PROPFIND")[0] == 207

    def carpeta(ruta):
        if not existe(ruta):
            codigo, r = peticion(url(ruta), cabeceras=cab, metodo="MKCOL")
            if codigo not in (201, 405):
                sys.exit(f"Nextcloud: no se pudo crear {ruta}: {codigo} {r[:200]}")

    subidos = 0

    def subir(ruta, datos):
        nonlocal subidos
        if existe(ruta):
            return
        codigo, r = peticion(url(ruta), datos, cab, "PUT")
        if codigo not in (201, 204):
            sys.exit(f"Nextcloud: no se pudo subir {ruta}: {codigo} {r[:200]}")
        subidos += 1

    for c in ["Comercial", "Técnico", "Técnico/Diagramas", "RRHH", "Plantillas"]:
        carpeta(c)
    for ruta, texto in TEXTOS.items():
        subir(ruta, texto.encode())
    diag = os.path.join(REPO, "docs", "diagramas")
    for f in sorted(os.listdir(diag)):
        if f.endswith((".png", ".drawio")):
            subir(f"Técnico/Diagramas/{f}", open(os.path.join(diag, f), "rb").read())
    for f in ["red.md", "riesgos.md", "contingencia.md"]:
        subir(f"Técnico/{f}", open(os.path.join(REPO, "docs", f), "rb").read())
    print(f"Nextcloud: {subidos} archivos subidos (los que ya estaban no se tocan)")


if __name__ == "__main__":
    wiki()
    nextcloud()
