"""Portal de clientes de NoSub (extranet): el cliente ve sus cajas y abre incidencias."""
import os
import secrets
from functools import wraps

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash

from bd import conectar

app = Flask(__name__, template_folder="plantillas", static_folder="estatico")
# Delante está Traefik: de él se toma la dirección y el esquema (https) reales del visitante
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
app.config.update(
    SECRET_KEY=os.environ["PORTAL_SECRETO"],
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=os.environ.get("PORTAL_COOKIE_SEGURA", "1") == "1",   # la cookie solo viaja por HTTPS
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=8 * 3600,
)
EMPRESA = os.environ.get("PORTAL_EMPRESA", "NoSub")

# Hash de una contraseña que no existe: así "usuario no existe" tarda lo mismo que "contraseña mal"
HASH_FALSO = "scrypt:32768:8:1$x$" + "0" * 128
# Fuerza bruta: tras MAX_FALLOS intentos fallidos en BLOQUEO, el usuario queda bloqueado hasta que pase BLOQUEO.
# Cuenta igual exista o no el usuario (así no se puede saber qué usuarios hay). Traefik limita además por IP.
MAX_FALLOS = int(os.environ.get("PORTAL_MAX_FALLOS", "5"))
BLOQUEO = os.environ.get("PORTAL_BLOQUEO", "15 minutes")


@app.context_processor
def comunes():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return {"empresa": EMPRESA, "csrf": session["csrf"], "cliente": g.get("cliente")}


@app.before_request
def antes():
    # Todos los formularios llevan el token de la sesión (protección CSRF)
    if request.method == "POST" and request.form.get("csrf") != session.get("csrf"):
        abort(400)
    g.cliente = None
    if "cliente_id" in session:
        with conectar() as con:
            g.cliente = con.execute("SELECT id, usuario, nombre, correo FROM clientes WHERE id = %s",
                                    (session["cliente_id"],)).fetchone()
        if g.cliente is None:
            session.clear()


def con_sesion(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if g.cliente is None:
            return redirect(url_for("entrar"))
        return vista(*args, **kwargs)
    return envoltura


@app.after_request
def cabeceras(respuesta):
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["X-Frame-Options"] = "DENY"
    respuesta.headers["Referrer-Policy"] = "same-origin"
    respuesta.headers["Content-Security-Policy"] = "default-src 'self'"
    return respuesta


@app.get("/salud")
def salud():
    with conectar() as con:
        con.execute("SELECT 1")
    return "ok\n"


@app.get("/privacidad")
def privacidad():
    return render_template("privacidad.html")


@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()[:100]
        with conectar() as con:
            fallos = con.execute("SELECT count(*) AS n FROM intentos_fallidos WHERE usuario = %s AND cuando > now() - %s::interval",
                                 (usuario, BLOQUEO)).fetchone()["n"]
            if fallos >= MAX_FALLOS:
                flash("Demasiados intentos fallidos. Espera unos minutos y vuelve a probar.")
                return render_template("entrar.html"), 429
            fila = con.execute("SELECT id, clave_hash FROM clientes WHERE usuario = %s", (usuario,)).fetchone()
            if check_password_hash(fila["clave_hash"] if fila else HASH_FALSO, request.form.get("clave", "")) and fila:
                con.execute("DELETE FROM intentos_fallidos WHERE usuario = %s", (usuario,))
                session.clear()
                session.permanent = True
                session["cliente_id"] = fila["id"]
                return redirect(url_for("panel"))
            con.execute("INSERT INTO intentos_fallidos (usuario, ip) VALUES (%s, %s)", (usuario, request.remote_addr))
            con.execute("DELETE FROM intentos_fallidos WHERE cuando < now() - interval '1 day'")   # no se guardan más de un día
        flash("Usuario o contraseña incorrectos.")
    return render_template("entrar.html")


@app.post("/salir")
def salir():
    session.clear()
    return redirect(url_for("entrar"))


@app.get("/")
@con_sesion
def panel():
    with conectar() as con:
        cajas = con.execute(
            "SELECT id, nombre, host(ip_vpn) AS ip_vpn, red, servicios, ultima_conexion"
            " FROM cajas WHERE cliente_id = %s ORDER BY nombre", (g.cliente["id"],)).fetchall()
        incidencias = con.execute(
            "SELECT i.id, i.asunto, i.estado, i.creada, c.nombre AS caja FROM incidencias i"
            " LEFT JOIN cajas c ON c.id = i.caja_id WHERE i.cliente_id = %s ORDER BY i.creada DESC",
            (g.cliente["id"],)).fetchall()
    return render_template("panel.html", cajas=cajas, incidencias=incidencias)


@app.route("/incidencias/nueva", methods=["GET", "POST"])
@con_sesion
def incidencia_nueva():
    with conectar() as con:
        cajas = con.execute("SELECT id, nombre FROM cajas WHERE cliente_id = %s ORDER BY nombre",
                            (g.cliente["id"],)).fetchall()
        if request.method == "POST":
            asunto = request.form.get("asunto", "").strip()[:200]
            detalle = request.form.get("detalle", "").strip()[:5000]
            caja = request.form.get("caja", type=int)
            if caja not in {c["id"] for c in cajas}:
                caja = None
            if asunto and detalle:
                con.execute("INSERT INTO incidencias (cliente_id, caja_id, asunto, detalle) VALUES (%s, %s, %s, %s)",
                            (g.cliente["id"], caja, asunto, detalle))
                flash("Incidencia enviada. Te responderemos lo antes posible.")
                return redirect(url_for("panel"))
            flash("Escribe el asunto y el detalle.")
    return render_template("incidencia_nueva.html", cajas=cajas)
