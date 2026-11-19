#!/usr/bin/python3
"""Genera los diagramas de casos de uso de NoSub (sede, caja y los dos juntos) en formato draw.io."""
from xml.sax.saxutils import quoteattr
from generar import Diagrama, AZUL, AZUL_F, VERDE, VERDE_F, NARANJA, NARANJA_F, GRIS, TITULO

ACTOR = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fontSize=12;fontStyle=1;"
ASOCIACION = f"endArrow=none;strokeColor={GRIS};strokeWidth=1.2;"
RELACION = "dashed=1;endArrow=open;endSize=10;strokeColor=#333333;fontSize=10;fontStyle=2;"
FLUJO = f"dashed=1;endArrow=block;endFill=1;strokeColor={NARANJA};strokeWidth=2;fontSize=11;fontStyle=1;fontColor={NARANJA};"
GENERALIZA = f"endArrow=block;endFill=0;endSize=14;strokeColor={GRIS};"
NUEVO = f"fillColor={NARANJA_F};strokeColor={NARANJA};strokeWidth=2;"
PREVISTO = "dashed=1;fillColor=#ffffff;strokeColor=#888888;fontColor=#555555;"
W, H = 190, 56


def actor(d, texto, x, y):
    i = d._id()
    d.celdas.append(f'<mxCell id="{i}" value={quoteattr(texto)} style="{ACTOR}" vertex="1" parent="1">'
                    f'<mxGeometry x="{x}" y="{y}" width="34" height="64" as="geometry"/></mxCell>')
    return i


def cu(d, texto, x, y, color, estilo="", w=W):
    return d.caja(texto, x, y, w, H, f"ellipse;fillColor={color};strokeColor=#555555;fontSize=11;" + estilo)


def sistema(d, texto, x, y, w, h, color):
    d.caja(f"<b>{texto}</b>", x, y, w, h, f"fillColor=none;strokeColor={color};strokeWidth=2;verticalAlign=top;"
           f"align=left;spacingLeft=10;spacingTop=4;fontSize=14;fontColor={color};arcSize=2;")


def inc(d, a, b, texto="«include»", puntos=(), estilo=""):
    d.linea(a, b, texto, RELACION + estilo, puntos)


def leyenda(d, x, y, previsto=True):
    filas = [("fillColor=#ffffff;strokeColor=#555555;", "Fase 1 (sprints 1-4): servicios obligatorios"),
             (NUEVO, "Nuevo: datos de uso caja → sede")]
    if previsto:
        filas.append((PREVISTO, "Fase 2 (sprints 5-6): partes individuales"))
    d.caja("", x, y, 300, 34 + 30 * len(filas) + 44, f"fillColor=#ffffff;strokeColor={GRIS};")
    d.texto("<b>Leyenda</b>", x + 10, y + 4, 200, 20)
    for k, (estilo, texto) in enumerate(filas):
        d.caja("", x + 12, y + 32 + 30 * k, 60, 24, "ellipse;" + estilo)
        d.texto(texto, x + 82, y + 34 + 30 * k, 215, 20, "fontSize=11;")
    d.texto("«include»: siempre lo usa · «extend»: solo a veces<br>Muñeco: persona o sistema que lo usa",
            x + 10, y + 36 + 30 * len(filas), 285, 36, "fontSize=10;fontColor=#555555;")


# ---------------------------------------------------------------- 5a. Sede: servicios del servidor
def paquete(d, titulo, detalle, x, y, w, h, color=AZUL, discontinuo=False):
    d.caja(f"<b>{titulo}</b><br><span style='font-size:10px'>{detalle}</span>", x, y, w, h,
           f"fillColor=#f4f8fd;strokeColor={color};verticalAlign=top;align=left;spacingLeft=8;spacingTop=2;fontSize=12;"
           f"fontColor={color};arcSize=3;" + ("dashed=1;" if discontinuo else ""))


