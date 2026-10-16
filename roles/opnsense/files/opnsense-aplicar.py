#!/usr/bin/python3
"""opnsense-aplicar: deja la configuración de OPNsense como dice el repositorio.

OPNsense guarda toda su configuración en un único config.xml. Este script:
  1. Entra en la web de OPNsense (como una persona: usuario y contraseña).
  2. Descarga el config.xml actual.
  3. Le aplica lo que dice la especificación (JSON generado por Ansible):
     sistema, WAN, VLANs, interfaces, puerta de enlace, alias y reglas.
     Lo que gestiona el repositorio se marca con uuid fijos; lo demás no se toca.
  4. Si el resultado es distinto, lo sube con "Restaurar". Después hay que reiniciar OPNsense\n     (lo hace Ansible con qm reboot): la restauración sola no activa las VLANs nuevas.

Uso:  opnsense-aplicar.py URL ESPEC.json [--simular]
Variables: OPN_CLAVE (para entrar ahora) y OPN_CLAVE_ROOT (la que debe tener root). Imprime CAMBIADO o SIN CAMBIOS en la última línea.
"""
import json, os, re, sys, time, uuid
import xml.etree.ElementTree as ET
import bcrypt, requests, urllib3

urllib3.disable_warnings()
NS = uuid.UUID("6b7f3c9e-2d4a-4f61-9a0e-6f1c2b3d4e5f")


def uid(*partes):
    return str(uuid.uuid5(NS, "/".join(partes)))


# ---------- web ----------
class Web:
    def __init__(self, url, usuario, clave):
        self.url, self.s = url, requests.Session()
        self.s.verify = False
        self.s.headers["Connection"] = "close"  # la web a veces manda cuerpo de más y rompe el keep-alive
        # la web a veces devuelve una página sin formulario (p. ej. mientras recarga servicios): reintentar
        for intento in range(6):
            try:
                k, v = self.csrf(self.s.get(url + "/", timeout=15).text)
                r = self.s.post(url + "/", data={"usernamefld": usuario, "passwordfld": clave, "login": "1", k: v}, timeout=15)
                if "usernamefld" not in r.text:
                    return
                error = "Login incorrecto en " + url
            except (SystemExit, requests.exceptions.RequestException) as e:
                error = str(e)
            time.sleep(3)
        raise SystemExit(error)

    @staticmethod
    def csrf(html):
        m = re.search(r'<input type="hidden" name="([^"]+)" value="([^"]+)"', html)
        if not m:
            raise SystemExit("No encuentro el token CSRF")
        return m.group(1), m.group(2)

    def token_backup(self):
        for intento in range(6):
            try:
                return self.csrf(self.s.get(self.url + "/diag_backup.php", timeout=15).text)
            except SystemExit:
                time.sleep(3)
        raise SystemExit("No encuentro el token CSRF en diag_backup.php")

    def bajar(self):
        k, v = self.token_backup()
        r = self.s.post(self.url + "/diag_backup.php", timeout=30,
                        data={"download": "Download configuration", "donotbackuprrd": "on", k: v})
        if not r.text.lstrip().startswith("<?xml"):
            raise SystemExit("La web no ha devuelto un config.xml")
        return r.text

    def subir(self, texto):
        k, v = self.token_backup()
        try:
            r = self.s.post(self.url + "/diag_backup.php", timeout=60,
                            data={"restore": "Restore configuration", "restorearea": "", k: v},
                            files={"conffile": ("config.xml", texto.encode(), "text/xml")})
        except requests.exceptions.ConnectionError:
            return  # se ha reiniciado antes de contestar: normal
        if r.status_code != 200 or "alert-danger" in r.text:
            m = re.search(r'alert-danger[^>]*>(.*?)</div>', r.text, re.S)
            raise SystemExit("Fallo al restaurar: " + (re.sub(r"<[^>]+>", " ", m.group(1)).strip() if m else str(r.status_code)))


# ---------- XML ----------
def hijo(padre, tag, texto=None):
    e = padre.find(tag)
    if e is None:
        e = ET.SubElement(padre, tag)
    if texto is not None:
        e.text = str(texto)
    return e


def quitar(padre, tag):
    for e in padre.findall(tag):
        padre.remove(e)


def rellenar(e, campos):
    for k, v in campos.items():
        hijo(e, k, "" if v is None else v)


REGLA_BASE = {
    "enabled": "1", "statetype": "keep", "action": "pass", "quick": "1", "interfacenot": "0",
    "direction": "in", "ipprotocol": "inet", "protocol": "any", "source_net": "any", "source_not": "0",
    "source_port": None, "destination_net": "any", "destination_not": "0", "destination_port": None,
    "disablereplyto": "0", "log": "0", "allowopts": "0", "nosync": "0", "nopfsync": "0", "tcpflags_any": "0",
}


