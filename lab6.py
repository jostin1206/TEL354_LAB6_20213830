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

# ==== FUNCIÓN PARA IMPORTAR DATOS DESDE YAML ====
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

    # Buscar curso por código
    for curso in cursos:
        if curso.codigo == codigo:
            print(f"\n→ Curso: {curso.nombre} ({curso.codigo})")
            print(f"→ Estado: {curso.estado}")

            # Mostrar alumnos del curso
            print("\n→ Alumnos:")
            for cod in curso.alumnos:
                for alumno in alumnos:
                    if str(alumno.codigo) == str(cod):
                        print(f"  - {alumno.nombre} ({alumno.codigo})")

            # Mostrar servidores del curso

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
    
    # Busca el curso
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

        # Verifica si ya está matriculado
        if cod_alumno in [str(c) for c in curso_encontrado.alumnos]:
            print("→ El alumno ya está matriculado.")
            return

        # Verifica si el alumno existe
        existe = any(str(a.codigo) == cod_alumno for a in alumnos)
        if not existe:
            print("→ El alumno no existe.")
            return

        # Agrega el alumno
        curso_encontrado.alumnos.append(cod_alumno)
        print("→ Alumno agregado correctamente.")

    elif opcion == "2":
        cod_alumno = input("Ingrese código del alumno a quitar: ").strip()

        # Verifica si está en el curso
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
        print("-" * 30)

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

    print("El alumno no está autorizado para acceder a ese servicio.")
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

def listar_servidores(servidores):
    if not servidores:
        print("No hay servidores registrados.")
        return

    print("\nListado de Servidores:")
    for servidor in servidores:
        print(f"- Nombre: {servidor.nombre}")
        print(f"  IP:     {servidor.ip}")
        print("  Servicios:")
        for servicio in servidor.servicios:
            # Mostramos nombre, protocolo y puerto de cada servicio
            print(f"    - {servicio.nombre} ({servicio.protocolo}, puerto {servicio.puerto})")
        print("-" * 30)

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



def mostrar_menu_principal():
    print("\n--- Menú Principal ---")
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
    archivo = input("Ingrese nombre de archivo YAML (ej: database.yaml): ")
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
            print("\n[IMPORTAR] (cargar archivo datos.yaml)...")
            importar()

        elif opcion == "2":
            print("\n[EXPORTAR] (guardar datos yaml)...")
            archivo = input("Ingrese nombre de archivo YAML para exportar: ")
            exportar_datos(archivo)
            print("Archivo exportado correctamente.")

        elif opcion == "3":
            print("\n[CURSOS]")
            print("1) Listar cursos")
            print("2) Mostrar detalle de un curso")
            print("3) Actualizar (agregar/quitar alumno)")
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


        elif opcion == "4":
            print("\n[ALUMNOS]")
            print("1) Listar alumnos")
            print("2) Mostrar detalle de un alumno")
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

        elif opcion == "5":
            print("\n[SERVIDORES]")
            print("1) Listar servidores")
            print("2) Mostrar detalle de un servidor")
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


        elif opcion == "6":
            print("\n[POLÍTICAS] Mostrar/gestionar políticas...")
            # aquí se implementará la lógica de políticas

        elif opcion == "7":
            print("\n[CONECTAR] Verificar y construir ruta...")
            # aquí se usará la lógica para instalar rutas con Floodlight
        elif opcion == "0":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    menu()