def sede_servicios():
    d = Diagrama("Casos de uso · Servidor de la sede")
    d.texto("Sede central (1/2): lo que hace cada máquina del servidor", 20, 10, 1200, 30, TITULO)
    sistema(d, "Servidor de la sede (Proxmox VE): cada recuadro es una máquina virtual o un contenedor", 200, 60, 1130, 1010, AZUL)
    c = "#ffffff"
    xa, xb = 250, 790
    R, L, T, B = "exitX=1;exitY=0.5;exitDx=0;exitDy=0;", "exitX=0;exitY=0.5;exitDx=0;exitDy=0;", "entryX=0.5;entryY=0;entryDx=0;entryDy=0;", "entryX=0.5;entryY=1;entryDx=0;entryDy=0;"
    paquete(d, "intranet (10.10.20.14)", "Wiki.js · Nextcloud", 225, 110, 500, 200)
    s7 = cu(d, "S07 · Consultar la wiki<br>de procedimientos", xa, 150, c, w=200)
    s8 = cu(d, "S08 · Guardar y compartir<br>archivos", xa, 225, c, w=200)
    paquete(d, "gitea (10.10.20.10)", "repositorio Git", 225, 320, 500, 105)
    s17 = cu(d, "S17 · Guardar código<br>y configuración", xa, 357, c, w=200)
    paquete(d, "fw · OPNsense (10.10.10.1)", "firewall, VLANs y VPN WireGuard", 225, 440, 500, 290)
    s1 = cu(d, "S01 · Conectarse a la red<br>de la oficina", xa, 490, c, w=200)
    s2 = cu(d, "S02 · Teletrabajar<br>por la VPN", xa, 570, c, w=200)
    s3 = cu(d, "S03 · Usar el WiFi<br>de invitados", xa, 650, c, w=200)
    paquete(d, "red-int (10.10.20.11)", "Kea DHCP · Bind9 DNS · Squid", 225, 750, 500, 305)
    s4 = cu(d, "S04 · Recibir una IP<br>automática (DHCP)", xa + 260, 790, c, w=200)
    s5 = cu(d, "S05 · Resolver nombres<br>(DNS nosub.lan)", xa + 260, 880, c, w=200)
    s6 = cu(d, "S06 · Navegar por<br>el proxy (Squid)", xa, 950, c, w=200)

    paquete(d, "bbdd (10.10.20.12)", "PostgreSQL (Rocky Linux)", 765, 110, 540, 120)
    s15 = cu(d, "S15 · Guardar y leer datos<br>(PostgreSQL)", xb, 150, c, w=200)
    paquete(d, "extranet · DMZ (10.10.30.10)", "Traefik (HTTPS) · portal de clientes", 765, 250, 540, 450)
    s10 = cu(d, "S10 · Iniciar sesión<br>en el portal", xb, 400, c, w=200)
    s9 = cu(d, "S09 · Entrar por HTTPS<br>(Traefik)", xb, 560, c, w=200)
    s11 = cu(d, "S11 · Consultar mis cajas", xb + 280, 300, c, w=200)
    s12 = cu(d, "S12 · Abrir una incidencia", xb + 280, 395, c, w=200)
    s13 = cu(d, "S13 · Ver mis estadísticas<br>de uso", xb + 280, 490, c, NUEVO, w=200)
    s14 = cu(d, "S14 · Aceptar o retirar el<br>envío de datos de uso", xb + 280, 585, c, NUEVO, w=200)
    paquete(d, "k3s · DMZ (10.10.30.20)", "Kubernetes ligero", 765, 720, 540, 100)
    s16 = cu(d, "S16 · Publicar un proyecto<br>DAM/DAW", xb + 280, 755, c, w=200)
    paquete(d, "VPS en el cloud (fuera del servidor)", "Gatus · copias externas", 765, 845, 540, 120, NARANJA, True)
    s18 = cu(d, "S18 · Ver la página de estado<br>de NoSub", xb + 280, 890, c, w=200)

    empleado = actor(d, "Empleado", 80, 250)
    tele = actor(d, "Teletrabajador", 80, 560)
    invitado = actor(d, "Invitado", 80, 760)
    cliente = actor(d, "Cliente", 1420, 430)
    alumno = actor(d, "Alumno<br>DAM/DAW", 1420, 740)
    publico = actor(d, "Cualquiera<br><span style='font-weight:normal'>(Internet)</span>", 1420, 880)
    d.linea(tele, empleado, "", GENERALIZA)
    for u in (s1, s7, s8, s17):
        d.linea(empleado, u, "", ASOCIACION)
    d.linea(tele, s2, "", ASOCIACION)
    d.linea(invitado, s3, "", ASOCIACION)
    for u in (s11, s12, s13, s14):
        d.linea(cliente, u, "", ASOCIACION)
        inc(d, u, s10)
    d.linea(alumno, s16, "", ASOCIACION)
    d.linea(publico, s18, "", ASOCIACION)
    inc(d, s1, s4, estilo=R + T)
    inc(d, s1, s5, "«include»", [(740, 518), (740, 908)], R + "entryX=1;entryY=0.5;entryDx=0;entryDy=0;")
    inc(d, s3, s4)
    inc(d, s6, s1, "«extend»", [(235, 978), (235, 518)], L + "entryX=0;entryY=0.5;entryDx=0;entryDy=0;")
    inc(d, s10, s9, estilo="exitX=0.5;exitY=1;exitDx=0;exitDy=0;" + T)
    inc(d, s16, s9, estilo=L + B)
    for u in (s7, s8, s17):
        inc(d, u, s15, estilo=R + "entryX=0;entryY=0.5;entryDx=0;entryDy=0;")
    inc(d, s10, s15, estilo="exitX=0.5;exitY=0;exitDx=0;exitDy=0;" + B)
    leyenda(d, 1350, 1000, previsto=False)
    return d


