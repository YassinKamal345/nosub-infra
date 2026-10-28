#!/usr/bin/python3
"""Genera los diagramas del Documento técnico de NoSub en formato draw.io (.drawio)."""
from xml.sax.saxutils import escape, quoteattr

AZUL, AZUL_F = "#1f4e79", "#dae8fc"
NARANJA, NARANJA_F = "#b45309", "#ffe6cc"
VERDE, VERDE_F = "#2e7d32", "#d5e8d4"
GRIS, GRIS_F = "#555555", "#f5f5f5"
ROJO, ROJO_F = "#b85450", "#f8cecc"
MORADO, MORADO_F = "#6a3d9a", "#e1d5e7"
AMARILLO_F = "#fff2cc"

ICONO = "verticalLabelPosition=bottom;verticalAlign=top;html=1;aspect=fixed;outlineConnect=0;fontSize=12;fontStyle=1;"
CISCO = {
    "router": "shape=mxgraph.cisco.routers.router;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;",
    "switch": "shape=mxgraph.cisco.switches.workgroup_switch;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;",
    "firewall": "shape=mxgraph.cisco.security.firewall;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;",
    "servidor": "shape=mxgraph.cisco.servers.fileserver;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;",
    "ap": "shape=mxgraph.cisco.misc.access_point;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;",
    "pc": "shape=mxgraph.cisco.computers_and_peripherals.pc;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;",
    "portatil": "shape=mxgraph.cisco.computers_and_peripherals.laptop;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;",
    "caja": "shape=mxgraph.cisco.computers_and_peripherals.workstation;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;",
    "nube": "shape=mxgraph.cisco.storage.cloud;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;",
}
TAM = {"router": (50, 33), "switch": (64, 32), "firewall": (40, 60), "servidor": (43, 62), "ap": (50, 34),
       "pc": (50, 43), "portatil": (55, 37), "caja": (50, 45), "nube": (110, 70)}


