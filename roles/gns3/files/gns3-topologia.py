#!/usr/bin/env python3
"""Monta en GNS3 la topología de un fichero JSON (lo genera Ansible, rol gns3) y la arranca.

Uso:  gns3-topologia.py TOPOLOGIA.json    (variables GNS3_USUARIO y GNS3_CLAVE)
Si el proyecto ya existe con la misma "huella" (la topología y los ficheros de cada equipo), solo lo arranca si
estaba parado. Si algo ha cambiado, lo borra y lo vuelve a montar: el ensayo no guarda datos propios.
Imprime CAMBIADO o SIN CAMBIOS en la última línea.
"""
import base64, hashlib, json, os, shutil, sys, urllib.error, urllib.request

API = "http://127.0.0.1:3080/v2"
CAMPO_HUELLA = "huella_nosub"


def api(metodo, ruta, datos=None):
    pet = urllib.request.Request(API + ruta, method=metodo, data=None if datos is None else json.dumps(datos).encode())
    pet.add_header("Content-Type", "application/json")
    cred = base64.b64encode(f'{os.environ["GNS3_USUARIO"]}:{os.environ["GNS3_CLAVE"]}'.encode()).decode()
    pet.add_header("Authorization", "Basic " + cred)
    try:
        with urllib.request.urlopen(pet, timeout=120) as r:
            cuerpo = r.read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"GNS3 respondió {e.code} a {metodo} {ruta}: {e.read().decode(errors='replace')[:500]}")
    return json.loads(cuerpo) if cuerpo else None


def huella(esp):
    h = hashlib.sha256(json.dumps(esp, sort_keys=True).encode())
    for n in esp["nodos"]:
        d = n.get("ficheros")
        if d:
            for f in sorted(os.listdir(d)):
                h.update(f.encode()); h.update(open(os.path.join(d, f), "rb").read())
    return h.hexdigest()


def crear_nodo(pid, n):
    base = {"name": n["nombre"], "compute_id": "local", "x": n["x"], "y": n["y"]}
    if n["tipo"] == "docker":
        base.update(node_type="docker", properties={
            "image": n["imagen"], "adapters": n["adaptadores"], "console_type": "none",
            "start_command": "sh /etc/nosub/arranque.sh", "extra_volumes": ["/etc/nosub"]})
    elif n["tipo"] == "switch":
        base.update(node_type="ethernet_switch", properties={"ports_mapping": [
            {"name": f'Ethernet{p["n"]}', "port_number": p["n"], "type": p["tipo"], "vlan": p["vlan"], "ethertype": ""}
            for p in n["puertos"]]})
    elif n["tipo"] == "cloud":
        base.update(node_type="cloud", properties={"ports_mapping": [
            {"interface": n["interfaz"], "name": n["interfaz"], "port_number": 0, "type": "ethernet"}]})
    nodo = api("POST", f"/projects/{pid}/nodes", base)
    if n["tipo"] == "docker":
        # Los ficheros del equipo van a su carpeta persistente /etc/nosub (GNS3 la monta en el contenedor)
        destino = os.path.join(nodo["node_directory"], "etc", "nosub")
        os.makedirs(destino, exist_ok=True)
        for f in os.listdir(n["ficheros"]):
            shutil.copy(os.path.join(n["ficheros"], f), destino)
        os.system(f'chown -R gns3:gns3 "{nodo["node_directory"]}"')
    return nodo["node_id"]


def main():
    esp = json.load(open(sys.argv[1]))
    hu = huella(esp)
    proyecto = next((p for p in api("GET", "/projects") if p["name"] == esp["proyecto"]), None)
    if proyecto:
        if proyecto["status"] != "opened":
            proyecto = api("POST", f'/projects/{proyecto["project_id"]}/open')
        actual = {v["name"]: v.get("value") for v in proyecto.get("variables") or []}.get(CAMPO_HUELLA)
        if actual == hu:
            nodos = api("GET", f'/projects/{proyecto["project_id"]}/nodes')
            if len(nodos) != len(esp["nodos"]):
                actual = None   # a medio montar: se vuelve a montar
        if actual == hu:
            if all(n["status"] == "started" for n in nodos):
                print("SIN CAMBIOS")
                return
            api("POST", f'/projects/{proyecto["project_id"]}/nodes/start')
            print("Proyecto arrancado\nCAMBIADO")
            return
        api("DELETE", f'/projects/{proyecto["project_id"]}')
    pid = api("POST", "/projects", {"name": esp["proyecto"]})["project_id"]
    ids = {n["nombre"]: crear_nodo(pid, n) for n in esp["nodos"]}
    for a, b in esp["enlaces"]:
        api("POST", f"/projects/{pid}/links", {"nodes": [
            {"node_id": ids[x[0]], "adapter_number": x[1], "port_number": x[2]} for x in (a, b)]})
    api("POST", f"/projects/{pid}/nodes/start")
    # La huella se guarda al final: si algo falla a medias, la próxima vez se vuelve a montar
    api("PUT", f"/projects/{pid}", {"variables": [{"name": CAMPO_HUELLA, "value": hu}]})
    print(f"Proyecto montado ({len(ids)} equipos, {len(esp['enlaces'])} enlaces)\nCAMBIADO")


if __name__ == "__main__":
    main()