# ---------------------------------------------------------------- 5b. Sede: administración y operación
def sede_admin():
    d = Diagrama("Casos de uso · Administración de la sede")
    d.texto("Sede central (2/2): administración y operación", 20, 10, 1200, 30, TITULO)
    sistema(d, "Sede central NoSub · administración (Ansible, Gitea, Prometheus, Grafana, copias)", 200, 60, 1110, 1090, AZUL)
    c = "#ffffff"
    x1, x2, x3 = 230, 520, 880

    admin = actor(d, "Administrador<br>de sistemas", 70, 300)
    soporte = actor(d, "Técnico de<br>soporte", 70, 740)
    producto = actor(d, "Responsable<br>de producto", 70, 1000)
    reloj = actor(d, "Reloj<br><span style='font-weight:normal'>(tareas diarias)</span>", 1400, 470)
    caja = actor(d, "Caja del cliente<br><span style='font-weight:normal'>«sistema»</span>", 1400, 820)

    s19 = cu(d, "S19 · Desplegar o actualizar<br>la sede con Ansible", x1, 100, c)
    s20 = cu(d, "S20 · Cambiar VLANs, reglas,<br>DNS o DHCP", x1, 180, c)
    s22 = cu(d, "S22 · Dar de alta una caja<br>(pedido: nº de serie y apps)", x1, 300, c)
    s25 = cu(d, "S25 · Actualizar las cajas<br>a distancia", x1, 400, c)
    s26 = cu(d, "S26 · Dar de baja una caja", x1, 480, c)
    s27 = cu(d, "S27 · Restaurar una copia<br>de seguridad", x1, 560, c)
    s28 = cu(d, "S28 · Vigilar la sede y las<br>cajas (Grafana)", x1, 680, c)
    s29 = cu(d, "S29 · Recibir un aviso<br>en el móvil", x1, 760, c)
    s30 = cu(d, "S30 · Atender incidencias<br>de clientes", x1, 840, c)
    s31 = cu(d, "S31 · Analizar estadísticas<br>de uso", x1, 960, c, NUEVO)
    s32 = cu(d, "S32 · Mejorar el catálogo<br>de apps", x1, 1060, c, NUEVO)
    s21 = cu(d, "S21 · Guardar el cambio<br>en Gitea", x2, 140, c)
    s23 = cu(d, "S23 · Crear el túnel<br>WireGuard de la caja", x2, 260, c)
    s24 = cu(d, "S24 · Elegir apps<br>del catálogo", x2, 380, c)
    s33 = cu(d, "S33 · Hacer copias de seguridad<br>(sede y cloud)", x3, 560, c, w=210)
    s34 = cu(d, "S34 · Instalar parches<br>de seguridad", x3, 440, c, w=210)
    s35 = cu(d, "S35 · Leer el estado de<br>cada caja (Prometheus)", x3, 680, c, w=210)
    s36 = cu(d, "S36 · Recibir y guardar datos<br>de uso (PostgreSQL)", x3, 960, c, NUEVO, w=210)
    s37 = cu(d, "S37 · Atender la solicitud del<br>primer arranque de una caja", x3, 820, c, PREVISTO, w=210)
    for u in (s19, s20, s22, s25, s26, s27):
        d.linea(admin, u, "", ASOCIACION)
    for u in (s28, s29, s30):
        d.linea(soporte, u, "", ASOCIACION)
    for u in (s31, s32):
        d.linea(producto, u, "", ASOCIACION)
    for u in (s33, s34):
        d.linea(reloj, u, "", ASOCIACION)
    for u in (s35, s36, s37):
        d.linea(caja, u, "", ASOCIACION)
    inc(d, s19, s21)
    inc(d, s20, s21)
    inc(d, s22, s23)
    inc(d, s22, s24)
    inc(d, s25, s24)
    inc(d, s29, s28, "«extend»")
    inc(d, s28, s35, "usa", estilo="exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;")
    inc(d, s31, s36, "usa los datos de", estilo="exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;")
    inc(d, s32, s31, "«extend»")
    inc(d, s32, s25, "«include»", [(215, 1088), (215, 428)], "exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;")
    inc(d, s27, s33, "usa", estilo="exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;")
    inc(d, s37, s23, "«include»", [(1350, 848), (1350, 240), (705, 240)], "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;")
    leyenda(d, 1310, 1170)
    return d