class Diagrama:
    def __init__(self, nombre):
        self.nombre, self.celdas, self.n = nombre, [], 1

    def _id(self):
        self.n += 1
        return f"c{self.n}"

    def caja(self, texto, x, y, w, h, estilo="", padre="1"):
        i = self._id()
        st = "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fontSize=12;" + estilo
        self.celdas.append(f'<mxCell id="{i}" value={quoteattr(texto)} style="{st}" vertex="1" parent="{padre}">'
                           f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i

    def texto(self, texto, x, y, w, h, estilo=""):
        return self.caja(texto, x, y, w, h, "text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;" + estilo)

    def icono(self, tipo, texto, cx, y, lado="abajo"):
        w, h = TAM[tipo]
        i = self._id()
        st = ICONO + CISCO[tipo]
        if lado == "izquierda":
            st = st.replace("verticalLabelPosition=bottom;verticalAlign=top;", "labelPosition=left;align=right;verticalLabelPosition=middle;verticalAlign=middle;spacingRight=6;")
        if lado == "derecha":
            st = st.replace("verticalLabelPosition=bottom;verticalAlign=top;", "labelPosition=right;align=left;verticalLabelPosition=middle;verticalAlign=middle;spacingLeft=6;")
        self.celdas.append(f'<mxCell id="{i}" value={quoteattr(texto)} style="{st}" vertex="1" parent="1">'
                           f'<mxGeometry x="{cx - w / 2}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i

    def linea(self, a, b, texto="", estilo="", puntos=(), desplazar=None):
        i = self._id()
        st = "html=1;endArrow=none;fontSize=11;labelBackgroundColor=#ffffff;rounded=0;" + estilo
        pts = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in puntos)
        dentro = ("<Array as=\"points\">" + pts + "</Array>" if pts else "")
        if desplazar:
            dentro += f'<mxPoint x="{desplazar[0]}" y="{desplazar[1]}" as="offset"/>'
        geo = f'<mxGeometry relative="1" as="geometry">{dentro}</mxGeometry>'
        self.celdas.append(f'<mxCell id="{i}" value={quoteattr(texto)} style="{st}" edge="1" parent="1" source="{a}" target="{b}">{geo}</mxCell>')
        return i

    def xml(self):
        return ('<mxfile host="drawio" agent="nosub-infra"><diagram name=' + quoteattr(self.nombre) + '>'
                '<mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
                'fold="1" page="0" pageScale="1" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
                + "".join(self.celdas) + '</root></mxGraphModel></diagram></mxfile>\n')


TRONCAL = f"strokeWidth=3;strokeColor={AZUL};"
ACCESO = f"strokeWidth=1.5;strokeColor={GRIS};"
TUNEL = f"strokeWidth=2;strokeColor={NARANJA};dashed=1;endArrow=classic;"
SERIE = f"strokeWidth=2;strokeColor={NARANJA};"
TITULO = "fontSize=20;fontStyle=1;fontColor=#1f4e79;"


def leyenda(d, x, y, filas):
    d.caja("", x, y, 300, 30 + 26 * len(filas), f"fillColor=#ffffff;strokeColor={GRIS};")
    d.texto("<b>Leyenda</b>", x + 10, y + 4, 200, 20)
    for k, (estilo, texto) in enumerate(filas):
        yy = y + 36 + 26 * k
        a = d.caja("", x + 12, yy, 1, 1, "fillColor=none;strokeColor=none;")
        b = d.caja("", x + 72, yy, 1, 1, "fillColor=none;strokeColor=none;")
        d.linea(a, b, "", estilo.replace("endArrow=classic;", "endArrow=none;"))
        d.texto(texto, x + 82, yy - 9, 215, 20, "fontSize=11;")


# ---------------------------------------------------------------- 1. Red física
def red_fisica():
    d = Diagrama("Red física")
    d.texto("Red física de la sede NoSub (instalación en el centro)", 20, 10, 900, 30, TITULO)
    centro = d.icono("nube", "Red del centro<br>(Catalyst 3750-X · Internet)", 700, 60, "derecha")
    r1 = d.icono("router", "R1 · router de borde<br><span style='font-weight:normal'>Cisco 2621 · NAT · OSPF</span>", 700, 200, "derecha")
    sw1 = d.icono("switch", "SW1 · switch núcleo<br><span style='font-weight:normal'>Catalyst 3560G<br>10.10.10.3 · raíz STP</span>", 700, 330, "izquierda")
    sw2 = d.icono("switch", "SW2 · switch de acceso<br><span style='font-weight:normal'>HP ProCurve 2626<br>10.10.10.4</span>", 1250, 330, "derecha")
    r2 = d.icono("router", "R2 · casa cliente A<br>192.168.10.0/24<br><span style='font-weight:normal'>Cisco 2610XM<br>Serial0/0 ↔ R1 Serial0/0</span>", 130, 500, "derecha")
    r3 = d.icono("router", "R3 · oficina cliente B<br>192.168.20.0/24<br><span style='font-weight:normal'>Cisco 2620<br>Serial0/0 ↔ R1 Serial0/1</span>", 390, 500, "derecha")
    ca = d.icono("caja", "Caja cliente A<br>(mini PC)<br><span style='font-weight:normal'>en R2 Fa0/0</span>", 130, 680, "derecha")
    cb = d.icono("caja", "Caja cliente B<br>(mini PC)<br><span style='font-weight:normal'>en R3 Fa0/0</span>", 390, 680, "derecha")
    prx = d.icono("servidor", "Centralita · Proxmox VE<br>10.10.10.2<br><span style='font-weight:normal'>OPNsense y servidores<br>virtuales dentro</span>", 700, 490)
    adm = d.icono("pc", "Puesto de administración<br><span style='font-weight:normal'>SW1 Gi0/4-5 · VLAN 10</span>", 900, 500)
    lab = d.icono("caja", "Cajas en preparación<br><span style='font-weight:normal'>SW1 Gi0/6-8 · VLAN 60</span>", 1080, 500)
    ap = d.icono("ap", "Punto de acceso WiFi<br>10.10.10.5<br><span style='font-weight:normal'>SW2 puerto 1 · troncal<br>10 (nativa), 40, 50<br>SSID Empleados → 40<br>SSID Invitados → 50</span>", 1250, 500)
    emp = d.icono("pc", "Puestos de empleados<br><span style='font-weight:normal'>SW2 puertos 2-20 · VLAN 40</span>", 1420, 500)

    d.linea(centro, r1, "Fa0/0 · IP por DHCP", ACCESO, desplazar=(-75, 0))
    d.linea(r1, sw1, "R1 Fa0/1 ↔ SW1 Gi0/3<br>VLAN 99", ACCESO, desplazar=(-85, 0))
    d.linea(r1, r2, "10.255.0.0/30", SERIE + "exitX=0;exitY=0.3;exitDx=0;exitDy=0;", [(130, 210)], desplazar=(-148, 120))
    d.linea(r1, r3, "10.255.0.4/30", SERIE + "exitX=0;exitY=0.7;exitDx=0;exitDy=0;", [(390, 223)], desplazar=(12, 120))
    d.linea(sw1, prx, "SW1 Gi0/1 ↔ Proxmox<br>troncal 10-60, 99", TRONCAL, desplazar=(-70, 42))
    d.linea(sw1, adm, "", ACCESO + "exitX=0.75;exitY=1;exitDx=0;exitDy=0;", [(716, 430), (900, 430)])
    d.linea(sw1, lab, "", ACCESO + "exitX=0.75;exitY=1;exitDx=0;exitDy=0;", [(716, 430), (1080, 430)])
    d.linea(sw1, sw2, "SW1 Gi0/2 ↔ SW2 puerto 25 · troncal 10, 40, 50", TRONCAL + "exitX=1;exitY=0.5;exitDx=0;exitDy=0;", desplazar=(0, -12))
    d.linea(sw2, ap, "", TRONCAL)
    d.linea(sw2, emp, "", ACCESO + "exitX=0.75;exitY=1;exitDx=0;exitDy=0;", [(1266, 430), (1420, 430)])
    d.linea(r2, ca, "", ACCESO)
    d.linea(r3, cb, "", ACCESO)

    d.caja("<b>Casas de los clientes</b> · Internet simulado<br>enlaces serie R1-R2 y R1-R3 (R1 = DCE, OSPF)", 50, 470, 530, 320,
           f"fillColor=none;dashed=1;strokeColor={NARANJA};verticalAlign=bottom;fontColor={NARANJA};spacingBottom=6;")
    leyenda(d, 1180, 700, [(TRONCAL, "Troncal 802.1Q (varias VLANs)"), (ACCESO, "Acceso (una sola VLAN)"), (SERIE, "Enlace serie (cable DB-60)")])
    d.texto("Puertos sin uso: apagados y en la VLAN 999 (nativa de los troncales).<br>"
            "Puertos de acceso con portfast y BPDU guard · STP: MST (SW1) y RSTP (SW2) · solo SSH v2.<br>"
            "<i>En el laboratorio (prx): SW1 y SW2 = bridge vmbr1 con VLANs, R1 = prx (vmbr2) y R2/R3 = GNS3.</i>",
            640, 700, 520, 70, "fontSize=11;")
    return d


# ---------------------------------------------------------------- 2. Red lógica
VLANS = [
    ("VLAN 10 · Gestión", "10.10.10.0/24", AZUL_F, AZUL,
     ["OPNsense .1", "Proxmox .2", "SW1 .3 · SW2 .4", "AP .5", "GNS3 .20", "DHCP .100-.199"], "→ todo"),
    ("VLAN 20 · Servidores", "10.10.20.0/24", VERDE_F, VERDE,
     ["gitea .10 · Gitea, Ansible", "red-int .11 · DNS, DHCP, proxy", "bbdd .12 · PostgreSQL",
      "monitor .13 · Prometheus,<br>Grafana", "intranet .14 · Wiki.js,<br>Nextcloud"], "→ todo menos gestión"),
    ("VLAN 30 · DMZ", "10.10.30.0/24", ROJO_F, ROJO,
     ["extranet .10 · Traefik<br>y portal de clientes", "k3s .20 · hosting DAM/DAW"], "→ solo Internet<br>(y BBDD :5432)"),
    ("VLAN 40 · Empleados", "10.10.40.0/24", AMARILLO_F, "#b8860b",
     ["Puestos y WiFi", "DHCP .100-.199"], "→ servidores, DMZ,<br>Internet"),
    ("VLAN 50 · Invitados", "10.10.50.0/24", GRIS_F, GRIS,
     ["WiFi de invitados", "DHCP .100-.199"], "→ solo Internet"),
    ("VLAN 60 · Lab cajas", "10.10.60.0/24", MORADO_F, MORADO,
     ["Cajas en preparación", "DHCP .100-.199"], "→ servidores, Internet"),
    ("VPN · WireGuard", "10.99.0.0/24", NARANJA_F, NARANJA,
     ["Servidor .1", "Teletrabajo .2-.127", "Cajas 10.99.0.128/25"], "teletrabajo →<br>servidores y DMZ<br>cajas → solo responden"),
]


def red_logica():
    d = Diagrama("Red lógica")
    d.texto("Red lógica de NoSub: redes, direcciones y quién puede hablar con quién", 20, 10, 1100, 30, TITULO)
    inet = d.icono("nube", "Internet", 760, 50, "izquierda")
    vps = d.icono("servidor", "VPS cloud (Oracle)<br><span style='font-weight:normal'>página de estado ·<br>entrada de la VPN · copias</span>", 1260, 100, "derecha")
    r1 = d.icono("router", "R1 · 172.31.255.1<br><span style='font-weight:normal'>NAT · OSPF área 0</span>", 760, 190, "derecha")
    fw = d.icono("firewall", "OPNsense · firewall<br><span style='font-weight:normal'>WAN 172.31.255.2<br>NAT · DMZ · WireGuard<br>relay DHCP</span>", 760, 330, "izquierda")
    r2 = d.icono("router", "R2 · 10.255.0.2<br><span style='font-weight:normal'>cliente A<br>192.168.10.0/24</span>", 130, 280, "derecha")
    r3 = d.icono("router", "R3 · 10.255.0.6<br><span style='font-weight:normal'>cliente B<br>192.168.20.0/24</span>", 340, 280, "derecha")
    ca = d.icono("caja", "Caja A<br><span style='font-weight:normal'>VPN 10.99.0.129</span>", 130, 400, "derecha")
    cb = d.icono("caja", "Caja B<br><span style='font-weight:normal'>VPN 10.99.0.130</span>", 340, 400, "derecha")
    tele = d.icono("portatil", "Teletrabajo<br><span style='font-weight:normal'>VPN 10.99.0.10</span>", 1360, 250, "derecha")

    d.linea(inet, r1, "", ACCESO)
    d.linea(r1, fw, "VLAN 99<br>172.31.255.0/30", TRONCAL, desplazar=(70, 0))
    d.linea(r1, r2, "enlaces serie 10.255.0.0/30 y 10.255.0.4/30 (Internet simulado, OSPF)", SERIE + "exitX=0;exitY=0.5;exitDx=0;exitDy=0;", [(130, 207)], desplazar=(110, -13))
    d.linea(r1, r3, "", SERIE + "exitX=0;exitY=0.5;exitDx=0;exitDy=0;", [(340, 207)])
    d.linea(r2, ca, "NAT · DHCP", ACCESO, desplazar=(-38, 0))
    d.linea(r3, cb, "NAT · DHCP", ACCESO, desplazar=(-38, 0))
    d.linea(inet, vps, "", ACCESO + "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.25;entryDx=0;entryDy=0;")
    d.linea(ca, vps, "túnel WireGuard · UDP 51820 (cajas y teletrabajo)",
            TUNEL + "exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.6;entryDx=0;entryDy=0;", [(40, 422), (40, 145), (1238, 145)])
    d.linea(cb, vps, "", TUNEL + "exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.75;entryDx=0;entryDy=0;", [(300, 422), (300, 450), (55, 450), (55, 155), (1238, 155)])
    d.linea(tele, vps, "", TUNEL + "exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.75;entryY=1;entryDx=0;entryDy=0;", [(1360, 200), (1271, 200)])
    d.linea(fw, vps, "enlace WireGuard 10.98.0.0/30<br>(lo abre la sede: no necesita IP pública)",
            TUNEL.replace("endArrow=classic;", "endArrow=classic;startArrow=classic;") + "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0.25;entryY=1;entryDx=0;entryDy=0;",
            [(1249, 360)], desplazar=(-60, -24))

    x0, ancho, sep = 20, 195, 10
    bus_y = 490
    for k, (titulo, red, relleno, borde, filas, permiso) in enumerate(VLANS):
        x = x0 + k * (ancho + sep)
        cuerpo = "<br>".join(filas)
        v = d.caja(f"<b>{titulo}</b><br>{red}<hr>"
                   f"<span style='font-size:11px'>{cuerpo}</span><hr>"
                   f"<span style='font-size:11px;color:{borde}'><b>{permiso}</b></span>",
                   x, 520, ancho, 205, f"fillColor={relleno};strokeColor={borde};strokeWidth=2;verticalAlign=top;spacing=6;")
        d.linea(fw, v, "", f"strokeColor={borde};strokeWidth=2;", [(760, bus_y), (x + ancho / 2, bus_y)])
    d.texto("Todo lo que no está permitido está bloqueado. La web y el SSH del firewall solo se abren desde gestión. "
            "DNS: Bind9 (zona nosub.lan) · DHCP: Kea con relay en OPNsense · salida a Internet con doble NAT (OPNsense y R1).",
            20, 740, 1420, 40, "fontSize=11;")
    leyenda(d, 1262, 340, [(TRONCAL, "Troncal / enlace 802.1Q"), (ACCESO, "Enlace normal"), (SERIE, "Enlace serie (Internet simulado)"), (TUNEL, "Túnel WireGuard (cifrado)")])
    return d


# ---------------------------------------------------------------- 3. Estructura del proyecto
def estructura():
    d = Diagrama("Estructura del proyecto")
    d.texto("Estructura del repositorio nosub-infra (Gitea + espejo en GitHub)", 20, 10, 1000, 30, TITULO)
    carpetas = [
        ("inventories/", "Qué máquinas hay y sus datos", AZUL_F, AZUL,
         ["sede/hosts.yml · máquinas de la sede", "sede/group_vars/all/ · VLANs, servicios, red física, cloud, cajas",
          "sede/group_vars/all/vault.yml · secretos (cifrado con Ansible Vault)", "sede/ca/ · certificado de la NoSub CA",
          "cajas/hosts.yml · una entrada por caja", "cajas/wireguard/*.pub · claves públicas de las cajas"]),
        ("playbooks/", "Qué se aplica y dónde", VERDE_F, VERDE,
         ["sede.yml · monta la sede entera", "caja_nueva.yml · prepara y da de alta una caja",
          "caja_entregar.yml · pasa la caja a casa del cliente", "actualizar_cajas.yml · actualiza las cajas por la VPN",
          "red_fisica.yml · configuraciones de R1-R3, SW1-SW2 y AP", "gns3.yml · ensayo de la red en GNS3"]),
        ("scripts/", "Pruebas y simulacros", AMARILLO_F, "#b8860b",
         ["probar-red.sh · probar-dhcp.sh · probar-vpn.sh · probar-cajas.sh",
          "simulacro-restauracion.sh · simulacro-corte-luz.sh", "totp-qr.sh · QR del doble factor"]),
        ("docs/", "Documentación de la entrega", MORADO_F, MORADO,
         ["red.md · planos de red", "riesgos.md · contingencia.md · simulacro.md", "rgpd.md · defensa.md · plan.md"]),
        ("network/ · plugins/", "Otros", GRIS_F, GRIS,
         ["network/generado/ · configuraciones Cisco (fuera de Git)", "plugins/filter/ · filtros propios (TOTP, WireGuard)"]),
    ]
    tronco_x, carp_x, cont_x = 250, 290, 510
    y = 70
    centros = []
    for nombre, desc, relleno, borde, filas in carpetas:
        h = 22 + 18 * len(filas)
        cy = y + h / 2
        c = d.caja(f"<b>{nombre}</b><br><i style='font-size:11px'>{desc}</i>", carp_x, cy - 25, 190, 50,
                   f"fillColor={relleno};strokeColor={borde};strokeWidth=2;")
        k = d.caja("<div style='text-align:left'>" + "<br>".join(filas) + "</div>", cont_x, y, 420, h,
                   f"fillColor=#ffffff;strokeColor={borde};fontSize=11;align=left;spacingLeft=10;")
        d.linea(c, k, "", f"strokeColor={borde};strokeWidth=1.5;")
        centros.append((c, cy, borde))
        y += h + 16

    grupos = [
        ("Infraestructura", AZUL, ["proxmox_vms", "red_lab", "opnsense", "red_fisica"]),
        ("Servicios de red", VERDE, ["bind9", "kea_dhcp", "squid"]),
        ("Datos y copias", "#b8860b", ["postgresql", "copias_externas"]),
        ("Aplicaciones", ROJO, ["gitea", "intranet", "extranet", "traefik", "k3s"]),
        ("Monitorización", MORADO, ["monitorizacion", "node_exporter"]),
        ("Sistema y seguridad", GRIS, ["actualizaciones", "ssh_seguro", "registros"]),
        ("Producto: la caja", NARANJA, ["caja", "caja_lab", "caja_minipc"]),
        ("Cloud y laboratorio", "#036897", ["cloud", "cloud_lab", "gns3"]),
    ]
    gy = y + 10
    alto_g = 118
    fondo = d.caja("", cont_x - 10, gy - 10, 4 * 205 + 15, 2 * (alto_g + 10) + 40,
                   f"fillColor=#fdf3f2;strokeColor={ROJO};dashed=1;")
    roles_cy = gy + alto_g + 5
    roles = d.caja("<b>roles/</b><br><i style='font-size:11px'>25 roles: uno por servicio</i>", carp_x, roles_cy - 25, 190, 50,
                   f"fillColor={ROJO_F};strokeColor={ROJO};strokeWidth=2;")
    d.linea(roles, fondo, "", f"strokeColor={ROJO};strokeWidth=1.5;")
    centros.append((roles, roles_cy, ROJO))
    for k, (titulo, color, lista) in enumerate(grupos):
        x = cont_x + (k % 4) * 205
        yy = gy + (k // 4) * (alto_g + 10)
        d.caja(f"<b style='color:{color}'>{titulo}</b><br><span style='font-size:11px'>" + "<br>".join(lista) + "</span>",
               x, yy, 195, alto_g, f"fillColor=#ffffff;strokeColor={color};verticalAlign=top;")
    d.texto("Cada rol tiene: tasks/ (pasos) · defaults/ (valores) · templates/ y files/ (configuraciones) · handlers/ · README.md",
            cont_x, gy + 2 * (alto_g + 10) - 2, 820, 20, "fontSize=11;fontStyle=2;align=center;")

    raiz_cy = (centros[0][1] + centros[-1][1]) / 2
    raiz = d.caja("<b>nosub-infra/</b><br>ansible.cfg<br>README.md", 30, raiz_cy - 35, 170, 70,
                  f"fillColor={AZUL};fontColor=#ffffff;strokeColor={AZUL};fontSize=13;")
    for c, cy, borde in centros:
        d.linea(raiz, c, "", f"strokeColor={AZUL};strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;",
                [(tronco_x, raiz_cy), (tronco_x, cy)])
    return d


# ---------------------------------------------------------------- 4. Entidad-Relación
def tabla(d, nombre, x, y, campos, color):
    alto = 30 + 22 * len(campos)
    t = d.caja(f"<b>{nombre}</b>", x, y, 250, alto,
               f"swimlane;fontStyle=1;startSize=30;fillColor={color};strokeColor={AZUL};rounded=1;arcSize=6;horizontal=1;")
    for k, (clave, campo, tipo) in enumerate(campos):
        d.caja(f"<b>{clave}</b>" if clave else "", 0, 30 + 22 * k, 40, 22,
               "text;strokeColor=none;fillColor=none;align=center;fontSize=10;fontColor=#1f4e79;", t)
        d.caja(f"{'<u>' + campo + '</u>' if clave == 'PK' else campo}", 40, 30 + 22 * k, 120, 22,
               "text;strokeColor=none;fillColor=none;align=left;fontSize=11;", t)
        d.caja(tipo, 160, 30 + 22 * k, 90, 22, "text;strokeColor=none;fillColor=none;align=left;fontSize=10;fontColor=#555555;", t)
    return t


def er():
    d = Diagrama("Entidad-Relación")
    d.texto("Base de datos del portal de clientes (extranet) · PostgreSQL 16 · base «extranet»", 20, 10, 1000, 30, TITULO)
    cli = tabla(d, "clientes", 40, 80, [("PK", "id", "serial"), ("UQ", "usuario", "text"), ("", "nombre", "text"),
                                         ("", "correo", "text"), ("", "clave_hash", "text"), ("", "creado", "timestamptz")], AZUL_F)
    caj = tabla(d, "cajas", 470, 60, [("PK", "id", "serial"), ("FK", "cliente_id", "integer"), ("UQ", "nombre", "text"),
                                       ("", "ip_vpn", "inet"), ("", "red", "cidr"), ("", "servicios", "text[]"),
                                       ("", "ultima_conexion", "timestamptz")], VERDE_F)
    inc = tabla(d, "incidencias", 470, 340, [("PK", "id", "serial"), ("FK", "cliente_id", "integer"), ("FK", "caja_id", "integer (nulo)"),
                                             ("", "asunto", "text"), ("", "detalle", "text"),
                                             ("", "estado", "text (CHECK)"), ("", "creada", "timestamptz")], AMARILLO_F)
    fal = tabla(d, "intentos_fallidos", 40, 380, [("", "usuario", "text"), ("", "ip", "inet"), ("", "cuando", "timestamptz")], GRIS_F)
    rel = "html=1;edgeStyle=orthogonalEdgeStyle;fontSize=11;labelBackgroundColor=#ffffff;strokeWidth=1.5;strokeColor=#1f4e79;"
    d.linea(cli, caj, "tiene", rel + "startArrow=ERmandOne;endArrow=ERmany;startFill=0;endFill=0;exitX=1;exitY=0.35;exitDx=0;exitDy=0;entryX=0;entryY=0.35;entryDx=0;entryDy=0;")
    d.linea(cli, inc, "abre", rel + "startArrow=ERmandOne;endArrow=ERmany;startFill=0;endFill=0;exitX=1;exitY=0.8;exitDx=0;exitDy=0;entryX=0;entryY=0.35;entryDx=0;entryDy=0;", [(380, 228), (380, 404)])
    d.linea(caj, inc, "afecta a", rel + "startArrow=ERzeroToOne;endArrow=ERmany;startFill=0;endFill=0;")
    d.linea(fal, cli, "usuario (sin clave foránea)", "html=1;dashed=1;endArrow=open;fontSize=11;labelBackgroundColor=#ffffff;strokeColor=#888888;")
    d.texto("<b>Relaciones</b><br>· Un cliente tiene 0..N cajas; cada caja es de un solo cliente.<br>"
            "· Un cliente abre 0..N incidencias; cada incidencia puede referirse a una<br>&nbsp;&nbsp;de sus cajas (o a ninguna).<br>"
            "· Al borrar un cliente se borran sus cajas e incidencias (ON DELETE CASCADE);<br>&nbsp;&nbsp;al borrar una caja, sus incidencias quedan sin caja (ON DELETE SET NULL).<br>"
            "· incidencias.estado solo admite: abierta, en curso o cerrada (restricción CHECK).<br>"
            "· intentos_fallidos guarda los inicios de sesión fallidos para bloquear<br>&nbsp;&nbsp;ataques de fuerza bruta (se borran a las 24 h).",
            770, 80, 600, 170, "fontSize=11;")
    d.texto("PK = clave primaria · FK = clave foránea · UQ = valor único", 770, 260, 400, 20, "fontSize=11;fontStyle=2;")
    return d


if __name__ == "__main__":
    import sys
    destino = sys.argv[1] if len(sys.argv) > 1 else "."
    for nombre, f in [("1-red-fisica", red_fisica), ("2-red-logica", red_logica), ("3-estructura-proyecto", estructura), ("4-entidad-relacion", er)]:
        open(f"{destino}/{nombre}.drawio", "w", encoding="utf8").write(f().xml())
        print(nombre)
