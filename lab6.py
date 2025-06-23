import yaml
import requests
# ==== CLASES BASE ====
class Alumno:
    def __init__(self, nombre, codigo, mac):
        self.nombre = nombre
        self.codigo = codigo
        self.mac = mac

class Servicio:
    def __init__(self, nombre, protocolo, puerto):
        self.nombre = nombre
        self.protocolo = protocolo
        self.puerto = puerto

class Servidor:
    def __init__(self, nombre, ip, servicios):
        self.nombre = nombre
        self.ip = ip
        self.servicios = servicios

class Curso:
    def __init__(self, codigo, estado, nombre, alumnos, servidores):
        self.codigo = codigo
        self.estado = estado
        self.nombre = nombre
        self.alumnos = alumnos
        self.servidores = servidores

# ==== FUNCIÓNES====
def importar_datos(archivo):
    with open(archivo, 'r') as file:
        data = yaml.safe_load(file)

    alumnos = [Alumno(a["nombre"], a["codigo"], a["mac"]) for a in data.get("alumnos", [])]

    servidores = []
    for s in data.get("servidores", []):
        servicios = [Servicio(sv["nombre"], sv["protocolo"], sv["puerto"]) for sv in s.get("servicios", [])]
        servidores.append(Servidor(s["nombre"], s["ip"], servicios))

    cursos = []
    for c in data.get("cursos", []):
        cursos.append(Curso(
            c["codigo"],
            c["estado"],
            c["nombre"],
            c.get("alumnos", []),
            c.get("servidores", [])
        ))

    return alumnos, servidores, cursos

def exportar_datos(archivo_path):
    with open(archivo_path, 'w') as file:
        yaml.dump({
            "alumnos": [
                {"nombre": a.nombre, "codigo": a.codigo, "mac": a.mac}
                for a in datos_cargados["alumnos"]
            ],
            "servidores": [
                {
                    "nombre": s.nombre,
                    "ip": s.ip,
                    "servicios": [
                        {"nombre": sv.nombre, "protocolo": sv.protocolo, "puerto": sv.puerto}
                        for sv in s.servicios
                    ]
                }
                for s in datos_cargados["servidores"]
            ],
            "cursos": [
                {
                    "codigo": c.codigo,
                    "estado": c.estado,
                    "nombre": c.nombre,
                    "alumnos": c.alumnos,
                    "servidores": c.servidores
                }
                for c in datos_cargados["cursos"]
            ]
        }, file, default_flow_style=False)

def listar_cursos(cursos):
    if not cursos:
        print("No hay cursos registrados.")
        return

    print("\nLista de cursos:")
    for curso in cursos:
        print(f"- Código: {curso.codigo}")
        print(f"  Nombre: {curso.nombre}")
        print(f"  Estado: {curso.estado}")
        print(f"  # Alumnos: {len(curso.alumnos)}")
        print(f"  # Servidores: {len(curso.servidores)}")
        print("-" * 30)

def mostrar_detalle_curso(cursos, alumnos, servidores):
    codigo = input("Ingrese el código del curso: ").strip()

    # Buscamos curso por código
    for curso in cursos:
        if curso.codigo == codigo:
            print(f"\n→ Curso: {curso.nombre} ({curso.codigo})")
            print(f"→ Estado: {curso.estado}")

            # Mostramos alumnos del curso
            print("\n→ Alumnos:")
            for cod in curso.alumnos:
                for alumno in alumnos:
                    if str(alumno.codigo) == str(cod):
                        print(f"  - {alumno.nombre} ({alumno.codigo})")

            # Mostramos servidores del curso

            print("\n→ Servidores y servicios permitidos:")
            for s in curso.servidores:
                for sv in servidores:
                    if sv.nombre == s["nombre"]:
                        print(f"  - {sv.nombre} ({sv.ip})")
                        servicios = s.get("servicios_permitidos", [])
                        print(f"    Servicios: {', '.join(servicios)}")
            return

    print("Curso no encontrado.")