# ---------------------------------------------------------------- 6. Caja del cliente
def caja():
    d = Diagrama("Casos de uso · Caja")
    d.texto("Casos de uso de la caja del cliente (el producto)", 20, 10, 900, 30, TITULO)
    sistema(d, "Caja NoSub (mini PC en casa del cliente)", 200, 60, 1110, 960, VERDE)
    c = VERDE_F
    x1, x2, x3, x4 = 230, 500, 790, 1090

    usuario = actor(d, "Persona de<br>la casa", 70, 300)
    titular = actor(d, "Cliente<br>titular", 70, 760)
    tecnico = actor(d, "Técnico de NoSub<br><span style='font-weight:normal'>(a distancia)</span>", 1400, 170)
    reloj = actor(d, "Reloj<br><span style='font-weight:normal'>(tareas diarias)</span>", 1400, 600)
    sede = actor(d, "Sede NoSub<br><span style='font-weight:normal'>«sistema»</span>", 1400, 880)
    d.linea(titular, usuario, "", GENERALIZA)

    # Uso diario en casa
    u1 = cu(d, "C01 · Abrir la página<br>de inicio", x1, 90, c)
    u2 = cu(d, "C02 · Navegar sin anuncios<br>ni rastreadores", x1, 170, c)
    u3 = cu(d, "C03 · Escuchar música", x1, 250, c)
    u4 = cu(d, "C04 · Editar y convertir PDF", x1, 330, c)
    u5 = cu(d, "C05 · Guardar y ver fotos", x1, 410, c, PREVISTO)
    u6 = cu(d, "C06 · Guardar y compartir<br>archivos", x1, 490, c, PREVISTO)
    u7 = cu(d, "C07 · Guardar contraseñas", x1, 570, c, PREVISTO)
    t1 = cu(d, "C08 · Configurar el bloqueo<br>y el control parental", x1, 700, c)
    t2 = cu(d, "C09 · Usar las apps<br>fuera de casa", x1, 780, c, PREVISTO)
    t3 = cu(d, "C10 · Hacer copia de los<br>datos de la caja", x1, 860, c, PREVISTO)
    for u in (u1, u2, u3, u4, u5, u6, u7):
        d.linea(usuario, u, "", ASOCIACION)
    for u in (t1, t2, t3):
        d.linea(titular, u, "", ASOCIACION)

    dns = cu(d, "C11 · Filtrar las consultas<br>DNS (AdGuard)", x2, 170, c)
    login = cu(d, "C12 · Iniciar sesión<br>en la app", x2, 450, c)
    inc(d, u2, dns)
    for u in (u3, u5, u6, u7, t1):
        inc(d, u, login)

    # Mantenimiento desde la sede
    m1 = cu(d, "C13 · Instalar o quitar<br>apps del catálogo", x3, 100, c)
    m2 = cu(d, "C14 · Aplicar una actualización<br>de la caja", x3, 180, c)
    m3 = cu(d, "C15 · Revisar el estado<br>(CPU, disco, servicios)", x3, 260, c)
    tunel = cu(d, "C16 · Conectar con la sede<br>(túnel WireGuard)", x4, 330, c, w=200)
    alta = cu(d, "C21 · Descargar sus servicios<br>en el primer arranque", x3, 375, c, PREVISTO, w=200)
    inc(d, alta, tunel)
    for u in (m1, m2, m3):
        d.linea(tecnico, u, "", ASOCIACION)
        inc(d, u, tunel)

    # Tareas automáticas
    a1 = cu(d, "C17 · Instalar parches<br>de seguridad", x3, 480, c)
    a2 = cu(d, "C18 · Recoger estadísticas<br>de uso", x3, 640, c, NUEVO)
    a3 = cu(d, "C19 · Quitar datos personales<br>(solo recuentos)", x3, 760, c, NUEVO)
    a4 = cu(d, "C20 · Enviar las estadísticas<br>a la sede", x4, 700, c, NUEVO, w=200)
    for u in (a1, a2):
        d.linea(reloj, u, "", ASOCIACION)
    inc(d, a2, a3)
    inc(d, a2, a4)
    inc(d, a4, tunel, estilo="exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;")
    d.linea(sede, a4, "", ASOCIACION)
    d.linea(sede, tunel, "", ASOCIACION, [(1350, 820), (1350, 358)])
    d.linea(sede, alta, "", ASOCIACION, [(1370, 830), (1370, 403)])
    d.texto("C18 solo se hace si el cliente lo ha aceptado en el portal (S14).<br>"
            "Nunca se envían ficheros, fotos ni el historial de navegación:<br>solo recuentos y listas de lo más usado.",
            x3, 850, 470, 60, f"fontSize=11;fontColor={NARANJA};fontStyle=2;")
    d.texto("Si la sede no responde, C01-C12 siguen funcionando: todo es local.", x2, 960, 600, 24, "fontSize=11;fontStyle=2;")
    d.texto("Más apps para la persona de la casa (C22-C51, catálogo ampliado de la fase 3): diagramas 3b y 3c.", x2, 984, 620, 24,
            "fontSize=11;fontStyle=2;fontColor=#1f4e79;")
    leyenda(d, 1310, 1040)
    return d