def aplicar(raiz, esp):
    quitar(raiz, "trigger_initial_wizard")

    # sistema
    s = raiz.find("system")
    hijo(s, "hostname", esp["hostname"]); hijo(s, "domain", esp["dominio"])
    hijo(s, "timezone", esp["zona_horaria"]); hijo(s, "dnsallowoverride", "0")
    quitar(s, "dnsserver")
    for d in esp["dns"]:
        ET.SubElement(s, "dnsserver").text = d
    root = [u for u in s.findall("user") if u.findtext("name") == "root"][0]
    # la contraseña solo se cambia si no coincide (el hash lleva sal aleatoria: rehacerlo siempre no sería idempotente)
    clave = os.environ["OPN_CLAVE_ROOT"].encode()
    actual = (root.findtext("password") or "").replace("$2y$", "$2b$", 1).encode()
    try:
        vale = bcrypt.checkpw(clave, actual)
    except ValueError:
        vale = False
    if not vale:
        hijo(root, "password", bcrypt.hashpw(clave, bcrypt.gensalt(10)).decode().replace("$2b$", "$2y$", 1))
    hijo(root, "authorizedkeys", esp["root_clave_ssh_b64"])
    ssh = hijo(s, "ssh")
    rellenar(ssh, {"group": "admins", "enabled": "enabled", "permitrootlogin": "1", "interfaces": esp["ssh_interfaz"]})
    quitar(ssh, "passwordauth")

    # interfaces: WAN y VLANs
    ifs = raiz.find("interfaces")
    wan = ifs.find("wan")
    rellenar(wan, {"enable": "1", "if": esp["wan"]["if"], "ipaddr": esp["wan"]["ip"], "subnet": esp["wan"]["mascara"],
                   "gateway": esp["wan"]["gateway"], "blockpriv": "0", "blockbogons": "1", "descr": "WAN"})
    quitar(wan, "ipaddrv6")

    vlans = raiz.find("vlans")
    etiquetas = [str(x["tag"]) for x in esp["vlans"]]
    for v in list(vlans):
        if v.findtext("if") == esp["troncal"] and v.findtext("tag") in etiquetas:
            vlans.remove(v)
    for n, v in enumerate(esp["vlans"], 1):
        e = ET.SubElement(vlans, "vlan", uuid=uid("vlan", str(v["tag"])))
        rellenar(e, {"if": esp["troncal"], "tag": v["tag"], "pcp": "0", "proto": None,
                     "descr": v["nombre"].upper(), "vlanif": f"vlan0{n}"})
        clave = v["clave"]
        quitar(ifs, clave)
        i = ET.Element(clave)
        rellenar(i, {"enable": "1", "if": f"vlan0{n}", "descr": v["nombre"].upper(), "ipaddr": v["ip"],
                     "subnet": v["mascara"], "spoofmac": None})
        if clave == "lan":  # LAN es la primera de la lista: mantener su posición
            ifs.insert(1, i)
        else:
            ifs.append(i)

    # puerta de enlace
    opn = raiz.find("OPNsense")
    gws = hijo(opn, "Gateways")
    for g in list(gws):
        if g.findtext("name") == esp["wan"]["gateway"]:
            gws.remove(g)
    g = ET.SubElement(gws, "gateway_item", uuid=uid("gw", esp["wan"]["gateway"]))
    rellenar(g, {"disabled": "0", "name": esp["wan"]["gateway"], "descr": "Proxmox (salida a Internet)",
                 "interface": "wan", "ipprotocol": "inet", "gateway": esp["wan"]["puerta"], "defaultgw": "1",
                 "fargw": "0", "monitor_disable": "1", "monitor_noroute": "0", "monitor_killstates": "0",
                 "monitor_killstates_priority": "0", "force_down": "0", "nosync": "0", "priority": "255", "weight": "1"})

    # alias
    fw = opn.find("Firewall")
    aliases = fw.find("Alias/aliases")
    nombres = {a["nombre"] for a in esp["alias"]}
    for a in list(aliases):
        if a.findtext("name") in nombres:
            aliases.remove(a)
    for a in esp["alias"]:
        e = ET.SubElement(aliases, "alias", uuid=uid("alias", a["nombre"]))
        rellenar(e, {"enabled": "1", "name": a["nombre"], "type": "network", "proto": None, "interface": None,
                     "counters": "0", "updatefreq": None, "content": "\n".join(a["redes"]), "categories": None,
                     "description": a["descripcion"]})

    # reglas: las del repositorio llevan uuid fijo y descripción "[nosub] ..."
    reglas = fw.find("Filter/rules")
    for r in list(reglas):
        if (r.findtext("description") or "").startswith("[nosub]"):
            reglas.remove(r)
    for n, r in enumerate(esp["reglas"]):
        e = ET.SubElement(reglas, "rule", uuid=uid("regla", r["interface"], r["descripcion"]))
        campos = dict(REGLA_BASE)
        campos.update({k: v for k, v in r.items() if k != "descripcion"})
        campos["sequence"] = str(1000 + n * 10)
        campos["description"] = "[nosub] " + r["descripcion"]
        rellenar(e, campos)

    # DHCP/DNS de fábrica (dnsmasq): fuera; el DHCP será Kea con relay y el DNS Unbound/Bind9
    dm = raiz.find("dnsmasq")
    if dm is not None:
        hijo(dm, "enable", "0")
        quitar(dm, "dhcp_ranges")


def normal(texto):
    raiz = ET.fromstring(texto.encode())
    for e in raiz.iter():
        e.attrib.pop("persisted_at", None)
    return ET.tostring(raiz, encoding="unicode")


def main():
    url, ruta = sys.argv[1:3]
    simular = "--simular" in sys.argv
    esp = json.load(open(ruta))
    web = Web(url, "root", os.environ["OPN_CLAVE"])
    actual = web.bajar()
    raiz = ET.fromstring(actual.encode())
    aplicar(raiz, esp)
    nuevo = '<?xml version="1.0"?>\n' + ET.tostring(raiz, encoding="unicode")
    # segunda pasada: aplicar dos veces debe dar lo mismo (idempotente)
    raiz2 = ET.fromstring(nuevo.encode()); aplicar(raiz2, esp)
    assert normal(ET.tostring(raiz2, encoding="unicode")) == normal(nuevo), "la transformación no es idempotente"
    if normal(actual) == normal(nuevo):
        print("SIN CAMBIOS")
        return
    if simular:
        print("Se aplicarían cambios (--simular)\nCAMBIADO")
        return
    web.subir(nuevo)
    print("Configuración subida (falta reiniciar)\nCAMBIADO")


if __name__ == "__main__":
    main()