def actualizar_curso(cursos, alumnos):
    codigo = input("Ingrese el código del curso a actualizar: ").strip()
    
    # Buscmos el curso
    curso_encontrado = None
    for curso in cursos:
        if curso.codigo == codigo:
            curso_encontrado = curso
            break

    if not curso_encontrado:
        print("Curso no encontrado.")
        return

    print(f"\nCurso seleccionado: {curso_encontrado.nombre} ({curso_encontrado.codigo})")
    print("1) Agregar alumno")
    print("2) Quitar alumno")
    opcion = input("Seleccione opción: ")

    if opcion == "1":
        cod_alumno = input("Ingrese código del alumno a agregar: ").strip()

        # Verificamos si ya está matriculado
        if cod_alumno in [str(c) for c in curso_encontrado.alumnos]:
            print("→ El alumno ya está matriculado.")
            return

        # Verificamo si el alumno existe
        existe = any(str(a.codigo) == cod_alumno for a in alumnos)
        if not existe:
            print("→ El alumno no existe.")
            return

        # Agregamos el alumno
        curso_encontrado.alumnos.append(cod_alumno)
        print("→ Alumno agregado correctamente.")

    elif opcion == "2":
        cod_alumno = input("Ingrese código del alumno a quitar: ").strip()

        # Verificamos si está en el curso
        if cod_alumno not in [str(c) for c in curso_encontrado.alumnos]:
            print("→ El alumno no está en el curso.")
            return

        # remueve el alumno
        curso_encontrado.alumnos.remove(cod_alumno)
        print("→ Alumno removido correctamente.")
    
    else:
        print("Opción inválida.")



def listar_alumnos(alumnos):
    if not alumnos:
        print("No hay alumnos registrados.")
        return

    print("\nListado de Alumnos:")
    for alumno in alumnos:
        # Mostramos nombre, código y MAC de cada alumno
        print(f"- Nombre: {alumno.nombre}")
        print(f"  Código: {alumno.codigo}")
        print(f"  MAC:    {alumno.mac}")
        

def mostrar_detalle_alumno(alumnos):
    codigo = input("Ingrese el código del alumno: ").strip()

    for alumno in alumnos:
        if str(alumno.codigo) == codigo:
            print("\n→ Detalle del Alumno:")
            print(f"  Nombre : {alumno.nombre}")
            print(f"  Código : {alumno.codigo}")
            print(f"  MAC    : {alumno.mac}")
            return

    print("Alumno no encontrado.")

def es_alumno_autorizado(mac, servicio_nombre, servidor_nombre, alumnos, cursos):
    # Buscamos al alumno por su MAC
    alumno = next((a for a in alumnos if a.mac == mac), None)
    if not alumno:
        print("No se encontró a un alumno con esa MAC.")
        return False

    for curso in cursos:
        if curso.estado != "DICTANDO":
            continue

        # Verificamos si el alumno está matriculado en este curso
        if str(alumno.codigo) not in [str(c) for c in curso.alumnos]:
            continue

        # Verificamos si el servidor está en el curso
        for s in curso.servidores:
            if s["nombre"] == servidor_nombre:
                if servicio_nombre in s.get("servicios_permitidos", []):
                    return True  #  Cumple todo

    ##print("El alumno no está autorizado para acceder a ese servicio.")
    return False