# ---------------------------------------------------------------- 7. Sede + caja
def conjunto():
    d = Diagrama("Casos de uso · Sede y caja")
    d.texto("NoSub completo: cómo se unen la caja y la sede", 20, 10, 1000, 30, TITULO)
    sistema(d, "Caja del cliente (casa)", 200, 60, 330, 860, VERDE)
    sistema(d, "Sede central NoSub", 960, 60, 360, 860, AZUL)
    d.caja(f"<b>Túnel WireGuard</b><br><span style='font-size:11px'>lo abre la caja;<br>sin abrir puertos<br>en casa</span>",
           600, 60, 290, 860, f"fillColor=#fff8ef;strokeColor={NARANJA};dashed=1;verticalAlign=top;fontColor={NARANJA};fontSize=13;")
    cv, ca = VERDE_F, AZUL_F
    xc, xs = 270, 1035

    cliente = actor(d, "Cliente", 70, 300)
    admin = actor(d, "Administrador /<br>técnico", 1420, 330)
    producto = actor(d, "Responsable<br>de producto", 1420, 720)

    c1 = cu(d, "C01-C07 · Usar las apps<br>y navegar sin anuncios", xc, 120, cv)
    c2 = cu(d, "C21 · Primer arranque: pedir<br>sus servicios a la sede", xc, 260, cv)
    c3 = cu(d, "C13-C14 · Recibir apps<br>y actualizaciones", xc, 380, cv)
    c4 = cu(d, "S35 / C15 · Entregar<br>métricas de estado", xc, 500, cv)
    c5 = cu(d, "C18-C20 · Recoger y enviar<br>estadísticas de uso", xc, 640, cv, NUEVO)

    s0 = cu(d, "S11-S14 · Portal: mis cajas,<br>incidencias y estadísticas", xs, 120, ca)
    s1 = cu(d, "S22 + S37 · Pedido y alta<br>automática de la caja", xs, 260, ca)
    s2 = cu(d, "S25 · Actualizar las cajas", xs, 380, ca)
    s3 = cu(d, "S28 · Vigilar las cajas<br>y avisar", xs, 500, ca)
    s4 = cu(d, "S36 · Guardar datos de uso<br>(PostgreSQL)", xs, 640, ca, NUEVO)
    s5 = cu(d, "S31 · Analizar estadísticas<br>(Grafana)", xs, 740, ca, NUEVO)
    s6 = cu(d, "S32 · Mejorar el catálogo", xs, 840, ca, NUEVO)

    d.linea(cliente, c1, "", ASOCIACION)
    d.linea(cliente, s0, "", ASOCIACION + "entryX=0.5;entryY=0;entryDx=0;entryDy=0;", [(87, 50), (1130, 50)])
    for u in (s1, s2, s3):
        d.linea(admin, u, "", ASOCIACION)
    for u in (s5, s6):
        d.linea(producto, u, "", ASOCIACION)

    horizontal = "exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;"
    d.linea(s1, c2, "① primer arranque: la caja pide<br>y recibe sus servicios", FLUJO + horizontal)
    d.linea(s2, c3, "② apps y parches (Ansible)", FLUJO + horizontal)
    d.linea(c4, s3, "③ estado (Prometheus)", FLUJO + "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;")
    d.linea(c5, s4, "④ datos de uso (sin nombres)", FLUJO + "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;")
    inc(d, s5, s4, "usa")
    inc(d, s6, s5, "«extend»")
    d.linea(s6, s2, "⑤ nueva app o ajuste<br>→ vuelve a ②", FLUJO + "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;",
            [(1290, 868), (1290, 408)])
    d.texto("<b>El ciclo de NoSub</b>: al encenderse por primera vez, la caja pide a la sede los servicios de su pedido →  la caja da el servicio en casa → envía su estado y sus datos de uso por el túnel → "
            "la sede los guarda y los analiza → decide mejoras del catálogo → actualiza las cajas.<br>"
            "En el portal (S11-S14) el cliente acepta o retira el envío de sus datos de uso y ve sus propias estadísticas. Las flechas naranjas son lo que viaja por el túnel. Los códigos (S.., C..) son los de los diagramas de la sede y de la caja.",
            200, 940, 1120, 70, "fontSize=12;")
    leyenda(d, 1360, 900, previsto=False)
    return d


if __name__ == "__main__":
    import sys
    destino = sys.argv[1] if len(sys.argv) > 1 else "."
    for nombre, f in [("5-casos-uso-sede", sede_servicios), ("5b-casos-uso-sede-admin", sede_admin), ("6-casos-uso-caja", caja), ("7-casos-uso-conjunto", conjunto)]:
        open(f"{destino}/{nombre}.drawio", "w", encoding="utf8").write(f().xml())
        print(nombre)
