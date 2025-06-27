from alumno import Alumno
from cola_guardado import ColaGuardado
from mongo_repositorio import MongoRepositorio

class InterfazAlumno:
    def __init__(self, contenedor_alumnos=None):
        if contenedor_alumnos is None:
            self.alumnos = Alumno()
            try:
                self.alumnos.leerJson("alumnos.json")
            except FileNotFoundError:
                pass
        else:
            self.alumnos = contenedor_alumnos
        
        self.cola_guardado = ColaGuardado("alumnos")
        self.cola_guardado._reiniciar_timer() 

    def seleccionarAlumnoNoEnGrupo(self, grupo):
        ids_en_grupo = {str(alumno.id) for alumno in grupo.alumnos.items}
        alumnos_disponibles = [a for a in self.alumnos.items if str(a.id) not in ids_en_grupo]

        if not alumnos_disponibles:
            print("Todos los alumnos ya están en este grupo. No hay alumnos disponibles para agregar.")
            return None

        print("\nSeleccione un alumno para agregar (por número):")
        for idx, alumno in enumerate(alumnos_disponibles, start=1):
            print(f"{idx}) {alumno.nombre} {alumno.apellido} (ID: {alumno.id})")

        while True:
            seleccion = input("Ingrese el número del alumno: ").strip()
            if not seleccion.isdigit():
                print("Por favor, ingrese un número válido.")
                continue
            seleccion = int(seleccion)
            if 1 <= seleccion <= len(alumnos_disponibles):
                return alumnos_disponibles[seleccion - 1]
            else:
                print("Número fuera de rango. Intente nuevamente.")

    def obtener_id(self):
        if not self.alumnos.items:
            return 1
        return max(alumno.id for alumno in self.alumnos.items) + 1

    def crearAlumno(self):
        nombre = input("Ingrese el nombre del alumno: ")
        apellido = input("Ingrese el apellido del alumno: ")
        edad = input("Ingrese la edad del alumno: ")

        while True:
            matricula = input("Ingrese la matrícula del alumno: ").strip()
            if not matricula:
                print("La matrícula no puede estar vacía.")
                continue
            matricula_duplicada = any(alumno.matricula == matricula for alumno in self.alumnos.items)
            if matricula_duplicada:
                print("Error: La matrícula ya está registrada. Ingrese una matrícula diferente.")
            else:
                break

        while True:
            promedio = input("Ingrese el promedio del alumno: ").strip()
            try:
                promedio_float = float(promedio)
                if promedio_float < 0 or promedio_float > 10:
                    print("Error: El promedio debe estar entre 0 y 10.")
                    continue
                break
            except ValueError:
                print("Error: El promedio debe ser un número válido.")

        nuevo_id = self.obtener_id()
        alumno = Alumno(nombre, apellido, edad, matricula, promedio, id=nuevo_id)
        self.alumnos.agregar(alumno)
        self.guardar()
        print(f"Alumno creado correctamente con ID: {nuevo_id}")

    def mostrarAlumnos(self):
        if not self.alumnos.items:
            print("No hay alumnos registrados")
            return

        print("\n=== LISTA DE ALUMNOS ===")
        for alumno in self.alumnos.items:
            print(f"\nID: {alumno.id}")
            print(f"Nombre: {alumno.nombre} {alumno.apellido}")
            print(f"Edad: {alumno.edad}")
            print(f"Matrícula: {alumno.matricula}")
            print(f"Promedio: {alumno.promedio}")
            print("-" * 50)

    def actualizarAlumno(self):
        self.mostrarAlumnos()
        id_str = input("\nIngrese el ID del alumno a actualizar: ")

        alumno_encontrado = None
        for alumno in self.alumnos.items:
            if str(alumno.id) == id_str:
                alumno_encontrado = alumno
                break

        if alumno_encontrado is None:
            print("Alumno no encontrado")
            return

        print("\nIngrese los nuevos datos (deje en blanco para mantener el valor actual):")
        alumno_encontrado.nombre = input(f"Nuevo nombre [{alumno_encontrado.nombre}]: ") or alumno_encontrado.nombre
        alumno_encontrado.apellido = input(f"Nuevo apellido [{alumno_encontrado.apellido}]: ") or alumno_encontrado.apellido
        alumno_encontrado.edad = input(f"Nueva edad [{alumno_encontrado.edad}]: ") or alumno_encontrado.edad

        while True:
            nueva_matricula = input(f"Nueva matrícula [{alumno_encontrado.matricula}]: ").strip()
            if not nueva_matricula:
                nueva_matricula = alumno_encontrado.matricula
                break
            matricula_duplicada = any(alumno.matricula == nueva_matricula and alumno.id != alumno_encontrado.id for alumno in self.alumnos.items)
            if matricula_duplicada:
                print("Error: La matrícula ya está registrada. Ingrese una matrícula diferente.")
            else:
                break

        alumno_encontrado.matricula = nueva_matricula

        while True:
            promedio = input(f"Nuevo promedio [{alumno_encontrado.promedio}]: ").strip()
            if not promedio:
                break
            try:
                promedio_float = float(promedio)
                if promedio_float < 0 or promedio_float > 10:
                    print("Error: El promedio debe estar entre 0 y 10.")
                else:
                    alumno_encontrado.promedio = promedio
                    break
            except ValueError:
                print("Error: El promedio debe ser un número válido.")

        self.guardar()
        print("Alumno actualizado correctamente.")

    def eliminarAlumno(self):
        self.mostrarAlumnos()
        id_alumno = input("Ingrese el ID del alumno a eliminar: ").strip()
        if self.alumnos.eliminar(id_alumno):
            self.guardar()
            print("Alumno eliminado correctamente.")
        else:
            print("No se pudo eliminar el alumno.")

    def guardar(self):
        self.alumnos.crearJson("alumnos.json")
        
        # Intentar guardar directo en MongoDB, sino agregar a cola de alumnos
        if self.cola_guardado.intentar_conexion():
            try:
                repo = MongoRepositorio()
                datos = [a.convADiccionario() for a in self.alumnos.items]
                repo.guardar_todos("alumnos", datos)
                print(f"Guardado directo en MongoDB: {len(datos)} alumnos")
            except Exception as e:
                print(f"Error al guardar alumnos en MongoDB: {e}")
                datos = [a.convADiccionario() for a in self.alumnos.items]
                self.cola_guardado.agregar_a_cola("alumnos", datos)
                print("Alumnos agregados a cola de guardado específica")
        else:
            datos = [a.convADiccionario() for a in self.alumnos.items]
            self.cola_guardado.agregar_a_cola("alumnos", datos)
            print("Sin conexión MongoDB. Alumnos agregados a cola de guardado específica")

    def menu_interactivo(self):
        while True:
            print("\n=== MENÚ DE ALUMNOS ===")
            print("1. Crear alumno")
            print("2. Mostrar alumnos")
            print("3. Actualizar alumno")
            print("4. Eliminar alumno")
            print("5. Salir")



            opcion = input("Ingrese una opción: ").strip()

            if opcion == "1":
                self.crearAlumno()
            elif opcion == "2":
                self.mostrarAlumnos()
            elif opcion == "3":
                self.actualizarAlumno()
            elif opcion == "4":
                self.eliminarAlumno()
            elif opcion == "5":
                print("Saliendo...")
                break
            else:
                print("Opción no válida")

if __name__ == "__main__":
    interfaz = InterfazAlumno()
    interfaz.menu_interactivo()