def get_attachment_points(mac_address):
    controller_ip = '10.20.12.209'  
    url = f"http://{controller_ip}:8080/wm/device/?mac={mac_address}"
    headers = {'Accept': 'application/json'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        dispositivos = response.json()
        if dispositivos and 'attachmentPoint' in dispositivos[0]:
            ap = dispositivos[0]['attachmentPoint'][0]
            return ap['switchDPID'], ap['port']
        else:
            print("No se encontró punto de conexión para esa MAC.")
            return None, None
    else:
        print("Error", response.status_code)
        return None, None

def crear_conexion(alumno_mac, servicio_nombre, servidor_nombre, alumnos, cursos, servidores):
    # P1 Validamos si el alumno está autorizado
    autorizado = es_alumno_autorizado(alumno_mac, servicio_nombre, servidor_nombre, alumnos, cursos)
    if not autorizado:
        print("El alumno no está autorizado para acceder a este servicio.")
        return

    # P2 Obtenemos  el punto de conexión (switch y puerto) para el alumno
    alumno_dpid, alumno_port = get_attachment_points(alumno_mac)
    if not alumno_dpid:
        print("No se pudo encontrar el punto de conexión del alumno.")
        return

    # P3 Obtenemos el punto de conexión (switch y puerto) para el servidor
    servidor = next((s for s in servidores if s.nombre == servidor_nombre), None)
    if not servidor:
        print(f"Servidor {servidor_nombre} no encontrado.")
        return

    # Obtenemos el servicio solicitado en el servidor
    servicio = next((sv for sv in servidor.servicios if sv.nombre == servicio_nombre), None)
    if not servicio:
        print(f"Servicio {servicio_nombre} no encontrado en {servidor_nombre}.")
        return

    # Obtenemmos ek punto de conexión del servidor (su IP)
    ##servidor_dpid, servidor_port = get_attachment_points(servidor.ip)
    servidor_dpid, servidor_port = get_attachment_by_ip(servidor.ip)

    if not servidor_dpid:
        print("No se pudo encontrar el punto de conexión del servidor.")
        return

    # P4 Obtenemmos la ruta entre el alumno y el servidor
    ruta = get_route(alumno_dpid, alumno_port, servidor_dpid, servidor_port)
    if not ruta:
        print("No se pudo calcular la ruta entre el alumno y el servidor.")
        return

    # P5 Insetamos los flujos necesarios en los switches (usaeremos staticflowpusher)
    ip_alumno = obtener_ip_por_mac(alumno_mac)
    if not ip_alumno:
        print("No se pudo obtener la IP del alumno.")
        return
    
    ##build_route(ruta, alumno_mac, servicio, servidor_ip=servidor.ip)
    build_route(ruta, ip_alumno, servicio, servidor_ip=servidor.ip)

    print(f"→ Ruta entre {alumno_mac} y {servidor_nombre} con servicio {servicio_nombre} instalada correctamente.")


def get_attachment_by_ip(ip_address):
    controller_ip = '10.20.12.209'
    url = f"http://{controller_ip}:8080/wm/device/"
    headers = {'Accept': 'application/json'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        dispositivos = response.json()
        for dev in dispositivos:
            if ip_address in dev.get('ipv4', []):
                if 'attachmentPoint' in dev and dev['attachmentPoint']:
                    ap = dev['attachmentPoint'][0]
                    return ap['switchDPID'], ap['port']
        print(f"No se encontró punto de conexión para la IP {ip_address}")
        return None, None
    else:
        print("Error", response.status_code)
        return None, None



def build_route(ruta, ip_alumno, servicio, servidor_ip):
    controller_ip = '10.20.12.209'

    for switch, port in ruta:
        try:
            # Obtenemos el número de puerto 
            in_port = port['portNumber'] if isinstance(port, dict) and 'portNumber' in port else port
            if not isinstance(in_port, int):
                print(f"Puerto inválido: {in_port}")
                continue

            # Generamos un nombre  del flujo por switch
            flow_name = f"flow-{switch.replace(':', '')}-{ip_alumno.replace('.', '-')}-{servidor_ip.replace('.', '-')}"
            
            flow = {
                "switch": switch,
                "name": flow_name,
                "cookie": "0",
                "priority": "32768",
                "in_port": in_port,
                "eth_type": "0x0800",
                "ipv4_src": ip_alumno,
                "ipv4_dst": servidor_ip,
                "protocol": servicio.protocolo.upper(),
                "tp_dst": servicio.puerto,
                "actions": f"output={in_port}"
            }

            url = f"http://{controller_ip}:8080/wm/staticflowpusher/json"
            headers = {'Content-Type': 'application/json'}

            response = requests.post(url, json=flow, headers=headers)

            if response.status_code == 200:
                print(f"Flujo insertado en {switch}, puerto {in_port} (nombre: {flow_name})")
            else:
                print(f"Error al insertar flujo en {switch}, código: {response.status_code}")
        except Exception as e:
            print(f"Except {switch}: {str(e)}")



def listar_conexiones():
    controller_ip = '10.20.12.209'
    url = f"http://{controller_ip}:8080/wm/staticflowpusher/list/all/json"
    headers = {'Accept': 'application/json'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        flujos = response.json()
        if not flujos:
            print("No hay conexiones activas (flows) registradas.")
            return

        print("\nListado de conexiones activas (flows):")
        for switch, flows in flujos.items():
            print(f"\nSwitch: {switch}")
            for flow in flows:
                name = flow.get("name", "N/A")
                ipv4_src = flow.get("ipv4_src", "N/A")
                ipv4_dst = flow.get("ipv4_dst", "N/A")
                tp_dst = flow.get("tp_dst", "N/A")
                action = flow.get("actions", "N/A")
                print(f" - Flow: {name}")
                print(f"   De: {ipv4_src}  →  {ipv4_dst}")
                print(f"   Puerto destino: {tp_dst}, Acción: {action}")
    else:
        print(f"Error al obtener la lista de flows: {response.status_code}")

def obtener_ip_por_mac(mac_address):
    controller_ip = '10.20.12.209'
    url = f"http://{controller_ip}:8080/wm/device/?mac={mac_address}"
    headers = {'Accept': 'application/json'}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        dispositivos = response.json()
        if dispositivos and 'ipv4' in dispositivos[0] and dispositivos[0]['ipv4']:
            return dispositivos[0]['ipv4'][0]
        else:
            print("No se encontró IP para esa MAC.")
            return None
    else:
        print("Error al consultar IP:", response.status_code)
        return None


def eliminar_conexion(alumno_mac, servidor_ip):
    controller_ip = '10.20.12.209'
    flow_name = f"flow-{alumno_mac}-{servidor_ip}"

    url = f"http://{controller_ip}:8080/wm/staticflowpusher/json"
    payload = {"name": flow_name}
    headers = {'Content-Type': 'application/json'}

    response = requests.delete(url, json=payload, headers=headers)

    if response.status_code == 200:
        print(f"Conexión eliminada exitosamente: {flow_name}")
    else:
        print(f"Error al eliminar la conexión: {response.status_code}")


def get_route(src_dpid, src_port, dst_dpid, dst_port):
    controller_ip = '10.20.12.209'
    url = f"http://{controller_ip}:8080/wm/topology/route/{src_dpid}/{src_port}/{dst_dpid}/{dst_port}/json"
    headers = {'Accept': 'application/json'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        route = [(hop['switch'], hop['port']) for hop in data]
        ##print(f"Ruta calculada: {route}")

        return route
    else:
        print("Error", response.status_code)
        return []

def listar_servidores(servidores):
    if not servidores:
        print("No hay servidores registrados.")
        return

    print("\nListado de Servidores:")
    for servidor in servidores:
        print(f"- Nombre: {servidor.nombre}")
        print(f"  IP:     {servidor.ip}")
        ##print("  Servicios:")
        ##for servicio in servidor.servicios:
            # Mostramos nombre, protocolo y puerto de cada servicio
          ##  print(f"    - {servicio.nombre} ({servicio.protocolo}, puerto {servicio.puerto})")
        print("--------------------------------------")

def mostrar_detalle_servidor(servidores):
    nombre = input("Ingrese el nombre del servidor: ").strip()

    for servidor in servidores:
        if servidor.nombre.lower() == nombre.lower(): ##para que no sea tan sensible a las mayusculas y minusculas
        ##if str(servidor.nombre) == nombre:
            print(f"\n→{servidor.nombre}")
            print(f"  IP: {servidor.ip}")
            print("  Servicios:")
            for servicio in servidor.servicios:
                print(f"    - {servicio.nombre} ({servicio.protocolo}, puerto {servicio.puerto})")
            return

    print("Servidor no encontrado.")

def listar_cursos_con_servicio_en_servidor(cursos):
    servicio = input("Ingrese el nombre del servicio (ej: ssh): ").strip()
    servidor_nombre = input("Ingrese el nombre del servidor (ej: Servidor 1): ").strip()

    encontrados = False
    print(f"\nCursos con acceso a '{servicio}' en el servidor '{servidor_nombre}':")
    for curso in cursos:
        for servidor in curso.servidores:
            if servidor["nombre"] == servidor_nombre:
                if servicio in servidor.get("servicios_permitidos", []):
                    print(f"- {curso.nombre} ({curso.codigo})")
                    encontrados = True
    if not encontrados:
        print("→ No se encontraron cursos con ese servicio en ese servidor.")


def mostrar_menu_principal():
    print("######################################")
    print("Network Policy Manager de la UPSM")
    print("######################################")
    print("1) Importar")
    print("2) Exportar")
    print("3) Cursos")
    print("4) Alumnos")
    print("5) Servidores")
    print("6) Políticas")
    print("7) Conexiones")
    print("0) Salir")

datos_cargados = None

def importar():
    global datos_cargados
    archivo = input("Ingrese nombre de archivo YAML (ej: datos.yaml): ")
    try:
        alumnos, servidores, cursos = importar_datos(archivo)
        datos_cargados = {
            "alumnos": alumnos,
            "servidores": servidores,
            "cursos": cursos
        }
        print("Archivo importado exitosamente.")
        print(f"Alumnos: {len(alumnos)}, Servidores: {len(servidores)}, Cursos: {len(cursos)}")
    except Exception as e:
        print(" Error al importar:", str(e))

def menu():
    while True:
        mostrar_menu_principal()
        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            print("\n[IMPORTAR]")
            importar()

        elif opcion == "2":
            print("\n[EXPORTAR]")
            archivo = input("Ingrese nombre de archivo YAML para exportar: ")
            exportar_datos(archivo)
            print("Archivo exportado correctamente.")

        elif opcion == "3":
            while True:
                print("\n[CURSOS]")
                print("1) Listar cursos")
                print("2) Mostrar detalle de un curso")
                print("3) Actualizar (agregar/quitar alumno)")
                print("4) Buscar cursos con acceso a un servicio y servidor")

                print("0) Volver al menú principal")

                sub_op = input("Seleccione opción: ")

                if sub_op == "1":
                    if datos_cargados:
                        listar_cursos(datos_cargados["cursos"])
                    else:
                        print("Primero debe importar los datos.")

                elif sub_op == "2":
                    if datos_cargados:
                        mostrar_detalle_curso(datos_cargados["cursos"], datos_cargados["alumnos"], datos_cargados["servidores"])
                    else:
                        print("Primero debe importar los datos.")
                
                elif sub_op == "3":
                    if datos_cargados:
                        actualizar_curso(datos_cargados["cursos"], datos_cargados["alumnos"])
                    else:
                        print("Primero debe importar los datos.")
                
                elif sub_op == "4":
                    if datos_cargados:
                        listar_cursos_con_servicio_en_servidor(datos_cargados["cursos"])
                    else:
                        print("Primero debe importar los datos.")

                elif sub_op == "0":
                    break  # salimos

                else:
                    print("Opción inválida")


        elif opcion == "4":
            while True:
                print("\n[ALUMNOS]")
                print("1) Listar alumnos")
                print("2) Mostrar detalle de un alumno")
                print("3) Listar alumnos por curso")
                print("0) Volver al menú principal")
                sub_op = input("Seleccione opción: ")

                if sub_op == "1":
                    if datos_cargados:
                        listar_alumnos(datos_cargados["alumnos"])
                    else:
                        print("Primero debe importar los datos.")
                
                elif sub_op == "2":
                    if datos_cargados:
                        mostrar_detalle_alumno(datos_cargados["alumnos"])
                    else:
                        print("Primero debe importar los datos.")

                elif sub_op == "3":
                    if datos_cargados:
                        codigo_curso = input("Ingrese el código del curso: ").strip()
                        curso = next((c for c in datos_cargados["cursos"] if c.codigo == codigo_curso), None)
                        if not curso:
                            print("Curso no encontrado, vuelva a intentarlo")
                        else:
                            print(f"\n→ Alumnos en el curso {curso.nombre} ({curso.codigo}):")
                            for cod in curso.alumnos:
                                alumno = next((a for a in datos_cargados["alumnos"] if str(a.codigo) == str(cod)), None)
                                if alumno:
                                    print(f"- {alumno.nombre} ({alumno.codigo})")
                    else:
                        print("Primero debe importar los datos.")


                elif sub_op == "0":
                    break  # salimos

                else:
                    print("Opción inválida")

        elif opcion == "5":
            while True:
                print("\n[SERVIDORES]")
                print("1) Listar servidores")
                print("2) Mostrar detalle de un servidor")
                print("0) Volver al menú principal")
                sub_op = input("Seleccione opción: ")

                if sub_op == "1":
                    if datos_cargados:
                        listar_servidores(datos_cargados["servidores"])
                    else:
                        print("Primero debe importar los datos.")

                elif sub_op == "2":
                    if datos_cargados:
                        mostrar_detalle_servidor(datos_cargados["servidores"])
                    else:
                        print("Primero debe importar los datos.")

                elif sub_op == "0":
                    break  # salimos

                else:
                    print("Opción inválida")



        elif opcion == "6":
            print("\n[POLÍTICAS]")
            

        elif opcion == "7":
            while True:
                print("\n[CONEXIONES]")
                print("1) Crear conexión")
                print("2) Listar conexiones")
                print("3) Borrar conexión")
                print("0) Volver al menú principal")
                sub_op = input("Seleccione opción: ")

                if sub_op == "1":
                    if datos_cargados:
                        alumno_mac = input("Ingrese la MAC del alumno: ").strip()
                        servicio_nombre = input("Ingrese el nombre del servicio (ej: ssh, web): ").strip()
                        servidor_nombre = input("Ingrese el nombre del servidor (ej: Servidor 1): ").strip()
                        crear_conexion(alumno_mac, servicio_nombre, servidor_nombre, 
                                    datos_cargados["alumnos"], datos_cargados["cursos"], datos_cargados["servidores"])
                    else:
                        print("Primero debe importar los datos.")
                
                elif sub_op == "2":
                    listar_conexiones()
                
                elif sub_op == "3":
                    print("\nBorrar ruta entre alumno y servidor")
                    alumno_mac = input("Ingrese la MAC del alumno: ").strip()
                    servidor_ip = input("Ingrese la IP del servidor: ").strip()
                    eliminar_conexion(alumno_mac, servidor_ip)

                elif sub_op == "0":
                    break 

                else:
                    print("Opción inválida")


        elif opcion == "0":
            print("Saliendo del sistema")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    menu()
