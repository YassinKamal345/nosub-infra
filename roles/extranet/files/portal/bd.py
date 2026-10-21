"""Conexión con PostgreSQL y tablas del portal de clientes."""
import os

import psycopg
from psycopg.rows import dict_row

TABLAS = """
CREATE TABLE IF NOT EXISTS clientes (
    id          serial PRIMARY KEY,
    usuario     text UNIQUE NOT NULL,
    nombre      text NOT NULL,
    correo      text NOT NULL,
    clave_hash  text NOT NULL,
    creado      timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS cajas (
    id          serial PRIMARY KEY,
    cliente_id  integer NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    nombre      text UNIQUE NOT NULL,
    ip_vpn      inet NOT NULL,
    red         cidr NOT NULL,
    servicios   text[] NOT NULL DEFAULT '{}',
    ultima_conexion timestamptz            -- la rellenará la monitorización de las cajas (fase 4)
);
CREATE TABLE IF NOT EXISTS incidencias (
    id          serial PRIMARY KEY,
    cliente_id  integer NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    caja_id     integer REFERENCES cajas(id) ON DELETE SET NULL,
    asunto      text NOT NULL,
    detalle     text NOT NULL,
    estado      text NOT NULL DEFAULT 'abierta' CHECK (estado IN ('abierta', 'en curso', 'cerrada')),
    creada      timestamptz NOT NULL DEFAULT now()
);
"""


def conectar():
    return psycopg.connect(
        host=os.environ["PORTAL_BD_HOST"],
        dbname=os.environ["PORTAL_BD_NOMBRE"],
        user=os.environ["PORTAL_BD_USUARIO"],
        password=os.environ["PORTAL_BD_CLAVE"],
        connect_timeout=5,
        row_factory=dict_row,
    )
