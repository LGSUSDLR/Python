from interfazalumno import InterfazAlumno
from interfazmaestro import InterfazMaestro
from interfazgrupo import InterfazGrupo

class InterfazGeneral:
    def __init__(self):
        self.interfaz_alumno = InterfazAlumno()
        self.interfaz_maestro = InterfazMaestro()
        self.interfaz_grupo = InterfazGrupo()

    def mostrar_alertas_de_colas(self):
        print()
        if self.interfaz_alumno.cola_guardado.tiene_elementos_pendientes():
            print("⚠️  Hay alumnos pendientes de sincronizar con MongoDB")
        if self.interfaz_maestro.cola_guardado.tiene_elementos_pendientes():
            print("⚠️  Hay maestros pendientes de sincronizar con MongoDB")
        if self.interfaz_grupo.cola_guardado.tiene_elementos_pendientes():
            print("⚠️  Hay grupos pendientes de sincronizar con MongoDB")

    def menu_principal(self):
        while True:
            print("\n=== MENÚ PRINCIPAL ===")
            self.mostrar_alertas_de_colas()
            print("1. Gestión de Alumnos")
            print("2. Gestión de Maestros")
            print("3. Gestión de Grupos")
            print("4. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                self.interfaz_alumno.menu_interactivo()
            elif opcion == "2":
                self.interfaz_maestro.menu_interactivo()
            elif opcion == "3":
                self.interfaz_grupo.menu_interactivo()
            elif opcion == "4":
                print("Saliendo del programa...")
                break
            else:
                print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    interfaz = InterfazGeneral()
    interfaz.menu_principal()
