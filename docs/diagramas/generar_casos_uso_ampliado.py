#!/usr/bin/env python3
"""Diagramas 3b y 3c de NoSub: casos de uso del catálogo ampliado de la caja (fase 3).
3b = C22-C31 (primera tanda) · 3c = C32-C51 (segunda tanda).
Uso: python3 -I generar_casos_uso_ampliado.py [destino] → <destino>/6b-casos-uso-caja-ampliado.{drawio,png}
y <destino>/6c-casos-uso-caja-ampliado-2.{drawio,png} (destino por defecto: esta carpeta)."""
import os, subprocess, sys
from html import escape

DEST = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

# Código, caso de uso, app (en el mismo orden que el catálogo de los demás documentos)
APPS_3B = [
    ("C22", "Ver películas y series", "Jellyfin"),
    ("C23", "Escuchar audiolibros y podcasts", "Audiobookshelf"),
    ("C24", "Leer libros y cómics", "Kavita"),
    ("C25", "Leer las noticias de sus webs", "FreshRSS"),
    ("C26", "Guardar enlaces para leer luego", "Linkwarden"),
    ("C27", "Escanear y buscar documentos", "Paperless-ngx"),
    ("C28", "Llevar las cuentas de casa", "Actual Budget"),
    ("C29", "Tomar notas rápidas", "Memos"),
    ("C30", "Controlar luces y sensores de casa", "Home Assistant"),
    ("C31", "Recibir avisos en el móvil", "ntfy"),
]

BASE = "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fontSize=12;"
TEXTO = BASE + "text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;"
ACTOR = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fontSize=12;fontStyle=1;"
FASE1 = BASE + "ellipse;fillColor=#d5e8d4;strokeColor=#555555;fontSize=11;"
FASE3 = BASE + "ellipse;fillColor=#e8eef7;strokeColor=#1f4e79;dashed=1;dashPattern=1 3;strokeWidth=1.5;fontSize=11;fontColor=#1f2d3d;"
LINEA = "endArrow=none;html=1;strokeColor=#444444;"
INCLUDE = "endArrow=open;endSize=10;dashed=1;html=1;strokeColor=#222222;fontSize=10;fontStyle=2;"

# Segunda tanda, agrupada por la categoría de los filtros del portal
APPS_3C = [
    ("Ocio", [("C32", "Emitir en directo", "Owncast"), ("C33", "Jugar a su colección retro", "RomM"),
              ("C34", "Consultar Wikipedia sin Internet", "Kiwix")]),
    ("Fotos, archivos y notas", [("C35", "Escribir la wiki de la familia", "BookStack"),
                                 ("C36", "Editar documentos a la vez", "Docmost")]),
    ("Casa y seguridad", [("C37", "Grabar las cámaras de casa", "Frigate"), ("C38", "Conectar sensores Zigbee", "Zigbee2MQTT"),
                          ("C39", "Controlar la despensa", "Grocy"), ("C40", "Planear el menú y la compra", "Mealie"),
                          ("C41", "Guardar códigos de doble factor", "2FAuth"), ("C42", "Copiar los ordenadores de casa", "UrBackup")]),
    ("Organización", [("C43", "Sincronizar calendario y contactos", "Radicale"), ("C44", "Repartir tareas", "Vikunja"),
                      ("C45", "Llevar las finanzas al detalle", "Firefly III"), ("C46", "Elegir fecha para quedar", "Rallly"),
                      ("C47", "Dibujar en una pizarra", "Excalidraw"), ("C48", "Vigilar cambios de precio", "changedetection.io"),
                      ("C49", "Buscar sin rastreo", "SearXNG"), ("C50", "Traducir textos", "LibreTranslate"),
                      ("C51", "Preguntar a un asistente de IA", "Ollama (experimental)")]),
]

celdas, n = [], [0]
def nuevo():
    celdas.clear()
    n[0] = 0
def cid():
    n[0] += 1
    return f"d{n[0]}"
