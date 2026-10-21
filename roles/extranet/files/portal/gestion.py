"""Tareas de Ansible sobre la base de datos del portal. Escribe CAMBIO si ha cambiado algo.

  gestion.py tablas                 crea las tablas que falten
  gestion.py cliente '<json>'       crea o actualiza un cliente y sus cajas
                                    (contraseña en la variable PORTAL_CLAVE_CLIENTE)
"""
import json
import os
import sys

from werkzeug.security import check_password_hash, generate_password_hash

from bd import TABLAS, conectar


def tablas(con):
    antes = con.execute("SELECT count(*) AS n FROM pg_tables WHERE schemaname = 'public'").fetchone()["n"]
    con.execute(TABLAS)
    despues = con.execute("SELECT count(*) AS n FROM pg_tables WHERE schemaname = 'public'").fetchone()["n"]
    return despues != antes


def cliente(con, datos):
    clave = os.environ["PORTAL_CLAVE_CLIENTE"]
    cambio = False
    fila = con.execute("SELECT * FROM clientes WHERE usuario = %s", (datos["usuario"],)).fetchone()
    if fila is None:
        fila = con.execute(
            "INSERT INTO clientes (usuario, nombre, correo, clave_hash) VALUES (%s, %s, %s, %s) RETURNING *",
            (datos["usuario"], datos["nombre"], datos["correo"], generate_password_hash(clave)),
        ).fetchone()
        cambio = True
    else:
        if (fila["nombre"], fila["correo"]) != (datos["nombre"], datos["correo"]):
            con.execute("UPDATE clientes SET nombre = %s, correo = %s WHERE id = %s",
                        (datos["nombre"], datos["correo"], fila["id"]))
            cambio = True
        # La contraseña solo se cambia si ya no coincide con la del Vault
        if not check_password_hash(fila["clave_hash"], clave):
            con.execute("UPDATE clientes SET clave_hash = %s WHERE id = %s", (generate_password_hash(clave), fila["id"]))
            cambio = True

    for caja in datos.get("cajas", []):
        nueva = (fila["id"], caja["ip_vpn"], caja["red"], caja["servicios"])
        actual = con.execute(
            "SELECT cliente_id, host(ip_vpn) AS ip_vpn, red::text AS red, servicios FROM cajas WHERE nombre = %s",
            (caja["nombre"],),
        ).fetchone()
        if actual is None:
            con.execute("INSERT INTO cajas (nombre, cliente_id, ip_vpn, red, servicios) VALUES (%s, %s, %s, %s, %s)",
                        (caja["nombre"], *nueva))
            cambio = True
        elif tuple(actual.values()) != nueva:
            con.execute("UPDATE cajas SET cliente_id = %s, ip_vpn = %s, red = %s, servicios = %s WHERE nombre = %s",
                        (*nueva, caja["nombre"]))
            cambio = True
    return cambio


def main():
    orden = sys.argv[1] if len(sys.argv) > 1 else ""
    with conectar() as con:
        if orden == "tablas":
            cambio = tablas(con)
        elif orden == "cliente" and len(sys.argv) == 3:
            cambio = cliente(con, json.loads(sys.argv[2]))
        else:
            sys.exit(__doc__)
    print("CAMBIO" if cambio else "IGUAL")


if __name__ == "__main__":
    main()
