import json
from grupo import Grupo
from maestro import Maestro
from alumno import Alumno
from interfazalumno import InterfazAlumno
from cola_guardado import ColaGuardado
from mongo_repositorio import MongoRepositorio

class InterfazGrupo:
    def __init__(self, contenedor_grupos=None):
        if contenedor_grupos is None:
            self.grupos = Grupo()
            try:
                # Primero intenta cargar desde JSON local
                self.grupos.leerJson("grupos.json")
            except FileNotFoundError:
                # Si no hay archivo, intenta cargar desde MongoDB
                try:
                    self.grupos.leer_desde_mongodb()
                    self.guardar_datos()  # guarda local para tener respaldo
                except Exception as e:
                    print(f"No se pudo cargar grupos desde MongoDB: {e}")
        else:
            self.grupos = contenedor_grupos

        self.maestros = Maestro()
        try:
            self.maestros.leerJson("maestros.json")
        except FileNotFoundError:
            pass

        self.alumnos = Alumno()
        try:
            self.alumnos.leerJson("alumnos.json")
        except FileNotFoundError:
            pass

        # Inicializar sistema de cola específico para grupos
        self.cola_guardado = ColaGuardado("grupos")
        self.cola_guardado._reiniciar_timer()  # Iniciar procesamiento automático

    def obtener_id(self):
        if not self.grupos.items:
            return 1
        return max(int(grupo.id) for grupo in self.grupos.items) + 1

    def crearGrupo(self):
        nombre = input("Ingrese el nombre del grupo: ")

        if not self.maestros.items:
            print("No hay maestros disponibles. Agregue uno primero.")
            return

        print("\nSeleccione un maestro por ID:")
        for maestro in self.maestros.items:
            print(f"ID: {maestro.id} | Nombre: {maestro.nombre} {maestro.apellido}")

        id_maestro = input("Ingrese el ID del maestro: ").strip()
        maestro_seleccionado = next((m for m in self.maestros.items if str(m.id) == id_maestro), None)

        if not maestro_seleccionado:
            print("Maestro no encontrado.")
            return

        nuevo_id = str(self.obtener_id())
        grupo = Grupo(nombre, maestro_seleccionado, id=nuevo_id)
        self.grupos.agregar(grupo)
        self.guardar_datos()
        print(f"Grupo creado exitosamente con ID {nuevo_id}.")

    def mostrarGrupos(self):
        if not self.grupos.items:
            print("No hay grupos registrados.")
            return

        print("\n=== LISTA DE GRUPOS ===")
        for grupo in self.grupos.items:
            print(f"\nGrupo ID: {grupo.id}")
            print(f"Nombre: {grupo.nombre}")
            if grupo.maestro:
                print(f"Maestro: {grupo.maestro.nombre} {grupo.maestro.apellido}")
            else:
                print("Maestro: No asignado")
            print("Alumnos:")
            for alumno in grupo.alumnos.items:
                print(f" - {alumno.nombre} {alumno.apellido} (ID: {alumno.id})")
            print("-" * 50)

    def agregarAlumnoAGrupo(self):
        if not self.alumnos.items:
            print("No hay alumnos disponibles.")
            return

        self.mostrarGrupos()
        id_grupo = input("Ingrese el ID del grupo al que desea agregar un alumno: ").strip()
        grupo = next((g for g in self.grupos.items if g.id == id_grupo), None)

        if not grupo:
            print("Grupo no válido.")
            return

        interfaz_alumno = InterfazAlumno(self.alumnos)
        alumno_seleccionado = interfaz_alumno.seleccionarAlumnoNoEnGrupo(grupo)

        if not alumno_seleccionado:
            print("Alumno no válido o ya está en el grupo.")
            return

        grupo.alumnos.agregar(alumno_seleccionado)
        self.guardar_datos()
        print("Alumno agregado al grupo correctamente.")

    def eliminarGrupo(self):
        self.mostrarGrupos()
        id_grupo = input("Ingrese el ID del grupo a eliminar: ").strip()
        if self.grupos.eliminar(id_grupo):
            self.guardar_datos()
            print("Grupo eliminado correctamente.")
        else:
            print("No se pudo eliminar el grupo.")

    def guardar_datos(self):
        """Guarda localmente y sincroniza con MongoDB usando cola de guardado específica para grupos."""
        self.grupos.crearJson("grupos.json")

        if self.cola_guardado.intentar_conexion():
            try:
                self.grupos.guardar_en_mongodb()
                print(f"Guardado directo en MongoDB: {len(self.grupos.items)} grupos")
            except Exception as e:
                print(f"Error al guardar grupos en MongoDB: {e}")
                datos = [grupo.convADiccionario() for grupo in self.grupos.items]
                self.cola_guardado.agregar_a_cola("grupos", datos)
                print("Grupos agregados a cola de guardado específica")
        else:
            datos = [grupo.convADiccionario() for grupo in self.grupos.items]
            self.cola_guardado.agregar_a_cola("grupos", datos)
            print("Sin conexión MongoDB. Grupos agregados a cola de guardado específica")

    def mostrar_estado_cola(self):
        """Muestra el estado actual de la cola de grupos"""
        print("\n" + self.cola_guardado.obtener_info_cola())

    def menu_interactivo(self):
        while True:
            print("\n=== MENÚ DE GRUPOS ===")
            print("1. Crear grupo")
            print("2. Mostrar grupos")
            print("3. Agregar alumno a grupo")
            print("4. Eliminar grupo")
            print("5. Salir")

            opcion = input("Ingrese una opción: ")

            if opcion == "1":
                self.crearGrupo()
            elif opcion == "2":
                self.mostrarGrupos()
            elif opcion == "3":
                self.agregarAlumnoAGrupo()
            elif opcion == "4":
                self.eliminarGrupo()
            elif opcion == "5":
                break
            else:
                print("Opción no válida")

if __name__ == "__main__":
    interfaz = InterfazGrupo()
    interfaz.menu_interactivo()