def caja(valor, estilo, x, y, w, h):
    i = cid()
    celdas.append(f'<mxCell id="{i}" value="{escape(valor)}" style="{estilo}" vertex="1" parent="1">'
                  f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    return i
def flecha(a, b, estilo, valor="", extra=""):
    i = cid()
    celdas.append(f'<mxCell id="{i}" value="{escape(valor)}" style="{estilo}{extra}" edge="1" parent="1" source="{a}" target="{b}">'
                  f'<mxGeometry relative="1" as="geometry"/></mxCell>')

def diagrama_3b():
    nuevo()
    caja("Casos de uso de la caja del cliente: catálogo ampliado (fase 3)", TEXTO + "fontSize=20;fontStyle=1;fontColor=#1f4e79;", 20, 10, 1000, 30)
    caja("<b>Caja NoSub (mini PC en casa del cliente)</b>",
         BASE + "fillColor=none;strokeColor=#2e7d32;strokeWidth=2;verticalAlign=top;align=left;spacingLeft=10;spacingTop=4;fontSize=14;fontColor=#2e7d32;arcSize=2;",
         200, 60, 1000, 960)
    grupo = caja("<b>Apps del catálogo ampliado</b>",
                 BASE + "fillColor=#f7f9fc;strokeColor=#1f4e79;dashed=1;verticalAlign=top;align=center;spacingTop=6;fontSize=12;fontColor=#1f4e79;arcSize=4;",
                 235, 100, 340, 890)
    persona = caja("Persona de<br>la casa", ACTOR, 70, 500, 34, 64)
    tecnico = caja("Técnico de NoSub<br><span style='font-weight:normal'>(a distancia)</span>", ACTOR, 1300, 560, 34, 64)

    ids = {}
    for k, (cod, caso, app) in enumerate(APPS_3B):
        ids[cod] = caja(f"{cod} · {caso}<br><b>{app}</b>", FASE3, 265, 135 + k * 84, 280, 62)
        flecha(persona, ids[cod], LINEA, "", "entryX=0;entryY=0.5;exitX=1;exitY=0.5;")

    c12 = caja("C12 · Iniciar sesión en la app<br><i>(diagrama 3)</i>", FASE1, 760, 330, 250, 62)
    c13 = caja("C13 · Instalar o quitar apps<br>del catálogo <i>(diagrama 3)</i>", FASE1, 760, 560, 250, 62)
    flecha(grupo, c12, INCLUDE, "«include» (todas)", "exitX=1;exitY=0.3;entryX=0;entryY=0.5;")
    flecha(c13, grupo, INCLUDE, "instala la app que pide el cliente", "exitX=0;exitY=0.5;entryX=1;entryY=0.6;")
    flecha(tecnico, c13, LINEA)
    flecha(ids["C31"], ids["C30"], INCLUDE, "«extend»", "exitX=1;exitY=0.5;entryX=1;entryY=0.5;edgeStyle=orthogonalEdgeStyle;curved=1;")

    caja("Fase 3: después de la defensa (desde junio de 2027).<br>Cada app llega ya configurada: usuarios, HTTPS y copia diaria.<br>"
         "Igual que C01-C12, siguen funcionando si la sede no responde.",
         TEXTO + "fontSize=11;fontStyle=2;fontColor=#1f4e79;", 640, 760, 520, 60)
    caja("C31 avisa al móvil cuando pasa algo en casa (C30)<br>o cuando la caja termina una tarea.",
         TEXTO + "fontSize=11;fontStyle=2;", 640, 850, 520, 40)

    # Leyenda
    caja("", BASE + "fillColor=#ffffff;strokeColor=#555555;arcSize=6;", 1230, 1040, 400, 190)
    caja("<b>Leyenda</b>", TEXTO + "fontSize=12;", 1245, 1048, 200, 20)
    caja("", FASE1, 1245, 1080, 80, 30)
    caja("Ya está en el diagrama 3 (fases 1 y 2)", TEXTO + "fontSize=11;", 1340, 1086, 280, 20)
    caja("", FASE3, 1245, 1125, 80, 30)
    caja("Fase 3: catálogo ampliado,<br>después de la defensa", TEXTO + "fontSize=11;", 1340, 1124, 280, 36)
    caja("«include»: siempre lo usa · «extend»: solo a veces<br>Muñeco: persona o sistema que lo usa",
         TEXTO + "fontSize=10;fontColor=#555555;", 1245, 1180, 380, 36)


def leyenda(y0=1040):
    caja("", BASE + "fillColor=#ffffff;strokeColor=#555555;arcSize=6;", 1230, y0, 400, 190)
    caja("<b>Leyenda</b>", TEXTO + "fontSize=12;", 1245, y0 + 8, 200, 20)
    caja("", FASE1, 1245, y0 + 40, 80, 30)
    caja("Ya está en el diagrama 3 (fases 1 y 2)", TEXTO + "fontSize=11;", 1340, y0 + 46, 280, 20)
    caja("", FASE3, 1245, y0 + 85, 80, 30)
    caja("Fase 3: catálogo ampliado,<br>después de la defensa", TEXTO + "fontSize=11;", 1340, y0 + 84, 280, 36)
    caja("«include»: siempre lo usa · «extend»: solo a veces<br>Muñeco: persona o sistema que lo usa",
         TEXTO + "fontSize=10;fontColor=#555555;", 1245, y0 + 140, 380, 36)


def diagrama_3c():
    nuevo()
    caja("Casos de uso de la caja del cliente: catálogo ampliado, segunda tanda (fase 3)", TEXTO + "fontSize=20;fontStyle=1;fontColor=#1f4e79;", 20, 10, 1200, 30)
    caja("<b>Caja NoSub (mini PC en casa del cliente)</b>",
         BASE + "fillColor=none;strokeColor=#2e7d32;strokeWidth=2;verticalAlign=top;align=left;spacingLeft=10;spacingTop=4;fontSize=14;fontColor=#2e7d32;arcSize=2;",
         200, 60, 1190, 960)
    grupo = caja("<b>Apps del catálogo ampliado (C32-C51)</b>",
                 BASE + "fillColor=#f7f9fc;strokeColor=#1f4e79;dashed=1;verticalAlign=top;align=center;spacingTop=6;fontSize=12;fontColor=#1f4e79;arcSize=3;",
                 235, 100, 700, 890)
    persona = caja("Persona de<br>la casa", ACTOR, 70, 500, 34, 64)
    tecnico = caja("Técnico de NoSub<br><span style='font-weight:normal'>(a distancia)</span>", ACTOR, 1440, 560, 34, 64)
    columnas = [(260, APPS_3C[:3]), (610, APPS_3C[3:])]
    for x, grupos in columnas:
        y = 132
        for categoria, apps in grupos:
            caja(f"<b>{categoria}</b>", TEXTO + "fontSize=11;fontColor=#1f4e79;align=center;", x, y, 300, 20)
            y += 24
            for cod, caso, app in apps:
                caja(f"{cod} · {caso}<br><b>{app}</b>", FASE3, x, y, 300, 56)
                y += 66
            y += 6
    flecha(persona, grupo, LINEA, "usa las 20 apps", "exitX=1;exitY=0.5;entryX=0;entryY=0.45;")
    c12 = caja("C12 · Iniciar sesión en la app<br><i>(diagrama 3)</i>", FASE1, 1100, 300, 250, 62)
    c13 = caja("C13 · Instalar o quitar apps<br>del catálogo <i>(diagrama 3)</i>", FASE1, 1100, 560, 250, 62)
    flecha(grupo, c12, INCLUDE, "«include» (todas)", "exitX=1;exitY=0.24;entryX=0;entryY=0.5;")
    flecha(c13, grupo, INCLUDE, "instala la app<br>que pide el cliente", "exitX=0;exitY=0.5;entryX=1;entryY=0.53;")
    flecha(tecnico, c13, LINEA)
    caja("Fase 3: después de la defensa.<br>NoSub las ofrecerá a medida que las pruebe,<br>empezando por las más pedidas.<br><br>"
         "C37 (Frigate) y C48 (changedetection.io) avisan<br>al móvil con C31 (ntfy, diagrama 3b).<br><br>"
         "C51 (Ollama) es experimental: en el mini PC<br>va lento y solo con modelos pequeños.",
         TEXTO + "fontSize=11;fontStyle=2;fontColor=#1f4e79;", 990, 700, 380, 180)
    leyenda()


def guardar(nombre, titulo):
    xml = (f'<mxfile host="drawio" agent="nosub-infra"><diagram name="{titulo}">'
           '<mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
           'page="0" pageScale="1" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
           + "".join(celdas) + "</root></mxGraphModel></diagram></mxfile>")
    ruta = f"{DEST}/{nombre}.drawio"
    open(ruta, "w", encoding="utf8").write(xml)
    subprocess.run(["xvfb-run", "-a", "drawio", "--no-sandbox", "-x", "-f", "png", "-s", "2", "-b", "20",
                    "-o", ruta.replace(".drawio", ".png"), ruta], check=True, capture_output=True)
    print(ruta.replace(".drawio", ".png"), os.path.exists(ruta.replace(".drawio", ".png")))


diagrama_3b()
guardar("6b-casos-uso-caja-ampliado", "Casos de uso · Caja (catálogo ampliado)")
diagrama_3c()
guardar("6c-casos-uso-caja-ampliado-2", "Casos de uso · Caja (catálogo ampliado, segunda tanda)")
