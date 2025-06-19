from maestro import Maestro
from mongo_repositorio import MongoRepositorio
from cola_guardado import ColaGuardado

class InterfazMaestro:
    def __init__(self, contenedor_maestros=None):
        if contenedor_maestros is None:
            self.maestros = Maestro()
            try:
                self.maestros.leerJson("maestros.json")
            except FileNotFoundError:
                pass
        else:
            self.maestros = contenedor_maestros

        self.cola_guardado = ColaGuardado()

    def obtener_id(self):
        if not self.maestros.items:
            return 1
        return max(int(maestro.id) for maestro in self.maestros.items) + 1


    def crearMaestro(self):
        nombre = input("Ingrese el nombre del maestro: ")
        apellido = input("Ingrese el apellido del maestro: ")

        while True:
            edad = input("Ingrese la edad del maestro: ").strip()
            if edad.isdigit():
                break
            print("Edad inválida. Debe ser un número.")

        especialidad = input("Ingrese la especialidad del maestro: ").strip()
        while not especialidad:
            print("La especialidad no puede estar vacía.")
            especialidad = input("Ingrese la especialidad del maestro: ").strip()

        nuevo_id = self.obtener_id()
        maestro = Maestro(nombre, apellido, edad, especialidad, id=nuevo_id)
        self.maestros.agregar(maestro)
        self.guardar()
        print(f"Maestro creado correctamente con ID: {nuevo_id}")

    def mostrarMaestros(self):
        if not self.maestros.items:
            print("No hay maestros registrados")
            return

        print("\n=== LISTA DE MAESTROS ===")
        for maestro in self.maestros.items:
            print(f"\nID: {maestro.id}")
            print(f"Nombre: {maestro.nombre} {maestro.apellido}")
            print(f"Edad: {maestro.edad}")
            print(f"Especialidad: {maestro.especialidad}")
            print("-" * 50)

    def actualizarMaestro(self):
        self.mostrarMaestros()
        id_str = input("\nIngrese el ID del maestro a actualizar: ").strip()

        maestro_encontrado = next((m for m in self.maestros.items if str(m.id) == id_str), None)
        if not maestro_encontrado:
            print("Maestro no encontrado")
            return

        print("\nIngrese los nuevos datos (deje en blanco para mantener el valor actual):")
        maestro_encontrado.nombre = input(f"Nuevo nombre [{maestro_encontrado.nombre}]: ") or maestro_encontrado.nombre
        maestro_encontrado.apellido = input(f"Nuevo apellido [{maestro_encontrado.apellido}]: ") or maestro_encontrado.apellido

        nueva_edad = input(f"Nueva edad [{maestro_encontrado.edad}]: ").strip()
        if nueva_edad.isdigit():
            maestro_encontrado.edad = nueva_edad

        nueva_especialidad = input(f"Nueva especialidad [{maestro_encontrado.especialidad}]: ").strip()
        if nueva_especialidad:
            maestro_encontrado.especialidad = nueva_especialidad

        self.guardar()
        print("Maestro actualizado correctamente.")

    def eliminarMaestro(self):
        self.mostrarMaestros()
        id_maestro = input("Ingrese el ID del maestro a eliminar: ").strip()
        if self.maestros.eliminar(id_maestro):
            self.guardar()
            print("Maestro eliminado correctamente.")
        else:
            print("No se pudo eliminar el maestro.")

    def guardar(self):
        """Método principal de guardado con sistema de cola"""
        # Guardar localmente en JSON
        self.maestros.crearJson("maestros.json")
        datos = self.maestros.lista_diccionarios()

        if self.cola_guardado.intentar_conexion():
            try:
                repo = MongoRepositorio()
                repo.guardar_todos("maestros", datos)
                print(f"Guardado directo en MongoDB: {len(datos)} maestros")
            except Exception as e:
                print(f"Error al guardar en MongoDB: {e}")
                self.cola_guardado.agregar_a_cola("maestros", datos)
                print("Agregado a cola de guardado")
        else:
            self.cola_guardado.agregar_a_cola("maestros", datos)
            print("Sin conexión MongoDB. Agregado a cola de guardado")

    def menu_interactivo(self):
        while True:
            print("\n=== MENÚ DE MAESTROS ===")
            print("1. Crear maestro")
            print("2. Mostrar maestros")
            print("3. Actualizar maestro")
            print("4. Eliminar maestro")
            print("5. Salir")

            if self.cola_guardado.tiene_elementos_pendientes():
                print("⚠️  Hay elementos pendientes de sincronizar con MongoDB")

            opcion = input("Ingrese una opción: ").strip()

            if opcion == "1":
                self.crearMaestro()
            elif opcion == "2":
                self.mostrarMaestros()
            elif opcion == "3":
                self.actualizarMaestro()
            elif opcion == "4":
                self.eliminarMaestro()
            elif opcion == "5":
                break
            else:
                print("Opción no válida")


if __name__ == "__main__":
    interfaz = InterfazMaestro()
    interfaz.menu_interactivo()
